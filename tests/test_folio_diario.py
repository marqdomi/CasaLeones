"""Folio diario por sucursal.

El `id` de Orden es una secuencia global que además salta cuando se descarta un
borrador: al tercer día el cliente escucharía "orden 247". El folio reinicia cada día
contable y sólo lo reciben las órdenes reales.
"""
import json
from datetime import timedelta
from decimal import Decimal

import pytest

from tests.conftest import login


def _setup_onboarding(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


def _orden(db, mesero, mesa=None):
    from backend.models.models import Orden, OrdenEstado
    o = Orden(mesero_id=mesero.id, mesa_id=mesa.id if mesa else None,
              es_para_llevar=mesa is None, estado=OrdenEstado.PENDIENTE)
    db.session.add(o)
    db.session.commit()
    return o


class TestAsignacion:
    def test_empieza_en_uno(self, app, db, mesero_user, sample_mesa):
        from backend.services.folio import asignar_folio

        orden = _orden(db, mesero_user, sample_mesa)
        assert asignar_folio(orden) == 1
        db.session.commit()
        assert orden.folio == 1

    def test_numera_consecutivo(self, app, db, mesero_user, sample_mesa):
        from backend.services.folio import asignar_folio

        folios = []
        for _ in range(3):
            o = _orden(db, mesero_user, sample_mesa)
            folios.append(asignar_folio(o))
            db.session.commit()
        assert folios == [1, 2, 3]

    def test_no_renumera_si_ya_tiene(self, app, db, mesero_user, sample_mesa):
        """Agregar un segundo producto no debe cambiarle el número a la orden."""
        from backend.services.folio import asignar_folio

        orden = _orden(db, mesero_user, sample_mesa)
        primero = asignar_folio(orden)
        db.session.commit()
        assert asignar_folio(orden) == primero

    def test_reinicia_al_dia_siguiente(self, app, db, mesero_user, sample_mesa):
        from backend.models.models import FolioDiario
        from backend.services.folio import asignar_folio
        from backend.services.tiempo import hoy_local

        o1 = _orden(db, mesero_user, sample_mesa)
        asignar_folio(o1)
        db.session.commit()

        # Simula que el contador de hoy es el de ayer: el de hoy arranca de cero
        contador = FolioDiario.query.one()
        contador.fecha = hoy_local() - timedelta(days=1)
        db.session.commit()

        o2 = _orden(db, mesero_user, sample_mesa)
        assert asignar_folio(o2) == 1, 'el folio no reinició al cambiar el día'

    def test_cada_sucursal_lleva_su_cuenta(self, app, db, mesero_user, sample_mesa):
        from backend.models.models import Sucursal
        from backend.services.folio import asignar_folio

        db.session.add_all([Sucursal(nombre='Centro'), Sucursal(nombre='Norte')])
        db.session.commit()
        centro, norte = Sucursal.query.order_by(Sucursal.id).all()[-2:]

        o1 = _orden(db, mesero_user, sample_mesa)
        o1.sucursal_id = centro.id
        o2 = _orden(db, mesero_user, sample_mesa)
        o2.sucursal_id = norte.id
        db.session.commit()

        assert asignar_folio(o1) == 1
        db.session.commit()
        assert asignar_folio(o2) == 1, 'las sucursales comparten la numeración'


class TestFlujoReal:
    def test_el_borrador_no_quema_folio(self, client, db, mesero_user, sample_mesa,
                                        sample_producto):
        """Entrar y regresarse no debe consumir un número del día."""
        from backend.models.models import Orden

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')

        # Tres intentos abandonados (se reutiliza el mismo borrador, sin folio)
        for _ in range(3):
            client.post('/meseros/crear_orden_para_llevar')
        borrador = Orden.query.one()
        assert borrador.folio is None

        # Al primer producto sí recibe el folio, y es el 1 del día
        client.post(f'/api/ordenes/{borrador.id}/detalle',
                    json={'producto_id': sample_producto.id, 'cantidad': 1})
        db.session.refresh(borrador)
        assert borrador.folio == 1

    def test_numero_visible_es_el_folio(self, client, db, mesero_user, sample_mesa,
                                        sample_producto):
        from backend.models.models import Orden

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        client.post('/meseros/seleccionar_mesa', data={'mesa_id': sample_mesa.id})
        orden = Orden.query.one()
        client.post(f'/api/ordenes/{orden.id}/detalle',
                    json={'producto_id': sample_producto.id, 'cantidad': 1})
        db.session.refresh(orden)

        html = client.get('/meseros/').get_data(as_text=True)
        assert f'#{orden.folio}' in html
        assert orden.numero == orden.folio


class TestSinSucursal:
    """La instalación de una sola sucursal deja `Orden.sucursal_id` en NULL.

    Con NULL en el contador, el UNIQUE(sucursal_id, fecha) NO impide duplicados —en
    SQL dos NULL nunca son iguales— y bajo carga se creaban varios contadores: tres
    clientes recibían el folio 1. Por eso el contador guarda 0, no NULL.
    """

    def test_el_contador_nunca_guarda_null(self, app, db, mesero_user):
        from backend.models.models import FolioDiario
        from backend.services.folio import asignar_folio

        orden = _orden(db, mesero_user)
        assert orden.sucursal_id is None
        asignar_folio(orden)
        db.session.commit()

        contador = FolioDiario.query.one()
        assert contador.sucursal_id == 0, \
            'con NULL el UNIQUE no protege y se duplican los contadores'

    def test_comparten_un_solo_contador(self, app, db, mesero_user):
        from backend.models.models import FolioDiario
        from backend.services.folio import asignar_folio

        folios = []
        for _ in range(3):
            o = _orden(db, mesero_user)
            folios.append(asignar_folio(o))
            db.session.commit()

        assert folios == [1, 2, 3]
        assert FolioDiario.query.count() == 1, 'se creó más de un contador para el día'


class TestOrdenesViejas:
    def test_sin_folio_cae_al_id(self, db, mesero_user, sample_mesa):
        """Las órdenes anteriores a esta función no tienen folio y siguen usable."""
        orden = _orden(db, mesero_user, sample_mesa)
        assert orden.folio is None
        assert orden.numero == orden.id
