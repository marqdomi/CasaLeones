"""Verificación de la parte financiera: que las cuentas cuadren.

El caso que motivó estos tests: las fechas se guardan en UTC pero el día contable es
el día local del negocio. Filtrar con `func.date(col) == date.today()` mandaba toda la
venta posterior a las 18:00 hora de México al día siguiente — el corte de caja no veía
la cena, que es el grueso de una taquería.
"""
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from backend.services.tiempo import rango_utc
from tests.conftest import login

# Zona fija para que los tests den lo mismo corran donde corran.
TZ_NEGOCIO = ZoneInfo('America/Mexico_City')


@pytest.fixture(autouse=True)
def _zona_del_negocio(monkeypatch):
    monkeypatch.setenv('APP_TIMEZONE', 'America/Mexico_City')


def _setup_onboarding(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


def _utc_de_hora_local(hora, dia=None):
    """El instante UTC (naive, como se guarda) de las `hora`:00 locales de hoy."""
    dia = dia or datetime.now(TZ_NEGOCIO).date()
    local = datetime.combine(dia, time(hour=hora), tzinfo=TZ_NEGOCIO)
    return local.astimezone(timezone.utc).replace(tzinfo=None)


def _venta(db, usuario, hora, monto, metodo='efectivo', propina=0):
    """Registra una venta cerrada + su pago a una hora local dada."""
    from backend.models.models import Sale, Pago, Orden, OrdenEstado

    momento = _utc_de_hora_local(hora)
    db.session.add(Sale(fecha_hora=momento, usuario_id=usuario.id,
                        total=Decimal(str(monto)), estado='cerrada'))
    orden = Orden(mesero_id=usuario.id, estado=OrdenEstado.PAGADA,
                  fecha_pago=momento, total=Decimal(str(monto)),
                  propina=Decimal(str(propina)))
    db.session.add(orden)
    db.session.flush()
    db.session.add(Pago(orden_id=orden.id, metodo=metodo, monto=Decimal(str(monto)),
                        propina=Decimal(str(propina)),
                        fecha=momento, registrado_por=usuario.id))
    db.session.commit()
    return orden


class TestDiaContable:
    def test_rango_utc_cubre_la_jornada_completa(self):
        hoy = datetime.now(TZ_NEGOCIO).date()
        desde, hasta = rango_utc(hoy)
        # Un día local dura 24h aunque en UTC empiece a otra hora
        assert (hasta - desde) == timedelta(days=1)
        # La cena (20:00 local) cae dentro del día contable de hoy
        assert desde <= _utc_de_hora_local(20) < hasta
        # y la comida del día anterior no
        assert not (desde <= _utc_de_hora_local(20, hoy - timedelta(days=1)) < hasta)

    def test_la_cena_cuenta_en_el_corte_de_hoy(self, client, superadmin_user, db):
        """8:00, 13:00 y 22:00 locales son el mismo día de trabajo."""
        _setup_onboarding(db)
        for hora in (8, 13, 22):
            _venta(db, superadmin_user, hora, 100)

        login(client, 'super_test@test.com', 'Test1234!')
        html = client.get('/admin/corte-caja').get_data(as_text=True)
        assert '300.00' in html, 'el corte no sumó las tres ventas de la jornada'

    def test_dashboard_ventas_hoy_incluye_la_cena(self, client, admin_user, db):
        _setup_onboarding(db)
        _venta(db, admin_user, 21, 250)

        login(client, 'admin_test@test.com', 'Test1234!')
        data = client.get('/admin/api/dashboard/ventas_hoy?period=today').get_json()
        assert data['ventasHoy'] == 250.0

    def test_reporte_de_ventas_agrupa_por_dia_local(self, client, admin_user, db):
        """Dos ventas del mismo día de trabajo no deben partirse en dos días."""
        _setup_onboarding(db)
        _venta(db, admin_user, 9, 100)
        _venta(db, admin_user, 23, 100)

        login(client, 'admin_test@test.com', 'Test1234!')
        hoy = datetime.now(TZ_NEGOCIO).date().isoformat()
        data = client.get(f'/admin/reportes/api/ventas?fecha_inicio={hoy}&fecha_fin={hoy}').get_json()
        assert len(data['por_dia']['labels']) == 1, 'la jornada se partió en dos días'
        assert data['por_dia']['totales'][0] == 200.0
        # y la gráfica por hora usa horas locales, no UTC
        assert data['por_hora']['labels'] == ['09:00', '23:00']


class TestCuadreDeCaja:
    def test_totales_por_metodo_de_pago(self, client, superadmin_user, db):
        _setup_onboarding(db)
        _venta(db, superadmin_user, 12, 100, 'efectivo')
        _venta(db, superadmin_user, 19, 200, 'tarjeta')
        _venta(db, superadmin_user, 21, 50, 'efectivo')

        login(client, 'super_test@test.com', 'Test1234!')
        client.post('/admin/corte-caja', data={'efectivo_contado': '150.00', 'notas': ''})

        from backend.models.models import CorteCaja
        corte = CorteCaja.query.order_by(CorteCaja.id.desc()).first()
        assert float(corte.total_ingresos) == 350.0
        assert float(corte.efectivo_esperado) == 150.0, 'efectivo esperado debe excluir tarjeta'
        assert float(corte.tarjeta_total) == 200.0
        assert float(corte.diferencia) == 0.0, 'contado == esperado no debe dar diferencia'

    def test_las_propinas_en_efectivo_cuentan_en_el_arqueo(self, client, superadmin_user, db):
        """En el cajón está la venta MÁS la propina; si no, el arqueo sale sobrado."""
        _setup_onboarding(db)
        _venta(db, superadmin_user, 14, 75, 'efectivo', propina=20)

        login(client, 'super_test@test.com', 'Test1234!')
        html = client.get('/admin/corte-caja').get_data(as_text=True)
        assert '95.00' in html, 'el corte no dice cuánto efectivo debe haber en caja'

        # Contar exactamente los $95 del cajón no debe reportar sobrante
        client.post('/admin/corte-caja', data={'efectivo_contado': '95.00', 'notas': ''})
        from backend.models.models import CorteCaja
        corte = CorteCaja.query.order_by(CorteCaja.id.desc()).first()
        assert float(corte.diferencia) == 0.0, f'arqueo descuadrado por {corte.diferencia}'


class TestHorasQueVeElPersonal:
    def test_los_timestamps_para_javascript_llevan_zona(self):
        """Sin la 'Z', el navegador lee el timestamp como hora local y el
        cronómetro del KDS queda 6 horas en el futuro (marcando 00:00)."""
        from backend.services.tiempo import iso_utc

        marca = iso_utc(datetime(2026, 7, 21, 16, 3, 52))
        assert marca.endswith('Z'), marca

    def test_la_hora_mostrada_es_la_del_negocio(self, app):
        """Un ticket cobrado a la 1 de la tarde no puede aparecer como 19:00."""
        with app.test_request_context():
            filtro = app.jinja_env.filters['hora_local']
            # 19:00 UTC son las 13:00 en México
            assert filtro(datetime(2026, 7, 21, 19, 0)) == '13:00'


class TestIVAyTotales:
    def test_iva_incluido_en_precio(self, app, db, sample_producto, sample_mesa, mesero_user):
        """Precios con IVA incluido: total = precio de menú, IVA se extrae."""
        from backend.models.models import Orden, OrdenDetalle, OrdenEstado

        orden = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                      estado=OrdenEstado.PENDIENTE)
        db.session.add(orden)
        db.session.flush()
        db.session.add(OrdenDetalle(orden_id=orden.id, producto_id=sample_producto.id,
                                    cantidad=2, precio_unitario=sample_producto.precio))
        db.session.commit()

        total = orden.calcular_totales()
        bruto = Decimal(str(sample_producto.precio)) * 2
        assert total == bruto.quantize(Decimal('0.01'))
        # subtotal + IVA reconstruye el total (sin centavos perdidos)
        assert (orden.subtotal + orden.iva) == orden.total

    def test_descuento_reduce_total_e_iva(self, app, db, sample_producto, sample_mesa, mesero_user):
        from backend.models.models import Orden, OrdenDetalle, OrdenEstado

        orden = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                      estado=OrdenEstado.PENDIENTE, descuento_pct=Decimal('10'))
        db.session.add(orden)
        db.session.flush()
        db.session.add(OrdenDetalle(orden_id=orden.id, producto_id=sample_producto.id,
                                    cantidad=1, precio_unitario=Decimal('100')))
        db.session.commit()

        assert orden.calcular_totales() == Decimal('90.00')
        assert (orden.subtotal + orden.iva) == orden.total
