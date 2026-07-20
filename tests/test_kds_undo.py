"""KDS: deshacer un item marcado listo por error (ventana de undo)."""
from datetime import timedelta
from tests.conftest import login, _make_user


def _setup(db, sample_categoria):
    """Onboarding + estación + producto + cocinero. Devuelve (estacion, producto, cocinero)."""
    from backend.models.models import ConfiguracionSistema, Estacion, Producto
    db.session.add(ConfiguracionSistema(clave='onboarding_completado', valor='true'))
    est = Estacion(nombre='Barbacoa')
    db.session.add(est)
    db.session.flush()
    prod = Producto(nombre='Taco undo', precio=30, categoria_id=sample_categoria.id, estacion_id=est.id)
    db.session.add(prod)
    db.session.commit()
    cocinero = _make_user(db, 'Coci', 'coci@test.com', 'Test1234!', 'cocina')
    cocinero.estacion_id = est.id
    db.session.commit()
    return est, prod, cocinero


def _orden_enviada(db, mesero, producto, cantidad_items=1):
    from backend.models.models import Orden, OrdenDetalle, OrdenEstado
    orden = Orden(mesero_id=mesero.id, estado=OrdenEstado.ENVIADO)
    db.session.add(orden)
    db.session.flush()
    detalles = []
    for _ in range(cantidad_items):
        d = OrdenDetalle(orden_id=orden.id, producto_id=producto.id, cantidad=1,
                         precio_unitario=30, estado=OrdenEstado.PENDIENTE)
        db.session.add(d)
        detalles.append(d)
    db.session.commit()
    return orden, detalles


class TestKdsUndo:

    def test_undo_dentro_de_ventana(self, client, db, mesero_user, sample_categoria):
        from backend.models.models import OrdenEstado
        est, prod, coci = _setup(db, sample_categoria)
        orden, (d1, d2) = _orden_enviada(db, mesero_user, prod, 2)

        login(client, coci.email, 'Test1234!')
        r = client.post(f'/cocina/barbacoa/marcar/{orden.id}/{d1.id}')
        assert r.status_code == 200
        db.session.refresh(d1)
        assert d1.estado == OrdenEstado.LISTO

        r = client.post(f'/cocina/barbacoa/desmarcar/{orden.id}/{d1.id}')
        assert r.status_code == 200, r.get_json()
        db.session.refresh(d1)
        assert d1.estado == OrdenEstado.PENDIENTE
        assert d1.fecha_listo is None

    def test_undo_regresa_orden_completa_al_kds(self, client, db, mesero_user, sample_categoria):
        from backend.models.models import OrdenEstado
        est, prod, coci = _setup(db, sample_categoria)
        orden, (d1,) = _orden_enviada(db, mesero_user, prod, 1)

        login(client, coci.email, 'Test1234!')
        client.post(f'/cocina/barbacoa/marcar/{orden.id}/{d1.id}')
        db.session.refresh(orden)
        assert orden.estado == OrdenEstado.LISTA_PARA_ENTREGAR, 'último item → orden completa'

        r = client.post(f'/cocina/barbacoa/desmarcar/{orden.id}/{d1.id}')
        assert r.status_code == 200
        db.session.refresh(orden)
        assert orden.estado == OrdenEstado.EN_PREPARACION, 'la orden debe regresar al KDS'

    def test_undo_fuera_de_ventana_rechazado(self, client, db, mesero_user, sample_categoria):
        from backend.models.models import OrdenEstado, utc_now
        est, prod, coci = _setup(db, sample_categoria)
        orden, (d1,) = _orden_enviada(db, mesero_user, prod, 1)

        login(client, coci.email, 'Test1234!')
        client.post(f'/cocina/barbacoa/marcar/{orden.id}/{d1.id}')
        # Simular que pasaron 5 minutos
        db.session.refresh(d1)
        d1.fecha_listo = utc_now().replace(tzinfo=None) - timedelta(minutes=5)
        # dejar la orden en preparación para aislar el motivo del rechazo
        orden.estado = OrdenEstado.EN_PREPARACION
        db.session.commit()

        r = client.post(f'/cocina/barbacoa/desmarcar/{orden.id}/{d1.id}')
        assert r.status_code == 409
        assert 'ventana' in r.get_json()['error']
        db.session.refresh(d1)
        assert d1.estado == OrdenEstado.LISTO, 'el item no debe cambiar'

    def test_undo_item_de_otra_estacion_rechazado(self, client, db, mesero_user, sample_categoria):
        from backend.models.models import Estacion, Producto, OrdenEstado
        est, prod, coci = _setup(db, sample_categoria)
        otra = Estacion(nombre='Bebidas')
        db.session.add(otra)
        db.session.flush()
        prod_bebida = Producto(nombre='Agua undo', precio=15,
                               categoria_id=sample_categoria.id, estacion_id=otra.id)
        db.session.add(prod_bebida)
        db.session.commit()
        orden, (d1,) = _orden_enviada(db, mesero_user, prod_bebida, 1)
        d1.estado = OrdenEstado.LISTO
        from backend.models.models import utc_now
        d1.fecha_listo = utc_now().replace(tzinfo=None)
        db.session.commit()

        login(client, coci.email, 'Test1234!')  # cocinero de Barbacoa
        r = client.post(f'/cocina/barbacoa/desmarcar/{orden.id}/{d1.id}')
        assert r.status_code == 403

    def test_undo_orden_pagada_rechazado(self, client, db, mesero_user, sample_categoria):
        from backend.models.models import OrdenEstado, utc_now
        est, prod, coci = _setup(db, sample_categoria)
        orden, (d1,) = _orden_enviada(db, mesero_user, prod, 1)
        d1.estado = OrdenEstado.LISTO
        d1.fecha_listo = utc_now().replace(tzinfo=None)
        orden.estado = OrdenEstado.PAGADA
        db.session.commit()

        login(client, coci.email, 'Test1234!')
        r = client.post(f'/cocina/barbacoa/desmarcar/{orden.id}/{d1.id}')
        assert r.status_code == 409
