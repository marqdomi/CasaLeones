"""Tests for inventory management."""
import pytest
from decimal import Decimal


class TestInventoryModels:
    def test_ingrediente_creation(self, db):
        """Test creating an ingredient."""
        from backend.models.models import Ingrediente

        ing = Ingrediente(
            nombre='Carne al Pastor',
            unidad='kg',
            stock_actual=Decimal('25.0'),
            stock_minimo=Decimal('5.0'),
            costo_unitario=Decimal('120.00'),
        )
        db.session.add(ing)
        db.session.commit()
        assert ing.id is not None
        assert float(ing.stock_actual) == 25.0

    def test_receta_detalle(self, db, sample_producto):
        """Test recipe detail linking product to ingredient."""
        from backend.models.models import Ingrediente, RecetaDetalle

        ing = Ingrediente(
            nombre='Tortilla',
            unidad='pieza',
            stock_actual=Decimal('100'),
            stock_minimo=Decimal('20'),
            costo_unitario=Decimal('2.50'),
        )
        db.session.add(ing)
        db.session.flush()

        receta = RecetaDetalle(
            producto_id=sample_producto.id,
            ingrediente_id=ing.id,
            cantidad_necesaria=Decimal('2'),
        )
        db.session.add(receta)
        db.session.commit()

        assert receta.id is not None
        assert float(receta.cantidad_necesaria) == 2.0

    def test_movimiento_inventario(self, db):
        """Test inventory movements."""
        from backend.models.models import Ingrediente, MovimientoInventario

        ing = Ingrediente(
            nombre='Piña',
            unidad='kg',
            stock_actual=Decimal('10.0'),
            stock_minimo=Decimal('2.0'),
            costo_unitario=Decimal('30.00'),
        )
        db.session.add(ing)
        db.session.flush()

        mov = MovimientoInventario(
            ingrediente_id=ing.id,
            tipo='entrada',
            cantidad=Decimal('5.0'),
            motivo='Compra semanal',
        )
        db.session.add(mov)
        db.session.commit()

        assert mov.id is not None
        assert mov.tipo == 'entrada'


class TestStockAlerts:
    def test_low_stock_detection(self, db):
        """Test detecting low stock ingredients."""
        from backend.models.models import Ingrediente

        ing = Ingrediente(
            nombre='Cilantro',
            unidad='manojo',
            stock_actual=Decimal('3'),
            stock_minimo=Decimal('10'),
            costo_unitario=Decimal('5.00'),
        )
        db.session.add(ing)
        db.session.commit()

        low_stock = Ingrediente.query.filter(
            Ingrediente.stock_actual <= Ingrediente.stock_minimo
        ).all()
        assert len(low_stock) >= 1
        assert ing in low_stock
