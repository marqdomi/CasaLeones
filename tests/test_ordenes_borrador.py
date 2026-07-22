"""Órdenes borrador: una cuenta sin productos no debe existir para nadie.

Antes, tocar "Nueva orden" creaba la fila de inmediato: si el mesero se regresaba
quedaba una orden fantasma ocupando la mesa y contando como activa. El carrito se
sigue guardando en el servidor producto por producto (así no se pierde la orden si
el celular se bloquea), pero mientras esté vacía la orden es invisible.
"""
from decimal import Decimal

import pytest

from tests.conftest import login


def _setup_onboarding(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


def _borrador(db, mesero, mesa=None, para_llevar=False):
    from backend.models.models import Orden, OrdenEstado
    o = Orden(mesero_id=mesero.id, mesa_id=mesa.id if mesa else None,
              es_para_llevar=para_llevar, estado=OrdenEstado.PENDIENTE)
    db.session.add(o)
    db.session.commit()
    return o


class TestParaLlevarEsPost:
    def test_get_ya_no_crea_orden(self, client, db, mesero_user):
        """Como enlace GET, una precarga del navegador creaba órdenes solas."""
        from backend.models.models import Orden

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        antes = Orden.query.count()
        resp = client.get('/meseros/crear_orden_para_llevar')

        assert resp.status_code == 405, 'la ruta sigue aceptando GET'
        assert Orden.query.count() == antes

    def test_post_crea_la_orden(self, client, db, mesero_user):
        from backend.models.models import Orden

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        resp = client.post('/meseros/crear_orden_para_llevar')

        assert resp.status_code == 302
        assert Orden.query.count() == 1

    def test_no_amontona_borradores(self, client, db, mesero_user):
        """Entrar y regresar tres veces no debe dejar tres cuentas."""
        from backend.models.models import Orden

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        for _ in range(3):
            client.post('/meseros/crear_orden_para_llevar')

        assert Orden.query.count() == 1, 'se creó una orden por cada intento'


class TestBorradorInvisible:
    def test_no_aparece_en_la_lista(self, client, db, mesero_user, sample_mesa):
        _setup_onboarding(db)
        orden = _borrador(db, mesero_user, sample_mesa)

        login(client, 'mesero_test@test.com', 'Test1234!')
        html = client.get('/meseros/').get_data(as_text=True)
        assert f'orden-card-{orden.id}' not in html, 'la cuenta vacía aparece en la lista'

    def test_no_ocupa_la_mesa(self, db, mesero_user, sample_mesa):
        from backend.models.models import Mesa
        from backend.utils import actualizar_estado_mesa

        _borrador(db, mesero_user, sample_mesa)
        actualizar_estado_mesa(sample_mesa.id)
        db.session.commit()

        assert db.session.get(Mesa, sample_mesa.id).estado == 'disponible', \
            'una cuenta vacía dejó la mesa ocupada'

    def test_con_producto_si_ocupa_la_mesa(self, client, db, mesero_user,
                                           sample_mesa, sample_producto):
        from backend.models.models import Mesa

        _setup_onboarding(db)
        orden = _borrador(db, mesero_user, sample_mesa)
        login(client, 'mesero_test@test.com', 'Test1234!')
        resp = client.post(f'/api/ordenes/{orden.id}/detalle',
                           json={'producto_id': sample_producto.id, 'cantidad': 1})
        assert resp.status_code == 201

        assert db.session.get(Mesa, sample_mesa.id).estado == 'ocupada'
        html = client.get('/meseros/').get_data(as_text=True)
        assert f'orden-card-{orden.id}' in html, 'con productos ya debe verse en la lista'


class TestReutilizacion:
    def test_elegir_la_misma_mesa_reutiliza_el_borrador(self, client, db,
                                                       mesero_user, sample_mesa):
        from backend.models.models import Orden

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        client.post('/meseros/seleccionar_mesa', data={'mesa_id': sample_mesa.id})
        client.post('/meseros/seleccionar_mesa', data={'mesa_id': sample_mesa.id})

        assert Orden.query.filter_by(mesa_id=sample_mesa.id).count() == 1


class TestLimpieza:
    def test_barre_los_borradores_viejos(self, db, mesero_user, sample_mesa):
        from datetime import timedelta
        from backend.models.models import Orden, utc_now
        from backend.utils import limpiar_borradores

        orden = _borrador(db, mesero_user, sample_mesa)
        orden.tiempo_registro = utc_now().replace(tzinfo=None) - timedelta(minutes=30)
        db.session.commit()

        assert limpiar_borradores(mesero_user.id) == 1
        assert db.session.get(Orden, orden.id) is None

    def test_no_toca_los_recien_creados(self, db, mesero_user, sample_mesa):
        """El mesero puede estar capturando en este momento."""
        from backend.models.models import Orden
        from backend.utils import limpiar_borradores

        orden = _borrador(db, mesero_user, sample_mesa)
        assert limpiar_borradores(mesero_user.id) == 0
        assert db.session.get(Orden, orden.id) is not None

    def test_no_toca_ordenes_con_productos(self, db, mesero_user, sample_mesa,
                                           sample_producto):
        from datetime import timedelta
        from backend.models.models import Orden, OrdenDetalle, utc_now
        from backend.utils import limpiar_borradores

        orden = _borrador(db, mesero_user, sample_mesa)
        orden.tiempo_registro = utc_now().replace(tzinfo=None) - timedelta(hours=2)
        db.session.add(OrdenDetalle(orden_id=orden.id, producto_id=sample_producto.id,
                                    cantidad=1, precio_unitario=Decimal('25')))
        db.session.commit()

        assert limpiar_borradores(mesero_user.id) == 0
        assert db.session.get(Orden, orden.id) is not None
