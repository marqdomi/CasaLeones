"""Auditoría del KDS de cocina.

El hallazgo: `batch-listo` movía la orden de "enviado" a "en preparación" antes
de comprobar si algún item calificaba, así que un batch que no marcaba nada
(ids de otra estación, o ya listos) igual sacaba la orden de la cola y le
avisaba al mesero por Socket.IO que ya la estaban preparando.

El resto (aislamiento entre estaciones, ventana de undo, 409 en órdenes
cerradas) ya funcionaba; queda cubierto para que no se rompa.
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
def estaciones(db):
    from backend.models.models import Estacion
    parrilla = Estacion(nombre='Parrilla')
    bebidas = Estacion(nombre='Bebidas')
    db.session.add_all([parrilla, bebidas])
    db.session.commit()
    return {'parrilla': parrilla, 'bebidas': bebidas}


@pytest.fixture
def productos(db, sample_categoria, estaciones):
    from backend.models.models import Producto
    taco = Producto(nombre='Taco', precio=25, categoria_id=sample_categoria.id,
                    estacion_id=estaciones['parrilla'].id)
    agua = Producto(nombre='Agua', precio=20, categoria_id=sample_categoria.id,
                    estacion_id=estaciones['bebidas'].id)
    db.session.add_all([taco, agua])
    db.session.commit()
    return {'taco': taco, 'agua': agua}


@pytest.fixture
def cocinero_parrilla(db, estaciones):
    from backend.models.models import Usuario
    u = Usuario(nombre='CociP', email='cocip@test.com', rol='cocina',
                estacion_id=estaciones['parrilla'].id)
    u.set_password('Test1234!')
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def orden_mixta(db, mesero_user, sample_mesa, productos):
    """Orden enviada a cocina con un item de Parrilla y otro de Bebidas."""
    from backend.models.models import Orden, OrdenDetalle, OrdenEstado
    o = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id, estado=OrdenEstado.ENVIADO)
    db.session.add(o)
    db.session.flush()
    d_taco = OrdenDetalle(orden_id=o.id, producto_id=productos['taco'].id, cantidad=1,
                          precio_unitario=25, estado=OrdenEstado.PENDIENTE)
    d_agua = OrdenDetalle(orden_id=o.id, producto_id=productos['agua'].id, cantidad=1,
                          precio_unitario=20, estado=OrdenEstado.PENDIENTE)
    db.session.add_all([d_taco, d_agua])
    db.session.commit()
    return {'orden': o, 'taco': d_taco, 'agua': d_agua}


class TestBatchListo:
    def test_batch_sin_items_validos_no_mueve_la_orden(self, client, superadmin_user, db,
                                                       orden_mixta):
        """El bug: la orden salía de "enviado" aunque no se marcara nada."""
        from backend.models.models import OrdenEstado

        orden = orden_mixta['orden']
        agua = orden_mixta['agua']          # es de Bebidas, no de Parrilla

        _entrar(client, db, 'super_test@test.com')
        resp = client.post('/cocina/parrilla/batch-listo',
                           json={'orden_id': orden.id, 'detalle_ids': [agua.id]})
        assert resp.status_code == 200

        db.session.refresh(orden)
        db.session.refresh(agua)
        assert agua.estado != OrdenEstado.LISTO
        assert orden.estado == OrdenEstado.ENVIADO, \
            'la orden se movió a en_preparacion sin que nadie la empezara'

    def test_batch_valido_si_mueve_la_orden(self, client, superadmin_user, db, orden_mixta):
        """Control positivo: si el batch nunca transicionara, el test de arriba
        pasaría por la razón equivocada."""
        from backend.models.models import OrdenEstado

        orden = orden_mixta['orden']
        taco = orden_mixta['taco']

        _entrar(client, db, 'super_test@test.com')
        resp = client.post('/cocina/parrilla/batch-listo',
                           json={'orden_id': orden.id, 'detalle_ids': [taco.id]})
        assert resp.status_code == 200

        db.session.refresh(orden)
        db.session.refresh(taco)
        assert taco.estado == OrdenEstado.LISTO
        assert orden.estado == OrdenEstado.EN_PREPARACION

    def test_batch_no_toca_ordenes_cerradas(self, client, superadmin_user, db, orden_mixta):
        from backend.models.models import OrdenEstado

        orden = orden_mixta['orden']
        orden.estado = OrdenEstado.CANCELADA
        db.session.commit()

        _entrar(client, db, 'super_test@test.com')
        resp = client.post('/cocina/parrilla/batch-listo',
                           json={'orden_id': orden.id,
                                 'detalle_ids': [orden_mixta['taco'].id]})
        assert resp.status_code == 409

        db.session.refresh(orden_mixta['taco'])
        assert orden_mixta['taco'].estado != OrdenEstado.LISTO

    def test_batch_sin_body_avisa(self, client, superadmin_user, db, estaciones):
        _entrar(client, db, 'super_test@test.com')
        assert client.post('/cocina/parrilla/batch-listo', json={}).status_code == 400


class TestAislamientoEntreEstaciones:
    def test_cocinero_no_abre_el_kds_de_otra_estacion(self, client, cocinero_parrilla, db):
        _entrar(client, db, 'cocip@test.com')
        assert client.get('/cocina/parrilla').status_code == 200
        assert client.get('/cocina/bebidas').status_code == 403

    def test_el_kds_solo_muestra_los_items_de_su_estacion(self, client, superadmin_user,
                                                          db, orden_mixta):
        _entrar(client, db, 'super_test@test.com')
        html = client.get('/cocina/parrilla').data.decode()
        assert 'Taco' in html
        assert 'Agua' not in html

    def test_no_marca_items_de_otra_estacion(self, client, superadmin_user, db, orden_mixta):
        from backend.models.models import OrdenEstado

        _entrar(client, db, 'super_test@test.com')
        resp = client.post(
            f"/cocina/parrilla/marcar/{orden_mixta['orden'].id}/{orden_mixta['agua'].id}")
        assert resp.status_code == 403

        db.session.refresh(orden_mixta['agua'])
        assert orden_mixta['agua'].estado != OrdenEstado.LISTO

    def test_rechaza_detalle_de_otra_orden(self, client, superadmin_user, db, orden_mixta,
                                           mesero_user, sample_mesa):
        from backend.models.models import Orden, OrdenEstado

        otra = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                     estado=OrdenEstado.ENVIADO)
        db.session.add(otra)
        db.session.commit()

        _entrar(client, db, 'super_test@test.com')
        resp = client.post(f"/cocina/parrilla/marcar/{otra.id}/{orden_mixta['taco'].id}")
        assert resp.status_code == 400


class TestCicloDeVida:
    def test_primer_item_pasa_a_en_preparacion(self, client, superadmin_user, db, orden_mixta):
        from backend.models.models import OrdenEstado

        _entrar(client, db, 'super_test@test.com')
        client.post(f"/cocina/parrilla/marcar/{orden_mixta['orden'].id}/{orden_mixta['taco'].id}")

        db.session.refresh(orden_mixta['orden'])
        assert orden_mixta['orden'].estado == OrdenEstado.EN_PREPARACION

    def test_todos_los_items_pasan_a_lista_para_entregar(self, client, superadmin_user,
                                                         db, orden_mixta):
        from backend.models.models import OrdenEstado

        _entrar(client, db, 'super_test@test.com')
        oid = orden_mixta['orden'].id
        client.post(f"/cocina/parrilla/marcar/{oid}/{orden_mixta['taco'].id}")
        client.post(f"/cocina/bebidas/marcar/{oid}/{orden_mixta['agua'].id}")

        db.session.refresh(orden_mixta['orden'])
        assert orden_mixta['orden'].estado == OrdenEstado.LISTA_PARA_ENTREGAR

    def test_no_marca_en_orden_cancelada(self, client, superadmin_user, db, orden_mixta):
        from backend.models.models import OrdenEstado

        orden_mixta['orden'].estado = OrdenEstado.CANCELADA
        db.session.commit()

        _entrar(client, db, 'super_test@test.com')
        resp = client.post(
            f"/cocina/parrilla/marcar/{orden_mixta['orden'].id}/{orden_mixta['taco'].id}")
        assert resp.status_code == 409


class TestDeshacer:
    def _marcar(self, client, orden_mixta):
        return client.post(
            f"/cocina/parrilla/marcar/{orden_mixta['orden'].id}/{orden_mixta['taco'].id}")

    def test_undo_regresa_el_item_y_la_orden(self, client, superadmin_user, db, orden_mixta):
        """Si la orden ya había salido del KDS, debe reaparecer para que el
        mesero no entregue de más."""
        from backend.models.models import OrdenEstado

        _entrar(client, db, 'super_test@test.com')
        oid = orden_mixta['orden'].id
        self._marcar(client, orden_mixta)
        client.post(f"/cocina/bebidas/marcar/{oid}/{orden_mixta['agua'].id}")
        db.session.refresh(orden_mixta['orden'])
        assert orden_mixta['orden'].estado == OrdenEstado.LISTA_PARA_ENTREGAR

        resp = client.post(f"/cocina/parrilla/desmarcar/{oid}/{orden_mixta['taco'].id}")
        assert resp.status_code == 200

        db.session.refresh(orden_mixta['taco'])
        db.session.refresh(orden_mixta['orden'])
        assert orden_mixta['taco'].estado == OrdenEstado.PENDIENTE
        assert orden_mixta['orden'].estado == OrdenEstado.EN_PREPARACION

    def test_undo_fuera_de_la_ventana_se_rechaza(self, client, superadmin_user, db,
                                                 orden_mixta):
        from datetime import timedelta
        from backend.models.models import utc_now
        from backend.routes.cocina import UNDO_LISTO_SEGUNDOS

        _entrar(client, db, 'super_test@test.com')
        self._marcar(client, orden_mixta)

        db.session.refresh(orden_mixta['taco'])
        orden_mixta['taco'].fecha_listo = (utc_now().replace(tzinfo=None)
                                           - timedelta(seconds=UNDO_LISTO_SEGUNDOS + 60))
        db.session.commit()

        resp = client.post(
            f"/cocina/parrilla/desmarcar/{orden_mixta['orden'].id}/{orden_mixta['taco'].id}")
        assert resp.status_code == 409

    def test_undo_de_item_de_otra_estacion_se_rechaza(self, client, superadmin_user, db,
                                                      orden_mixta):
        _entrar(client, db, 'super_test@test.com')
        oid = orden_mixta['orden'].id
        client.post(f"/cocina/bebidas/marcar/{oid}/{orden_mixta['agua'].id}")

        resp = client.post(f"/cocina/parrilla/desmarcar/{oid}/{orden_mixta['agua'].id}")
        assert resp.status_code == 403


class TestPantallasKds:
    @pytest.mark.parametrize('ruta', ['/cocina/api/estaciones', '/cocina/api/orders',
                                      '/cocina/parrilla', '/cocina/parrilla/stats',
                                      '/cocina/parrilla/fragmento_ordenes'])
    def test_responden(self, client, superadmin_user, db, estaciones, ruta):
        _entrar(client, db, 'super_test@test.com')
        assert client.get(ruta).status_code == 200

    def test_estacion_con_acento_y_espacio_resuelve(self, client, superadmin_user, db):
        from backend.models.models import Estacion

        db.session.add(Estacion(nombre='Plancha Fría'))
        db.session.commit()

        _entrar(client, db, 'super_test@test.com')
        assert client.get('/cocina/plancha-fria').status_code == 200

    def test_estacion_inexistente_da_404(self, client, superadmin_user, db, estaciones):
        _entrar(client, db, 'super_test@test.com')
        assert client.get('/cocina/no-existe').status_code == 404

    def test_historial_es_solo_de_admin(self, client, cocinero_parrilla, db):
        _entrar(client, db, 'cocip@test.com')
        assert client.get('/cocina/historial').status_code in (302, 403)

    def test_timestamps_llevan_sufijo_z(self, client, superadmin_user, db, orden_mixta):
        """Sin la Z, `new Date()` los lee como hora local y el cronómetro del KDS
        sale corrido por el offset."""
        _entrar(client, db, 'super_test@test.com')
        datos = client.get('/cocina/api/orders').get_json()
        texto = str(datos)
        assert 'T' in texto and 'Z' in texto
