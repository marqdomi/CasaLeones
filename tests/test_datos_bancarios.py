"""Datos bancarios del negocio para cobrar por transferencia."""
import pytest

from backend.services.banco import (datos_bancarios, digito_verificador_clabe,
                                    formatear_clabe, validar_clabe)
from tests.conftest import login


def _setup_onboarding(db):
    from backend.models.models import ConfiguracionSistema
    if not ConfiguracionSistema.query.filter_by(clave='onboarding_completado').first():
        db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
        db.session.commit()


class TestValidacionCLABE:
    @pytest.mark.parametrize('clabe', [
        '032180000118359719',
        '002010077777777771',
        '646180110400000007',
    ])
    def test_clabes_reales_pasan(self, clabe):
        valida, _ = validar_clabe(clabe)
        assert valida, f'{clabe} debería ser válida'

    def test_un_digito_cambiado_se_detecta(self):
        """Justo el error que manda el dinero a la cuenta de otra persona."""
        valida, mensaje = validar_clabe('032180000118359718')
        assert not valida
        assert 'válida' in mensaje

    def test_longitud_incorrecta(self):
        valida, mensaje = validar_clabe('03218000011835')
        assert not valida
        assert '18 dígitos' in mensaje

    def test_vacia_es_aceptable(self):
        """Capturarla es opcional: el negocio puede no usar transferencias."""
        valida, _ = validar_clabe('')
        assert valida

    def test_ignora_espacios_al_capturar(self):
        valida, _ = validar_clabe('0321 8000 0118 3597 19')
        assert valida

    def test_digito_verificador_coincide_con_el_real(self):
        assert digito_verificador_clabe('03218000011835971') == 9

    def test_se_muestra_agrupada_para_leerla(self):
        assert formatear_clabe('032180000118359719') == '0321 8000 0118 3597 19'


class TestConfiguracionEnAdmin:
    def test_guardar_datos_bancarios(self, client, superadmin_user, db, app):
        from backend.models.models import Sucursal

        _setup_onboarding(db)
        db.session.add(Sucursal(nombre='Barbacoa Demo'))
        db.session.commit()

        login(client, 'super_test@test.com', 'Test1234!')
        resp = client.post('/admin/personalizacion', data={
            'nombre': 'Barbacoa Demo',
            'color_primario': '#C41E3A',
            'metodos_pago': ['efectivo', 'transferencia'],
            'banco_nombre': 'BBVA',
            'banco_titular': 'María Ramírez',
            'banco_clabe': '032180000118359719',
        }, follow_redirects=True)
        assert resp.status_code == 200

        with app.test_request_context():
            datos = datos_bancarios()
        assert datos['banco_nombre'] == 'BBVA'
        assert datos['banco_clabe'] == '032180000118359719'
        assert datos['configurado'] is True

    def test_una_clabe_invalida_no_se_guarda(self, client, superadmin_user, db, app):
        from backend.models.models import Sucursal

        _setup_onboarding(db)
        db.session.add(Sucursal(nombre='Barbacoa Demo'))
        db.session.commit()

        login(client, 'super_test@test.com', 'Test1234!')
        resp = client.post('/admin/personalizacion', data={
            'nombre': 'Barbacoa Demo',
            'color_primario': '#C41E3A',
            'metodos_pago': ['efectivo'],
            'banco_clabe': '032180000118359718',  # último dígito mal
        }, follow_redirects=True)

        assert 'no es válida' in resp.get_data(as_text=True)
        with app.test_request_context():
            assert datos_bancarios()['banco_clabe'] == ''


class TestEnPantallaDeCobro:
    def test_la_cuenta_aparece_al_cobrar(self, client, db, sample_producto,
                                         sample_mesa, mesero_user):
        from backend.models.models import (ConfiguracionSistema, Orden,
                                           OrdenDetalle, OrdenEstado)
        from decimal import Decimal

        _setup_onboarding(db)
        ConfiguracionSistema.set('banco_nombre', 'BBVA')
        ConfiguracionSistema.set('banco_clabe', '032180000118359719')
        db.session.commit()

        orden = Orden(mesa_id=sample_mesa.id, mesero_id=mesero_user.id,
                      estado=OrdenEstado.COMPLETADA)
        db.session.add(orden)
        db.session.flush()
        db.session.add(OrdenDetalle(orden_id=orden.id, producto_id=sample_producto.id,
                                    cantidad=1, precio_unitario=Decimal('100')))
        db.session.commit()

        login(client, 'mesero_test@test.com', 'Test1234!')
        html = client.get(f'/meseros/ordenes/{orden.id}/pago_view').get_data(as_text=True)

        assert 'BBVA' in html
        assert '0321 8000 0118 3597 19' in html, 'la CLABE debe verse agrupada para dictarla'
