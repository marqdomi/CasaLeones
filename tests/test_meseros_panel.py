"""Auditoría del panel de meseros.

Fija los dos hallazgos de la auditoría, ambos de control de acceso:

1. `POST /api/ordenes/<id>/detalle/<did>/listo` — duplicaba el marcado del KDS
   sin ninguno de sus guards y sin comprobar que el detalle perteneciera a la
   orden. Ningún frontend la usaba; se eliminó.
2. `POST /api/ordenes` aceptaba cualquier sesión: un usuario de cocina podía
   levantar órdenes y quedaba acreditado como su mesero.

El resto (IDOR entre meseros, borradores, mesas compartidas, cobro dividido)
ya funcionaba; se cubre aquí para que no se rompa.
"""
import pytest

from tests.conftest import login


def _onboarding_listo(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


def _entrar(client, db, email, password='Test1234!'):
    _onboarding_listo(db)
    return login(client, email, password)


@pytest.fixture
def otro_mesero(db):
    from backend.models.models import Usuario
    u = Usuario(nombre='Beto', email='beto_test@test.com', rol='mesero')
    u.set_password('Test1234!')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def cocinero(db):
    from backend.models.models import Usuario, Estacion
    est = Estacion(nombre='Parrilla')
    db.session.add(est)
    db.session.flush()
    u = Usuario(nombre='Coci', email='coci_test@test.com', rol='cocina', estacion_id=est.id)
    u.set_password('Test1234!')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def orden_de_otro(db, otro_mesero, sample_mesa, sample_producto):
    """Orden que pertenece a Beto, para probar accesos de Ana."""
    from backend.models.models import Orden, OrdenDetalle, OrdenEstado
    o = Orden(mesa_id=sample_mesa.id, mesero_id=otro_mesero.id, estado=OrdenEstado.ENVIADO)
    db.session.add(o)
    db.session.flush()
    d = OrdenDetalle(orden_id=o.id, producto_id=sample_producto.id, cantidad=2,
                     precio_unitario=sample_producto.precio, estado=OrdenEstado.PENDIENTE)
    db.session.add(d)
    db.session.commit()
    return o


class TestApiListoEliminada:
    """La ruta se quitó por completo; el flujo vivo es el del KDS."""

    def test_la_ruta_ya_no_existe(self, app):
        rutas = {str(r) for r in app.url_map.iter_rules()}
        assert '/api/ordenes/<int:orden_id>/detalle/<int:detalle_id>/listo' not in rutas

    def test_no_responde_a_nadie(self, client, mesero_user, db, orden_de_otro):
        """Antes: un mesero ajeno la llamaba y marcaba listo el item de otro."""
        from backend.models.models import OrdenDetalle, OrdenEstado

        detalle = OrdenDetalle.query.filter_by(orden_id=orden_de_otro.id).first()
        _entrar(client, db, 'mesero_test@test.com')

        resp = client.post(f'/api/ordenes/{orden_de_otro.id}/detalle/{detalle.id}/listo')
        assert resp.status_code in (404, 405)

        db.session.refresh(detalle)
        assert detalle.estado != OrdenEstado.LISTO

    def test_el_kds_sigue_siendo_el_camino_vivo(self, client, superadmin_user, db,
                                                orden_de_otro, cocinero, sample_producto):
        """Control positivo: si el KDS tampoco marcara, el test de arriba pasaría
        por la razón equivocada."""
        from backend.models.models import OrdenDetalle, OrdenEstado

        sample_producto.estacion_id = cocinero.estacion_id
        db.session.commit()
        detalle = OrdenDetalle.query.filter_by(orden_id=orden_de_otro.id).first()

        _entrar(client, db, 'super_test@test.com')
        resp = client.post(f'/cocina/parrilla/marcar/{orden_de_otro.id}/{detalle.id}')
        assert resp.status_code == 200

        db.session.refresh(detalle)
        assert detalle.estado == OrdenEstado.LISTO

    def test_el_kds_rechaza_detalle_de_otra_orden(self, client, superadmin_user, db,
                                                  orden_de_otro, cocinero, sample_producto,
                                                  mesero_user, sample_mesa):
        """La ruta borrada ni siquiera comprobaba esto."""
        from backend.models.models import Orden, OrdenDetalle, OrdenEstado

        sample_producto.estacion_id = cocinero.estacion_id
        otra = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                     estado=OrdenEstado.ENVIADO)
        db.session.add(otra)
        db.session.commit()

        detalle_ajeno = OrdenDetalle.query.filter_by(orden_id=orden_de_otro.id).first()

        _entrar(client, db, 'super_test@test.com')
        resp = client.post(f'/cocina/parrilla/marcar/{otra.id}/{detalle_ajeno.id}')
        assert resp.status_code >= 400


class TestQuienPuedeLevantarOrdenes:
    def test_cocina_no_puede_crear_ordenes(self, client, cocinero, db, sample_mesa):
        """Una orden creada por cocina queda con ese usuario como `mesero_id` y
        se le acredita en el reporte de meseros."""
        from backend.models.models import Orden

        _entrar(client, db, 'coci_test@test.com')
        resp = client.post('/api/ordenes', json={'mesa_id': sample_mesa.id})
        assert resp.status_code in (302, 403)
        assert Orden.query.count() == 0

    def test_mesero_si_puede_crear_ordenes(self, client, mesero_user, db, sample_mesa):
        """Control positivo del anterior."""
        _entrar(client, db, 'mesero_test@test.com')
        resp = client.post('/api/ordenes', json={'mesa_id': sample_mesa.id})
        assert resp.status_code == 201

    def test_admin_si_puede_crear_ordenes(self, client, superadmin_user, db, sample_mesa):
        _entrar(client, db, 'super_test@test.com')
        resp = client.post('/api/ordenes', json={'mesa_id': sample_mesa.id})
        assert resp.status_code == 201


class TestIdorEntreMeseros:
    """Ana no debe poder tocar las órdenes de Beto por ningún camino."""

    RUTAS_GET = ['/meseros/ordenes/{oid}/detalle_orden',
                 '/meseros/ordenes/{oid}/cobrar_info',
                 '/api/ordenes/{oid}/detalle']
    RUTAS_POST = ['/meseros/ordenes/{oid}/enviar_a_cocina',
                  '/meseros/ordenes/{oid}/cancelar',
                  '/meseros/ordenes/{oid}/descuento',
                  '/meseros/ordenes/{oid}/pago',
                  '/api/ordenes/{oid}/detalle']

    @pytest.mark.parametrize('plantilla', RUTAS_GET)
    def test_get_ajeno_bloqueado(self, client, mesero_user, db, orden_de_otro, plantilla):
        _entrar(client, db, 'mesero_test@test.com')
        resp = client.get(plantilla.format(oid=orden_de_otro.id))
        assert resp.status_code in (302, 403, 404)

    @pytest.mark.parametrize('plantilla', RUTAS_POST)
    def test_post_ajeno_bloqueado(self, client, mesero_user, db, orden_de_otro, plantilla):
        _entrar(client, db, 'mesero_test@test.com')
        resp = client.post(plantilla.format(oid=orden_de_otro.id), json={})
        assert resp.status_code in (302, 403, 404)

    def test_la_orden_ajena_queda_intacta(self, client, mesero_user, db, orden_de_otro):
        from backend.models.models import Orden, OrdenEstado

        _entrar(client, db, 'mesero_test@test.com')
        client.post(f'/meseros/ordenes/{orden_de_otro.id}/cancelar', json={'motivo': 'x'})
        client.post(f'/api/ordenes/{orden_de_otro.id}/detalle',
                    json={'producto_id': 1, 'cantidad': 5})

        db.session.refresh(orden_de_otro)
        assert orden_de_otro.estado == OrdenEstado.ENVIADO
        assert len(orden_de_otro.detalles) == 1

    def test_el_admin_si_entra(self, client, superadmin_user, db, orden_de_otro):
        """Bypass legítimo: el admin supervisa todas las cuentas."""
        _entrar(client, db, 'super_test@test.com')
        resp = client.get(f'/meseros/ordenes/{orden_de_otro.id}/detalle_orden')
        assert resp.status_code == 200


class TestPantallasDelMesero:
    @pytest.mark.parametrize('ruta', ['/meseros/', '/meseros/mapa', '/meseros/historial',
                                      '/meseros/historial/csv', '/meseros/seleccionar_mesa'])
    def test_responden(self, client, mesero_user, db, ruta):
        _entrar(client, db, 'mesero_test@test.com')
        assert client.get(ruta).status_code == 200

    def test_crear_para_llevar_es_post_only(self, client, mesero_user, db):
        """Era un GET sin CSRF: bastaba con que el navegador precargara la liga."""
        _entrar(client, db, 'mesero_test@test.com')
        assert client.get('/meseros/crear_orden_para_llevar').status_code == 405
