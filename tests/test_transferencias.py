"""Transferencias: la cuenta no se libera hasta que alguien confirma el depósito.

El negocio no acepta tarjeta pero sí transferencias, y una de las dueñas revisa en su
app del banco que el dinero haya llegado antes de dar la cuenta por pagada. El efectivo
no necesita eso: ya está en la mano.
"""
from decimal import Decimal

import pytest

from tests.conftest import login


def _setup_onboarding(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


@pytest.fixture
def orden_por_cobrar(db, sample_producto, sample_mesa, mesero_user):
    """Una orden lista para cobrar, de $100."""
    from backend.models.models import Orden, OrdenDetalle, OrdenEstado

    orden = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                  estado=OrdenEstado.COMPLETADA)
    db.session.add(orden)
    db.session.flush()
    db.session.add(OrdenDetalle(orden_id=orden.id, producto_id=sample_producto.id,
                                cantidad=1, precio_unitario=Decimal('100'),
                                estado=OrdenEstado.LISTO))
    db.session.commit()
    orden.calcular_totales()
    db.session.commit()
    return orden


def _cobrar(client, orden_id, **payload):
    return client.post(f'/meseros/ordenes/{orden_id}/pago', json=payload)


class TestCobroConTransferencia:
    def test_transferencia_no_cierra_la_cuenta(self, client, db, mesero_user, orden_por_cobrar):
        from backend.models.models import Orden, OrdenEstado, Sale

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        resp = _cobrar(client, orden_por_cobrar.id, metodo='transferencia',
                       monto=100, referencia='FOLIO-123')
        datos = resp.get_json()

        assert datos['success'] is True
        assert datos['requiere_verificacion'] is True
        assert datos['orden_pagada'] is False

        orden = db.session.get(Orden, orden_por_cobrar.id)
        assert orden.estado != OrdenEstado.PAGADA, 'la cuenta se liberó sin confirmar el depósito'
        assert orden.saldo_pendiente() == Decimal('100.00')
        assert Sale.query.count() == 0, 'no debe haber venta antes de confirmar'

    def test_transferencia_exige_referencia(self, client, db, mesero_user, orden_por_cobrar):
        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        resp = _cobrar(client, orden_por_cobrar.id, metodo='transferencia',
                       monto=100, referencia='')

        assert resp.status_code == 400
        assert 'referencia' in resp.get_json()['message'].lower()

    def test_efectivo_no_requiere_verificacion(self, client, db, mesero_user, orden_por_cobrar):
        from backend.models.models import Orden, OrdenEstado

        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        datos = _cobrar(client, orden_por_cobrar.id, metodo='efectivo', monto=100).get_json()

        assert datos['orden_pagada'] is True
        assert datos.get('requiere_verificacion') is False
        assert db.session.get(Orden, orden_por_cobrar.id).estado == OrdenEstado.PAGADA

    def test_metodo_deshabilitado_se_rechaza(self, client, db, mesero_user, orden_por_cobrar):
        """El negocio no tiene terminal: cobrar con tarjeta no debe ser posible."""
        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        resp = _cobrar(client, orden_por_cobrar.id, metodo='tarjeta', monto=100)

        assert resp.status_code == 400
        assert 'no habilitado' in resp.get_json()['message'].lower()


class TestVerificacion:
    def _dejar_transferencia(self, client, db, orden):
        login(client, 'mesero_test@test.com', 'Test1234!')
        _cobrar(client, orden.id, metodo='transferencia', monto=100, referencia='FOLIO-9')
        client.post('/logout')
        from backend.models.models import Pago
        return Pago.query.filter_by(orden_id=orden.id).one()

    def test_confirmar_libera_la_cuenta_y_registra_la_venta(
            self, client, db, mesero_user, admin_user, orden_por_cobrar):
        from backend.models.models import Orden, OrdenEstado, Pago, Sale

        _setup_onboarding(db)
        pago = self._dejar_transferencia(client, db, orden_por_cobrar)

        login(client, 'admin_test@test.com', 'Test1234!')
        resp = client.post(f'/admin/pagos/{pago.id}/verificar')
        assert resp.status_code == 200
        assert resp.get_json()['orden_cerrada'] is True

        orden = db.session.get(Orden, orden_por_cobrar.id)
        assert orden.estado == OrdenEstado.PAGADA
        assert Sale.query.count() == 1

        pago = db.session.get(Pago, pago.id)
        assert pago.verificado is True
        assert pago.verificado_por == admin_user.id
        assert pago.fecha_verificacion is not None

    def test_la_venta_se_atribuye_al_mesero_no_a_quien_verifica(
            self, client, db, mesero_user, admin_user, orden_por_cobrar):
        from backend.models.models import Sale

        _setup_onboarding(db)
        pago = self._dejar_transferencia(client, db, orden_por_cobrar)
        login(client, 'admin_test@test.com', 'Test1234!')
        client.post(f'/admin/pagos/{pago.id}/verificar')

        venta = Sale.query.one()
        assert venta.usuario_id == mesero_user.id, 'la venta quedó a nombre de quien verificó'

    def test_rechazar_devuelve_la_cuenta_a_por_cobrar(
            self, client, db, mesero_user, admin_user, orden_por_cobrar):
        from backend.models.models import Orden, OrdenEstado, Pago, Sale

        _setup_onboarding(db)
        pago = self._dejar_transferencia(client, db, orden_por_cobrar)

        login(client, 'admin_test@test.com', 'Test1234!')
        resp = client.post(f'/admin/pagos/{pago.id}/rechazar',
                           json={'motivo': 'no aparece en el estado de cuenta'})
        assert resp.status_code == 200

        assert Pago.query.count() == 0
        orden = db.session.get(Orden, orden_por_cobrar.id)
        assert orden.estado != OrdenEstado.PAGADA
        assert orden.saldo_pendiente() == Decimal('100.00')
        assert Sale.query.count() == 0

    def test_no_se_puede_verificar_dos_veces(
            self, client, db, mesero_user, admin_user, orden_por_cobrar):
        from backend.models.models import Sale

        _setup_onboarding(db)
        pago = self._dejar_transferencia(client, db, orden_por_cobrar)
        login(client, 'admin_test@test.com', 'Test1234!')
        client.post(f'/admin/pagos/{pago.id}/verificar')
        resp = client.post(f'/admin/pagos/{pago.id}/verificar')

        assert resp.status_code == 409
        assert Sale.query.count() == 1, 'una doble confirmación duplicó la venta'

    def test_el_mesero_no_puede_verificar_su_propio_cobro(
            self, client, db, mesero_user, orden_por_cobrar):
        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        _cobrar(client, orden_por_cobrar.id, metodo='transferencia', monto=100,
                referencia='FOLIO-9')
        from backend.models.models import Pago
        pago = Pago.query.filter_by(orden_id=orden_por_cobrar.id).one()

        resp = client.post(f'/admin/pagos/{pago.id}/verificar', follow_redirects=False)
        assert resp.status_code in (302, 403), 'un mesero pudo confirmar su propia transferencia'
        assert db.session.get(Pago, pago.id).verificado is False


class TestCorteConTransferencias:
    def test_lo_no_confirmado_no_cuenta_como_ingreso(
            self, client, db, mesero_user, superadmin_user, orden_por_cobrar):
        _setup_onboarding(db)
        login(client, 'mesero_test@test.com', 'Test1234!')
        _cobrar(client, orden_por_cobrar.id, metodo='transferencia', monto=100,
                referencia='FOLIO-7')
        client.post('/logout')

        login(client, 'super_test@test.com', 'Test1234!')
        html = client.get('/admin/corte-caja').get_data(as_text=True)
        assert 'sin confirmar' in html, 'el corte no avisa de transferencias pendientes'
        assert 'Total Ingresos' in html
        # El depósito sin confirmar no debe sumarse al total del día
        assert '$100.00</div>' not in html.replace(' ', '').replace('\n', '')
