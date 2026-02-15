"""Tests for models and core business logic."""
import pytest
from decimal import Decimal


class TestUsuarioModel:
    def test_create_usuario(self, db):
        from backend.models.models import Usuario
        from werkzeug.security import generate_password_hash

        user = Usuario(
            nombre='Test User',
            username='test_user',
            password=generate_password_hash('Pass1234!'),
            rol='mesero',
        )
        db.session.add(user)
        db.session.commit()
        assert user.id is not None
        assert user.rol == 'mesero'

    def test_usuario_roles(self, db):
        from backend.models.models import Usuario
        from werkzeug.security import generate_password_hash

        roles = ['superadmin', 'admin', 'mesero', 'taquero', 'comal', 'bebidas']
        for rol in roles:
            user = Usuario(
                nombre=f'User {rol}',
                username=f'user_{rol}',
                password=generate_password_hash('Pass1234!'),
                rol=rol,
            )
            db.session.add(user)
        db.session.commit()
        assert Usuario.query.count() == len(roles)


class TestProductoModel:
    def test_create_producto(self, sample_producto):
        assert sample_producto.id is not None
        assert sample_producto.nombre == 'Taco al Pastor'
        assert float(sample_producto.precio) == 45.0

    def test_producto_disponibilidad(self, db):
        from backend.models.models import Producto

        prod = Producto(nombre='Quesadilla', precio=55.0, categoria='tacos', disponible=False)
        db.session.add(prod)
        db.session.commit()

        disponibles = Producto.query.filter_by(disponible=True).count()
        no_disponibles = Producto.query.filter_by(disponible=False).count()
        assert no_disponibles >= 1


class TestMesaModel:
    def test_create_mesa(self, sample_mesa):
        assert sample_mesa.id is not None
        assert sample_mesa.numero == 1
        assert sample_mesa.estado == 'disponible'

    def test_mesa_estados(self, db):
        from backend.models.models import Mesa

        estados = ['disponible', 'ocupada', 'reservada', 'mantenimiento']
        for i, estado in enumerate(estados):
            mesa = Mesa(numero=10 + i, capacidad=4, zona='test', estado=estado)
            db.session.add(mesa)
        db.session.commit()
        assert Mesa.query.count() >= len(estados)


class TestOrdenModel:
    def test_orden_calcular_totales(self, db, sample_producto):
        from backend.models.models import Orden, OrdenDetalle, IVA_RATE

        orden = Orden(estado='pendiente')
        db.session.add(orden)
        db.session.flush()

        d = OrdenDetalle(
            orden_id=orden.id,
            producto_id=sample_producto.id,
            cantidad=3,
            precio_unitario=Decimal('45.00'),
        )
        db.session.add(d)
        db.session.flush()

        orden.calcular_totales()
        assert float(orden.subtotal) == 135.0
        assert float(orden.iva) == pytest.approx(135.0 * float(IVA_RATE), abs=0.01)

    def test_orden_propina(self, db):
        from backend.models.models import Orden

        orden = Orden(estado='pagada', propina=Decimal('50.00'))
        db.session.add(orden)
        db.session.commit()
        assert float(orden.propina) == 50.0


class TestClienteModel:
    def test_create_cliente(self, db):
        from backend.models.models import Cliente

        cliente = Cliente(
            nombre='Juan López',
            rfc='LOJJ900101AAA',
            razon_social='Juan López',
            uso_cfdi='G03',
            regimen_fiscal='612',
        )
        db.session.add(cliente)
        db.session.commit()
        assert cliente.id is not None


class TestFacturaModel:
    def test_create_factura(self, db, sample_producto):
        from backend.models.models import Orden, OrdenDetalle, Factura, Cliente

        cliente = Cliente(nombre='Test', rfc='XAXX010101000', razon_social='Test SA')
        db.session.add(cliente)

        orden = Orden(estado='pagada')
        db.session.add(orden)
        db.session.flush()

        d = OrdenDetalle(
            orden_id=orden.id, producto_id=sample_producto.id,
            cantidad=1, precio_unitario=Decimal('100.00'))
        db.session.add(d)
        db.session.flush()
        orden.calcular_totales()

        factura = Factura(
            orden_id=orden.id,
            cliente_id=cliente.id,
            rfc_receptor='XAXX010101000',
            razon_social='Test SA',
            subtotal=orden.subtotal,
            iva=orden.iva,
            total=orden.total,
            estado='pendiente',
            metodo_pago_cfdi='PUE',
        )
        db.session.add(factura)
        db.session.commit()
        assert factura.id is not None
        assert factura.metodo_pago_cfdi == 'PUE'

    def test_factura_ppd(self, db, sample_producto):
        from backend.models.models import Orden, OrdenDetalle, Factura, Cliente

        cliente = Cliente(nombre='PPD Test', rfc='XAXX010101000', razon_social='PPD SA')
        db.session.add(cliente)

        orden = Orden(estado='pagada')
        db.session.add(orden)
        db.session.flush()

        d = OrdenDetalle(
            orden_id=orden.id, producto_id=sample_producto.id,
            cantidad=1, precio_unitario=Decimal('200.00'))
        db.session.add(d)
        db.session.flush()
        orden.calcular_totales()

        factura = Factura(
            orden_id=orden.id,
            cliente_id=cliente.id,
            rfc_receptor='XAXX010101000',
            razon_social='PPD SA',
            subtotal=orden.subtotal,
            iva=orden.iva,
            total=orden.total,
            estado='pendiente',
            metodo_pago_cfdi='PPD',
            forma_pago='99',
        )
        db.session.add(factura)
        db.session.commit()
        assert factura.metodo_pago_cfdi == 'PPD'
        assert factura.forma_pago == '99'


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get('/health')
        assert resp.status_code in (200, 503)
        data = resp.get_json()
        assert 'status' in data
