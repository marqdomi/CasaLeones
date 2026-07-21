"""Tests del panel de administración: APIs del dashboard y corte de caja.

Cubren rutas que sólo se ejercitan desde el navegador (fetch del dashboard, POST del
corte) y que por eso pasaban desapercibidas cuando rompían con 500.
"""
from tests.conftest import login


DASHBOARD_APIS = [
    'ventas_hoy', 'ordenes_hoy', 'ticket_promedio', 'top_productos',
    'mesas_activas', 'ordenes_cocina', 'alertas_stock', 'propinas_hoy',
    'ultimo_corte', 'ventas_7dias', 'actividad_reciente',
]


def _setup_onboarding(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


def _login_admin(client, db):
    _setup_onboarding(db)
    login(client, 'admin_test@test.com', 'Test1234!')


class TestDashboardAPIs:
    def test_todas_las_apis_responden_json(self, client, admin_user, db):
        _login_admin(client, db)
        for nombre in DASHBOARD_APIS:
            resp = client.get(f'/admin/api/dashboard/{nombre}')
            assert resp.status_code == 200, f'{nombre} devolvió {resp.status_code}'
            assert resp.get_json() is not None, f'{nombre} no devolvió JSON'

    def test_ordenes_cocina_cuenta_ordenes_del_kds(self, client, admin_user, db, sample_mesa, mesero_user):
        """Cuenta los estados que el KDS muestra (enviado / en preparación)."""
        from backend.models.models import Orden, OrdenEstado

        db.session.add_all([
            Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id, estado=OrdenEstado.ENVIADO),
            Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id, estado=OrdenEstado.EN_PREPARACION),
            Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id, estado=OrdenEstado.PENDIENTE),
            Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id, estado=OrdenEstado.PAGADA),
        ])
        db.session.commit()

        _login_admin(client, db)
        data = client.get('/admin/api/dashboard/ordenes_cocina').get_json()
        assert data['pendientes'] == 2
        assert data['timer_promedio_min'] >= 0

    def test_actividad_reciente_incluye_alias_de_cuenta(self, client, admin_user, db, sample_mesa, mesero_user):
        """Mesas compartidas: el feed debe distinguir cuentas de la misma mesa."""
        from backend.models.models import Orden, OrdenEstado

        db.session.add(Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                             estado=OrdenEstado.ENVIADO, alias='los de la esquina'))
        db.session.commit()

        _login_admin(client, db)
        items = client.get('/admin/api/dashboard/actividad_reciente').get_json()['items']
        assert any(i['alias'] == 'los de la esquina' for i in items)


class TestCorteCaja:
    def test_generar_corte_de_caja(self, client, superadmin_user, db):
        from backend.models.models import CorteCaja

        _setup_onboarding(db)
        login(client, 'super_test@test.com', 'Test1234!')
        resp = client.post('/admin/corte-caja',
                           data={'efectivo_contado': '100.00', 'notas': 'corte de prueba'},
                           follow_redirects=False)
        assert resp.status_code == 302
        corte = CorteCaja.query.order_by(CorteCaja.id.desc()).first()
        assert corte is not None
        assert corte.usuario_id == superadmin_user.id


class TestRutasLegacyProductos:
    def test_urls_viejas_redirigen_al_crud_vigente(self, client, admin_user, db):
        _login_admin(client, db)
        assert client.get('/admin/productos/').status_code == 302
        assert client.get('/admin/productos/crear').status_code == 302
