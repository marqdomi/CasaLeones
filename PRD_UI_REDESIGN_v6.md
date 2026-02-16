# PRD — CasaLeones POS: Enterprise UI Redesign v6.0

**Fecha:** 2026-02-15  
**Autor:** Auditoría automatizada + análisis de industria  
**Estado:** Draft — pendiente aprobación  
**Versión actual del producto:** v5.5  
**Versión objetivo:** v6.0  

---

## 1. Resumen Ejecutivo

### Problema

La interfaz actual de CasaLeones POS fue construida de forma incremental a lo largo de 6 sprints, acumulando deuda técnica visual significativa. El resultado es una UI funcional pero inconsistente, visualmente datada, y que no proyecta la imagen enterprise que el producto necesita para competir con soluciones como **Toast POS**, **Square Restaurant**, **Lightspeed** o **TouchBistro**.

### Hallazgos Clave de la Auditoría

| Categoría | Calificación Actual | Objetivo |
|-----------|---------------------|----------|
| Consistencia Visual | 2.5/5 | 4.5/5 |
| Sistema de Diseño | 2/5 (ad-hoc) | 5/5 (design tokens + componentes) |
| Responsividad | 3/5 | 4.5/5 |
| Accesibilidad (WCAG) | 2/5 | 4/5 (AA compliant) |
| UX/Flujos | 3/5 | 4.5/5 |
| Performance Percibido | 3/5 | 4.5/5 |

### Propuesta

Rediseño completo del frontend manteniendo el stack actual (Flask + Jinja2 + Bootstrap 5.3), implementando:

1. **Design System** con tokens CSS, macros Jinja2 reutilizables, y componentes estandarizados
2. **Navegación enterprise** con sidebar colapsable (admin) y top-bar contextual (operaciones)
3. **Dashboards modernos** con KPIs interactivos, gráficas mejoradas, y datos en tiempo real
4. **Kitchen Display System** optimizado para legibilidad a distancia y urgencia visual
5. **Flujos de pago y pedidos** rediseñados con split-panel layout
6. **CRUD enterprise** con búsqueda, filtrado, paginación, y acciones masivas
7. **Accesibilidad WCAG 2.1 AA** completa

---

## 2. Auditoría Detallada del Estado Actual

### 2.1 Problemas Críticos Encontrados

#### P0 — Bloquers (rompen funcionalidad)

| # | Problema | Archivo(s) | Impacto |
|---|----------|------------|---------|
| 1 | **Font Awesome nunca se carga** — todos los íconos `<i class="fas fa-*">` son invisibles | `corte_caja.html`, reportes/*, facturacion/*, delivery/* | Íconos críticos no se ven: exportar, PDF, acciones |
| 2 | **pago.html tiene bloques Jinja2 anidados** incorrectamente (`{% block scripts %}` dentro de `{% block content %}`) | `pago.html` | Scripts de pago pueden no ejecutarse |
| 3 | **pago.html sin CSRF token** en formulario de pago | `pago.html` | Vulnerabilidad de seguridad activa |
| 4 | **producto_form usa inputs numéricos crudos** para Categoría/Estación en vez de `<select>` | `producto_form.html` | Admin debe conocer IDs de memoria |

#### P1 — Alto Impacto UX

| # | Problema | Archivo(s) | Impacto |
|---|----------|------------|---------|
| 5 | **Sin paginación** en ninguna tabla CRUD | usuarios, productos, mesas, clientes, ingredientes, facturas, reservaciones, historial_dia | Degradación con >50 registros |
| 6 | **Sin `table-responsive`** en varias tablas | usuarios.html, productos.html, mesas.html | Overflow horizontal en móvil |
| 7 | **seleccionar_mesa no muestra estado** de mesa | seleccionar_mesa.html | Se puede seleccionar mesa ocupada/reservada |
| 8 | **Nav pills admin duplicados** en ~8 templates sin partial, mayoría sin estado `active` | Todos los CRUD admin | Navegación confusa |
| 9 | **detalle_orden tiene `me-5`** inexplicable creando margen derecho de 3rem | detalle_orden.html | Layout roto en pantallas medianas |
| 10 | **historial_dia tiene botón Export CSV permanentemente `disabled`** | historial_dia.html | Funcionalidad muerta visible al usuario |

#### P2 — Deuda Técnica Visual

| # | Problema | Impacto |
|---|----------|---------|
| 11 | CSS duplicado (`body` definido 2 veces en styles.css con colores contradictorios: `#000` vs `var(--color-light)`) | Conflictos de renderizado |
| 12 | jQuery 3.6 cargado solo en estaciones cocina + vanilla fetch en el resto | Bundle size innecesario |
| 13 | `container` vs `container-fluid` inconsistente entre páginas | Anchos de contenido erráticos |
| 14 | Emojis usados como íconos sin `aria-hidden` consistente | Accesibilidad degradada |
| 15 | Sin `<title>` block en usuarios, productos, mesas | SEO y usabilidad (tabs del navegador) |

### 2.2 Calificaciones por Módulo

| Módulo | Rating | Fortalezas | Debilidades |
|--------|--------|------------|-------------|
| **Reportes** | 4/5 | Patrón consistente, charts, exports, toggle tabla/gráfica | Font Awesome invisible |
| **Admin Dashboard** | 4/5 | KPIs, skeleton loading, charts, real-time refresh | Emojis como íconos, sin manual refresh |
| **Mapa Mesas** | 4/5 | Drag-drop, leyenda, filtros zona, fallback móvil | — |
| **Estaciones Cocina** | 3.5/5 | Socket.IO, timers, dark mode | jQuery Legacy, alert() en errores |
| **Facturación** | 3.5/5 | Forms SAT bien resueltos, catálogos dinámicos | Lista sin paginación |
| **Meseros** | 3.5/5 | Accordion real-time, modal cobro | Modal cobro incompleto (sin propina visual) |
| **Corte de Caja** | 3.5/5 | KPIs, reconciliación, PDF export | Sin paginación historial |
| **Inventario** | 3/5 | Forms consistentes, alertas stock | Sin búsqueda/paginación |
| **CRM/Clientes** | 3/5 | Form excelente con datos fiscales | Lista básica sin filtros |
| **CRUD Admin** | 2/5 | — | Tablas desnudas, sin búsqueda, sin responsive |
| **Pago** | 1.5/5 | — | Bloques Jinja2 rotos, sin CSRF, sin multi-pago |
| **Seleccionar Mesa** | 2/5 | Grid responsive | Ciega al estado de mesa |

---

## 3. Benchmarking: Estándares de la Industria

### 3.1 Líderes de Referencia

| Sistema | Fortaleza Principal | Lo que CasaLeones debe adoptar |
|---------|---------------------|-------------------------------|
| **Toast POS** | Split-panel layout para pedidos, navegación lateral | Layout de 2 paneles: menú + carrito |
| **Square Restaurant** | Diseño limpio y minimalista, flujo de pago intuitivo | Tipografía Inter, espaciado 8px grid |
| **Lightspeed** | Dashboard admin con sidebar, reportes interactivos | Sidebar colapsable para admin |
| **TouchBistro** | Floor plan como home screen, drag-drop mesas | Mapa de mesas como pantalla principal meseros |
| **Aloha POS** | KDS con gradientes de urgencia por tiempo | Sistema de colores por tiempo en cocina |
| **Clover** | Componentes modulares, tema consistente | Design tokens + macros Jinja2 |
| **Revel** | CRUD enterprise con bulk actions | Tablas con search + filtros + paginación |

### 3.2 Patrones de Diseño Clave

**Split-Panel Layout (Pedidos):**
```
┌─────────────────────────────────────────────┐
│  Categorías (pills horizontal)              │
├──────────────────────┬──────────────────────┤
│  Productos (grid)    │  Carrito (sticky)    │
│  ┌──────┐ ┌──────┐  │  ┌──────────────┐   │
│  │ Prod │ │ Prod │  │  │ Item 1    $80 │   │
│  └──────┘ └──────┘  │  │ Item 2    $45 │   │
│  ┌──────┐ ┌──────┐  │  ├──────────────┤   │
│  │ Prod │ │ Prod │  │  │ Total    $125 │   │
│  └──────┘ └──────┘  │  │ [Cobrar]      │   │
│                      │  └──────────────┘   │
└──────────────────────┴──────────────────────┘
```

**Admin Sidebar (Back-office):**
```
┌────────┬───────────────────────────────────┐
│ LOGO   │ Breadcrumb > Usuarios > Lista     │
│────────│───────────────────────────────────│
│ 📊 Dash│ ┌─────────────────────────────┐   │
│ 👥 Users│ │ [Buscar...] [Filtro▼] [+Nuevo]│  │
│ 🍽 Prods │ ├─────────────────────────────┤   │
│ 📦 Inv │ │ Tabla paginada con actions  │   │
│ 📋 Orders│ │ □ User1  Admin  Editar Elim │   │
│ 💰 Sales│ │ □ User2  Mesero Editar Elim │   │
│────────│ ├─────────────────────────────┤   │
│ 🔧 Config│ │ ← 1 2 3 ... 10 →          │   │
│ 📈 Report│ └─────────────────────────────┘   │
└────────┴───────────────────────────────────┘
```

---

## 4. Especificaciones de Diseño

### 4.1 Design Tokens (CSS Custom Properties)

```css
:root {
  /* ═══════════════════════════
     COLORES — Paleta CasaLeones
     ═══════════════════════════ */
  
  /* Primarios */
  --cl-red-50:  #FFF5F5;
  --cl-red-100: #FED7D7;
  --cl-red-200: #FEB2B2;
  --cl-red-400: #E5535A;
  --cl-red-500: #C41E3A;   /* Primary — rojo CasaLeones refinado */
  --cl-red-600: #A6192E;   /* Primary hover */
  --cl-red-700: #8B1525;
  --cl-red-900: #5C0D19;

  /* Neutrales */
  --cl-gray-25:  #FCFCFD;
  --cl-gray-50:  #F9FAFB;
  --cl-gray-100: #F2F4F7;
  --cl-gray-200: #EAECF0;
  --cl-gray-300: #D0D5DD;
  --cl-gray-400: #98A2B3;
  --cl-gray-500: #667085;
  --cl-gray-600: #475467;
  --cl-gray-700: #344054;
  --cl-gray-800: #1D2939;
  --cl-gray-900: #101828;

  /* Semánticos */
  --cl-success-50:  #ECFDF5;
  --cl-success-500: #12B76A;
  --cl-success-700: #027A48;
  --cl-warning-50:  #FFFAEB;
  --cl-warning-500: #F79009;
  --cl-warning-700: #B54708;
  --cl-error-50:  #FEF3F2;
  --cl-error-500: #F04438;
  --cl-error-700: #B42318;
  --cl-info-50:  #EFF8FF;
  --cl-info-500: #2E90FA;
  --cl-info-700: #175CD3;

  /* Superficies */
  --cl-bg-primary:   #FFFFFF;
  --cl-bg-secondary: var(--cl-gray-50);
  --cl-bg-tertiary:  var(--cl-gray-100);
  --cl-bg-brand:     var(--cl-red-50);

  /* Texto */
  --cl-text-primary:    var(--cl-gray-900);
  --cl-text-secondary:  var(--cl-gray-600);
  --cl-text-tertiary:   var(--cl-gray-500);
  --cl-text-placeholder: var(--cl-gray-400);
  --cl-text-on-brand:   #FFFFFF;
  --cl-text-brand:      var(--cl-red-500);

  /* Bordes */
  --cl-border-primary:   var(--cl-gray-300);
  --cl-border-secondary: var(--cl-gray-200);
  --cl-border-brand:     var(--cl-red-500);

  /* ═══════════════════════════
     TIPOGRAFÍA — Inter Font Stack
     ═══════════════════════════ */
  --cl-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --cl-font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace;

  /* Tamaños (Type Scale — Major Third 1.250) */
  --cl-text-xs:   0.75rem;    /* 12px */
  --cl-text-sm:   0.875rem;   /* 14px */
  --cl-text-base: 1rem;       /* 16px */
  --cl-text-lg:   1.125rem;   /* 18px */
  --cl-text-xl:   1.25rem;    /* 20px */
  --cl-text-2xl:  1.5rem;     /* 24px */
  --cl-text-3xl:  1.875rem;   /* 30px */
  --cl-text-4xl:  2.25rem;    /* 36px */
  --cl-text-kds:  3.5rem;     /* 56px — Kitchen Display */

  /* Pesos */
  --cl-font-regular: 400;
  --cl-font-medium:  500;
  --cl-font-semibold: 600;
  --cl-font-bold:    700;

  /* Line Heights */
  --cl-leading-tight:  1.25;
  --cl-leading-normal: 1.5;
  --cl-leading-relaxed: 1.75;

  /* ═══════════════════════════
     ESPACIADO — 8px Grid System
     ═══════════════════════════ */
  --cl-space-0:  0;
  --cl-space-1:  0.25rem;   /* 4px */
  --cl-space-2:  0.5rem;    /* 8px */
  --cl-space-3:  0.75rem;   /* 12px */
  --cl-space-4:  1rem;      /* 16px */
  --cl-space-5:  1.25rem;   /* 20px */
  --cl-space-6:  1.5rem;    /* 24px */
  --cl-space-8:  2rem;      /* 32px */
  --cl-space-10: 2.5rem;    /* 40px */
  --cl-space-12: 3rem;      /* 48px */
  --cl-space-16: 4rem;      /* 64px */

  /* ═══════════════════════════
     ELEVACIÓN — Sombras
     ═══════════════════════════ */
  --cl-shadow-xs:  0 1px 2px rgba(16,24,40,0.05);
  --cl-shadow-sm:  0 1px 3px rgba(16,24,40,0.10), 0 1px 2px rgba(16,24,40,0.06);
  --cl-shadow-md:  0 4px 8px -2px rgba(16,24,40,0.10), 0 2px 4px -2px rgba(16,24,40,0.06);
  --cl-shadow-lg:  0 12px 16px -4px rgba(16,24,40,0.08), 0 4px 6px -2px rgba(16,24,40,0.03);
  --cl-shadow-xl:  0 20px 24px -4px rgba(16,24,40,0.08), 0 8px 8px -4px rgba(16,24,40,0.03);
  --cl-shadow-2xl: 0 24px 48px -12px rgba(16,24,40,0.18);

  /* ═══════════════════════════
     BORDES & RADII
     ═══════════════════════════ */
  --cl-radius-sm:   0.375rem;   /* 6px */
  --cl-radius-md:   0.5rem;     /* 8px */
  --cl-radius-lg:   0.75rem;    /* 12px */
  --cl-radius-xl:   1rem;       /* 16px */
  --cl-radius-2xl:  1.5rem;     /* 24px */
  --cl-radius-full: 9999px;

  /* ═══════════════════════════
     TRANSICIONES
     ═══════════════════════════ */
  --cl-transition-fast:   150ms cubic-bezier(0.4, 0, 0.2, 1);
  --cl-transition-base:   200ms cubic-bezier(0.4, 0, 0.2, 1);
  --cl-transition-slow:   300ms cubic-bezier(0.4, 0, 0.2, 1);
  --cl-transition-spring: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);

  /* ═══════════════════════════
     LAYOUT
     ═══════════════════════════ */
  --cl-sidebar-width: 260px;
  --cl-sidebar-collapsed: 72px;
  --cl-topbar-height: 64px;
  --cl-content-max-width: 1280px;
  --cl-form-max-width: 640px;
}

/* ═══════════════════════════
   DARK MODE TOKENS
   ═══════════════════════════ */
[data-bs-theme="dark"] {
  --cl-bg-primary:    var(--cl-gray-900);
  --cl-bg-secondary:  var(--cl-gray-800);
  --cl-bg-tertiary:   var(--cl-gray-700);
  --cl-bg-brand:      var(--cl-red-900);

  --cl-text-primary:    var(--cl-gray-50);
  --cl-text-secondary:  var(--cl-gray-300);
  --cl-text-tertiary:   var(--cl-gray-400);

  --cl-border-primary:   var(--cl-gray-600);
  --cl-border-secondary: var(--cl-gray-700);

  --cl-shadow-xs:  0 1px 2px rgba(0,0,0,0.3);
  --cl-shadow-sm:  0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
  --cl-shadow-md:  0 4px 8px -2px rgba(0,0,0,0.5), 0 2px 4px -2px rgba(0,0,0,0.3);
}
```

### 4.2 Tipografía

| Rol | Font | Peso | Tamaño | Uso |
|-----|------|------|--------|-----|
| Display | Inter | 700 | 36px | Títulos principales de sección |
| Heading 1 | Inter | 600 | 30px | Títulos de página |
| Heading 2 | Inter | 600 | 24px | Subtítulos, nombres de card |
| Heading 3 | Inter | 600 | 20px | Encabezados de grupo |
| Body | Inter | 400 | 16px | Texto general |
| Body Small | Inter | 400 | 14px | Tablas, metadata |
| Caption | Inter | 500 | 12px | Labels, badges, timestamps |
| KDS Large | Inter | 700 | 56px | Números de orden en cocina |
| KDS Item | Inter | 600 | 28px | Items de orden en cocina |
| Mono | JetBrains Mono | 400 | 14px | Precios, códigos, tickets |

### 4.3 Iconografía

**Reemplazar:** Emojis y Font Awesome (no cargado) por **Lucide Icons** (SVG, tree-shakeable, MIT license).

```html
<!-- CDN: 1 línea en base.html -->
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
<!-- Uso: -->
<i data-lucide="shopping-cart" class="icon-sm"></i>
<i data-lucide="users" class="icon-md"></i>
```

| Tamaño | Clase | px | Uso |
|--------|-------|----|-----|
| Extra Small | `.icon-xs` | 14px | Inline con texto small |
| Small | `.icon-sm` | 16px | Botones, badges |
| Medium | `.icon-md` | 20px | Navegación, cards |
| Large | `.icon-lg` | 24px | Headers, KPIs |
| XL | `.icon-xl` | 32px | Dashboard KPIs |

---

## 5. Arquitectura de Componentes

### 5.1 Macros Jinja2 Reutilizables

Crear `backend/templates/components/` con macros compartidos:

```
backend/templates/components/
├── _kpi_card.html           # KPI con ícono, valor, tendencia, color
├── _data_table.html         # Tabla con search, sort, pagination
├── _empty_state.html        # Estado vacío con ícono y CTA
├── _page_header.html        # Header de página con breadcrumb y acciones
├── _sidebar.html            # Sidebar admin colapsable
├── _topbar.html             # Barra superior operaciones
├── _modal.html              # Modal estandarizado
├── _form_group.html         # Grupo de form con label, input, error
├── _badge.html              # Badge semántico
├── _toast.html              # Toast notification
├── _pagination.html         # Paginador
├── _search_filter.html      # Barra de búsqueda + filtros
├── _product_tile.html       # Tile de producto clickeable
├── _order_summary.html      # Panel de resumen de orden
└── _skeleton.html           # Skeleton loader configurab
```

**Ejemplo — Macro KPI Card:**

```jinja2
{# components/_kpi_card.html #}
{% macro kpi_card(title, value, icon, color="primary", trend=None, trend_up=True, prefix="", suffix="") %}
<div class="cl-kpi-card cl-kpi-card--{{ color }}">
  <div class="cl-kpi-card__header">
    <span class="cl-kpi-card__icon">
      <i data-lucide="{{ icon }}" class="icon-lg"></i>
    </span>
    <span class="cl-kpi-card__title">{{ title }}</span>
  </div>
  <div class="cl-kpi-card__value">
    {% if prefix %}<span class="cl-kpi-card__prefix">{{ prefix }}</span>{% endif %}
    <span data-kpi="{{ title|lower|replace(' ','-') }}">{{ value }}</span>
    {% if suffix %}<span class="cl-kpi-card__suffix">{{ suffix }}</span>{% endif %}
  </div>
  {% if trend is not none %}
  <div class="cl-kpi-card__trend cl-kpi-card__trend--{{ 'up' if trend_up else 'down' }}">
    <i data-lucide="{{ 'trending-up' if trend_up else 'trending-down' }}" class="icon-xs"></i>
    <span>{{ trend }}</span>
  </div>
  {% endif %}
</div>
{% endmacro %}
```

**Ejemplo — Macro Data Table:**

```jinja2
{# components/_data_table.html #}
{% macro data_table(id, columns, searchable=True, filterable=True, paginated=True, 
                     empty_icon="inbox", empty_text="Sin registros", empty_cta=None) %}
<div class="cl-table-container" id="{{ id }}-container">
  {% if searchable or filterable %}
  <div class="cl-table-toolbar">
    {% if searchable %}
    <div class="cl-search">
      <i data-lucide="search" class="icon-sm cl-search__icon"></i>
      <input type="search" class="cl-search__input" placeholder="Buscar..." 
             data-table-search="{{ id }}" aria-label="Buscar en tabla">
    </div>
    {% endif %}
    {% if filterable %}
    <div class="cl-filters" data-table-filters="{{ id }}">
      {{ caller() if caller }}
    </div>
    {% endif %}
  </div>
  {% endif %}
  
  <div class="table-responsive">
    <table class="cl-table" id="{{ id }}" aria-label="{{ id|replace('-',' ')|title }}">
      <thead>
        <tr>
          {% for col in columns %}
          <th scope="col" {% if col.sortable %}class="cl-table__sortable" data-sort="{{ col.key }}"{% endif %}>
            {{ col.label }}
            {% if col.sortable %}<i data-lucide="chevrons-up-down" class="icon-xs"></i>{% endif %}
          </th>
          {% endfor %}
        </tr>
      </thead>
      <tbody>
        {% block table_body %}{% endblock %}
      </tbody>
    </table>
  </div>
  
  <!-- Empty state (hidden by default, shown via JS when 0 rows) -->
  <div class="cl-empty-state d-none" id="{{ id }}-empty">
    <i data-lucide="{{ empty_icon }}" class="cl-empty-state__icon"></i>
    <p class="cl-empty-state__text">{{ empty_text }}</p>
    {% if empty_cta %}
    <a href="{{ empty_cta.href }}" class="btn cl-btn cl-btn--primary">{{ empty_cta.text }}</a>
    {% endif %}
  </div>
  
  {% if paginated %}
  <div class="cl-pagination" data-table-pagination="{{ id }}">
    <!-- Rendered by JS -->
  </div>
  {% endif %}
</div>
{% endmacro %}
```

### 5.2 Layouts Base

**Crear 3 layouts base:**

#### Layout 1: `_layout_admin.html` — Back-office con sidebar

```
┌──────────────────────────────────────────────────┐
│ Topbar: Logo │ Breadcrumb │ Sucursal │ User │ 🌙 │
├────────┬─────────────────────────────────────────┤
│ Side-  │ Page Header: Title + Actions            │
│ bar    │─────────────────────────────────────────│
│        │                                         │
│ 📊     │ Content Area                            │
│ 👥     │ (Tablas, Forms, Dashboards)             │
│ 🍽     │                                         │
│ 📦     │                                         │
│ …      │                                         │
│        │                                         │
│ ◀      │                                         │
└────────┴─────────────────────────────────────────┘
```

**Páginas que usan este layout:**
- Dashboard admin
- Usuarios, Productos, Mesas (CRUD)
- Inventario, Clientes, Reservaciones
- Reportes, Facturación, Corte de Caja
- Delivery, Sucursales, Auditoría

#### Layout 2: `_layout_operations.html` — Operaciones con topbar

```
┌──────────────────────────────────────────────────┐
│ Logo │ Meseros │ Mapa │ Historial │ User │ 🌙    │
├──────────────────────────────────────────────────┤
│                                                  │
│ Content Area (full-width)                        │
│ (Dashboard mesero, Mapa mesas, Detalle orden)    │
│                                                  │
└──────────────────────────────────────────────────┘
```

**Páginas que usan este layout:**
- Meseros dashboard
- Mapa de mesas
- Detalle de orden (split-panel)
- Seleccionar mesa
- Historial del día

#### Layout 3: `_layout_kds.html` — Kitchen Display System

```
┌──────────────────────────────────────────────────┐
│ Estación: TAQUEROS │ Pendientes: 8 │ ⏱ 00:00    │
├──────────────────────────────────────────────────┤
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐            │
│ │ Ord  │ │ Ord  │ │ Ord  │ │ Ord  │            │
│ │ #42  │ │ #43  │ │ #44  │ │ #45  │            │
│ │ 🟢   │ │ 🟡   │ │ 🟠   │ │ 🔴   │            │
│ │ 2min │ │ 5min │ │ 8min │ │ 12m  │            │
│ │      │ │      │ │      │ │      │            │
│ │ [✓]  │ │ [✓]  │ │ [✓]  │ │ [✓]  │            │
│ └──────┘ └──────┘ └──────┘ └──────┘            │
└──────────────────────────────────────────────────┘
```

**Páginas que usan este layout:**
- Taqueros, Comal, Bebidas

#### Layout 4: `_layout_auth.html` — Login/Auth

```
┌──────────────────────────────────────────────────┐
│              ┌──────────────┐                    │
│              │  🦁 LOGO     │                    │
│              │              │                    │
│              │ Email        │                    │
│              │ [__________] │                    │
│              │ Contraseña   │                    │
│              │ [__________] │                    │
│              │ [Entrar]     │                    │
│              └──────────────┘                    │
│                                                  │
│ © CasaLeones 2026                                │
└──────────────────────────────────────────────────┘
```

---

## 6. Especificaciones por Pantalla

### 6.1 Login (Prioridad: Alta)

**Estado actual:** Card centrada, funcional pero con inputs `form-control-sm` pequeños.

**Rediseño:**
- [ ] Fondo con gradiente sutil (rojo oscuro → negro) o imagen blurred del restaurante
- [ ] Card con `backdrop-filter: blur(16px)` y borde sutil
- [ ] Logo animado (fade-in al cargar)
- [ ] Inputs tamaño full (`form-control-lg` con padding 12px 16px)
- [ ] Botón "Entrar" full-width, height 48px, con loading spinner al enviar
- [ ] Toggle "mostrar contraseña" (ojo)
- [ ] Flash messages con toast animado en vez de alert estático
- [ ] Footer con versión app y copyright
- [ ] Auto-focus en campo email

### 6.2 Dashboard Admin (Prioridad: Alta)

**Estado actual:** 8 KPI cards con emojis, 2 charts, skeleton loading. Rating 4/5.

**Rediseño:**
- [ ] Migrar emojis → Lucide icons
- [ ] KPI cards con trend indicator (↑12% vs ayer) y sparkline miniatura
- [ ] Gráfica principal: área con relleno gradiente (no solo línea)
- [ ] Grid CSS en vez de Bootstrap row/col para KPIs
- [ ] Botón "Actualizar" manual + indicador auto-refresh mejorado
- [ ] Empty states con ilustración SVG para alertas stock y actividad
- [ ] Activity feed con avatar placeholder por usuario
- [ ] Período seleccionable: Hoy / 7 días / 30 días / Custom

### 6.3 Detalle de Orden — Split Panel (Prioridad: Crítica)

**Estado actual:** Tabs de categoría + grid de productos + dropdown de carrito. Rating 3/5.

**Rediseño mayor — adoptar patrón Toast POS:**
- [x] **Layout split-panel:** 60% productos (izquierda) + 40% carrito (derecha, sticky) ✅ Sprint 9
- [x] **Buscador de productos** en la parte superior del panel izquierdo ✅ Sprint 9
- [x] **Category pills** horizontal scrollable (en vez de tabs con scroll overflow) ✅ Sprint 9
- [x] **Product tiles** mejorados: nombre, precio, animación bounce al agregar ✅ Sprint 9
- [x] **Panel carrito** sticky con: Header Mesa/Para llevar, items +/-, notas, Subtotal/IVA/Total, botones Enviar a Cocina (verde) + Cobrar (dorado) ✅ Sprint 9
- [x] **Eliminar `me-5`** del container actual ✅ Sprint 9
- [x] **"Enviar a Cocina"** cambiar de `btn-danger` (rojo) a `btn-success` (verde) ✅ Sprint 9
- [x] Keyboard shortcuts: `/` para buscar, `Esc` para cerrar modales ✅ Sprint 9
- [x] Mobile: carrito colapsa a bottom sheet (FAB toggle) ✅ Sprint 9

### 6.4 Seleccionar Mesa (Prioridad: Alta)

**Estado actual:** Grid de botones verdes sin estado de mesa. Rating 2/5.

**Rediseño:**
- [x] **Color-coded grid** con estados visuales por mesa ✅ Sprint 9 (mapa link en operations tab)
- [x] Cada mesa muestra: número, capacidad, estado con color semántico ✅ Sprint 9
- [x] Colores: verde (disponible), rojo (ocupada), amarillo (reservada), gris (mantenimiento) ✅ Sprint 9
- [x] Mesas ocupadas muestran orden activa (#ID badge) ✅ Sprint 9
- [x] Click mesa disponible → crear orden directamente (form POST) ✅ Sprint 9
- [x] Click mesa ocupada → ir a orden activa (link to detalle) ✅ Sprint 9
- [x] Mesas no-disponibles deshabilitadas (cursor: not-allowed, opacity reducida) ✅ Sprint 9
- [x] Grid responsivo (col-6/sm-4/md-3/lg-2) para mobile ✅ Sprint 9
- [x] Filtro por zona con pills ✅ Sprint 9

### 6.5 Pago / Cobro (Prioridad: Crítica — Tiene bugs)

**Estado actual:** Template roto (Jinja2 nesting), sin CSRF, solo efectivo. Rating 1.5/5.

**Rediseño completo:**
- [x] **Arreglar bugs:** Jinja2 blocks, CSRF token — reescritura completa ✅ Sprint 9
- [x] **Página dedicada** con layout split: resumen (izq) + métodos (der) ✅ Sprint 9
- [x] **Selector de método de pago:** Efectivo / Tarjeta / Transferencia (visual cards) ✅ Sprint 9
- [x] **Efectivo:** Botones rápidos ($100, $200, $500, $1000, Exacto), cálculo de cambio en vivo ✅ Sprint 9
- [x] **Multi-pago:** Dividir entre métodos, pagos previos visibles ✅ Sprint 9
- [x] **Propina:** Botones 0%, 10%, 15%, 20% + monto custom ✅ Sprint 9
- [ ] **Split de cuenta:** Dividir equitativamente o seleccionar items por comensal (pendiente Sprint 11)
- [x] **Descuento:** Disponible via cobro modal en meseros dashboard (admin auth) ✅ existente
- [x] Botón "Confirmar Pago" grande (64px height), color dorado, con loading state ✅ Sprint 9
- [x] Animación de éxito: checkmark scale-in + auto-redirect 2s ✅ Sprint 9
- [x] Ruta dedicada: `/meseros/ordenes/<id>/pago_view` GET ✅ Sprint 9

### 6.6 Meseros Dashboard (Prioridad: Alta)

**Estado actual:** Accordion con órdenes activas. Rating 3.5/5.

**Rediseño:**
- [x] **Cards en grid** en vez de accordion (col-12/sm-6/lg-4/xl-3) ✅ Sprint 9
- [x] Card por orden: Mesa #, tiempo transcurrido, estado (badge), items count ✅ Sprint 9
- [x] Color de borde por urgencia temporal (verde < 10min, amarillo < 20min, rojo > 20min) ✅ Sprint 9
- [x] Header sticky con contadores: Activas / En Cocina / Listas ✅ Sprint 9
- [x] Botón FAB (floating action button) "Nueva Orden" + "Para Llevar" ✅ Sprint 9
- [x] Empty state ilustrado cuando no hay órdenes ✅ Sprint 9
- [x] Socket.IO: animación de nueva orden entrando (slideInRight) ✅ Sprint 9

### 6.7 Kitchen Display System — Taqueros/Comal/Bebidas (Prioridad: Alta)

**Estado actual:** Cards con timer, Socket.IO. Rating 3.5/5.

**Rediseño:**
- [ ] **Dark mode obligatorio** (ya implementado, refinar)
- [ ] **Conveyor layout:** Cards en fila horizontal scrollable con scroll snap
- [ ] **Timer con gradiente de urgencia:**
  - 0-5 min: `#12B76A` (verde)
  - 5-10 min: `#F79009` (amarillo)
  - 10-15 min: `#F04438` (rojo)
  - 15+ min: `#B42318` (rojo oscuro pulsante)
- [ ] **Fuentes grandes:** Número de orden 56px, items 28px, notas 20px
- [ ] **Notas de item:** Fondo amarillo con borde, ícono de atención
- [ ] **Sonido** configurable al llegar nueva orden
- [ ] Botón "Listo" grande (72px height) con confirmación táctil (haptic via API)
- [ ] **Counter prominente** en header: "X órdenes pendientes"
- [ ] Eliminar jQuery — migrar a fetch nativo
- [ ] Animación: nueva orden aparece desde la derecha con deslizamiento

### 6.8 CRUD Admin (Usuarios, Productos, Mesas, Ingredientes, etc.) (Prioridad: Alta)

**Estado actual:** Tablas desnudas sin búsqueda, filtro, paginación. Rating 2/5.

**Rediseño universal con macro `_data_table.html`:**
- [ ] **Page header** con título, breadcrumb, botón acción principal ("+Nuevo")
- [ ] **Barra de herramientas:** Search input + filtros dropdown + export
- [ ] **Tabla mejorada:**
  - Checkbox para selección múltiple
  - Columnas sorteables (click header)
  - Hover effect en filas
  - Acciones en columna derecha con dropdown (•••) en vez de botones inline
  - Badge de estado con color semántico
- [ ] **Paginación:** 20 registros por página, selector de tamaño (10/20/50)
- [ ] **Empty state** con ícono + mensaje + CTA
- [ ] **Confirmación de eliminación** con modal (no `confirm()`)
- [ ] **Bulk actions:** Eliminar seleccionados, cambiar estado, exportar
- [ ] **Responsive:** En mobile, tabla se transforma en lista de cards

**Específico por módulo:**

| Módulo | Filtros | Columnas extras necesarias |
|--------|---------|---------------------------|
| Usuarios | Rol, Sucursal | Último login, Estado activo |
| Productos | Categoría, Estación, Rango precio | Imagen thumb, Stock status |
| Mesas | Zona, Estado, Capacidad | Estado actual, Mesero asignado |
| Ingredientes | Categoría, Stock (bajo/ok) | Barra de stock visual |
| Clientes | Visitas (rango), Total gastado | Última visita, Facturas |
| Facturas | Estado, Método pago, Rango fecha | Acciones contextuales |
| Reservaciones | Estado, Fecha, Zona | — |

### 6.9 Forms Admin (Prioridad: Media)

**Estado actual:** Forms full-width sin validación visual. Rating 2.5/5.

**Rediseño:**
- [ ] Max-width 640px centrado (ya implementado en inventario — estandarizar)
- [ ] **Grouped sections** con `<fieldset>` y títulos
- [ ] **Inline validation** en blur (no solo submit):
  - Borde rojo + mensaje de error debajo del input
  - Borde verde cuando correcto
  - Icono ✓/✗ dentro del input
- [ ] **Password field** con strength meter visual (ya hay policy, falta feedback)
- [ ] **Select dropdowns** en vez de IDs numéricos (producto_form)
- [ ] **Textarea** con character count
- [ ] Touch targets: inputs min 44px height

### 6.10 Reportes (Prioridad: Baja — ya están bien)

**Estado actual:** Patrón consistente con charts, toggle, export. Rating 4/5.

**Mejoras incrementales:**
- [ ] Cargar Lucide icons en vez de Font Awesome (arregla íconos invisibles)
- [ ] Sparklines en KPI cards
- [ ] Daterange picker mejorado (no solo 2 inputs date)
- [ ] Print-friendly CSS para reportes
- [ ] Dark mode en charts (ya funciona pero colores de ejes no se ajustan)

---

## 7. Arquitectura CSS

### 7.1 Estructura de Archivos

```
backend/static/css/
├── tokens.css              # Design tokens (variables)
├── base.css                # Reset, tipografía, utilities básicas
├── components/
│   ├── buttons.css         # Botones (primario, secundario, ghost, danger)
│   ├── cards.css           # Cards (kpi, product, order, info)
│   ├── tables.css          # Tablas enterprise
│   ├── forms.css           # Inputs, selects, checkboxes
│   ├── modals.css          # Modales
│   ├── badges.css          # Badges semánticos
│   ├── toasts.css          # Notificaciones toast
│   ├── pagination.css      # Paginador
│   ├── sidebar.css         # Sidebar admin
│   ├── topbar.css          # Barra superior
│   ├── empty-states.css    # Estados vacíos
│   └── skeleton.css        # Skeleton loaders
├── layouts/
│   ├── admin.css           # Layout sidebar
│   ├── operations.css      # Layout operaciones
│   ├── kds.css             # Layout cocina
│   └── auth.css            # Layout login
├── pages/
│   ├── dashboard.css       # Específico dashboard
│   ├── order-detail.css    # Split panel pedido
│   ├── payment.css         # Flujo de pago
│   └── floor-plan.css      # Mapa de mesas
├── vendors/
│   └── chart-theme.css     # Override Chart.js
└── dark-mode.css           # Override dark (migrar a data-bs-theme)
```

### 7.2 Migración Dark Mode

**Actual:** `[data-theme="dark"]` custom con ~291 líneas de overrides.

**Objetivo:** Bootstrap 5.3 nativo `[data-bs-theme="dark"]` + tokens CSS.

Beneficio: Reducir dark-mode.css de ~291 líneas a ~50 líneas (solo overrides de tokens CasaLeones).

---

## 8. Plan de Implementación

### Sprint 7 — Foundation (Semana 1-2)

| # | Item | Tipo | Prioridad | Est. |
|---|------|------|-----------|------|
| 7.1 | Design tokens CSS (`tokens.css`) | Infra | P0 | 4h |
| 7.2 | Font Inter + Lucide Icons CDN | Infra | P0 | 1h |
| 7.3 | Arreglar bugs P0 (pago.html, Font Awesome, producto_form) | Bugfix | P0 | 3h |
| 7.4 | Macros Jinja2 base: `_kpi_card`, `_page_header`, `_empty_state`, `_badge` | Componente | P0 | 6h |
| 7.5 | Layout `_layout_admin.html` con sidebar | Layout | P0 | 8h |
| 7.6 | Layout `_layout_operations.html` | Layout | P0 | 4h |
| 7.7 | Layout `_layout_kds.html` | Layout | P0 | 3h |
| 7.8 | Layout `_layout_auth.html` + Login redesign | Layout | P1 | 4h |

**Entregable Sprint 7:** Fundación del design system lista, 4 layouts, bugs P0 corregidos.

### Sprint 8 — Core CRUD & Navigation (Semana 3-4)

| # | Item | Tipo | Prioridad | Est. |
|---|------|------|-----------|------|
| 8.1 | Macro `_data_table.html` con search, sort, pagination | Componente | P0 | 8h |
| 8.2 | Macro `_form_group.html` con validación inline | Componente | P0 | 4h |
| 8.3 | Sidebar admin: navegación completa con iconos, grupos, colapsable | Componente | P0 | 6h |
| 8.4 | Migrar Usuarios CRUD al nuevo sistema | Migración | P0 | 4h |
| 8.5 | Migrar Productos CRUD (arreglar select dropdowns) | Migración | P0 | 4h |
| 8.6 | Migrar Mesas CRUD (agregar columnas faltantes) | Migración | P1 | 3h |
| 8.7 | Migrar Ingredientes, Clientes, Reservaciones, Sucursales CRUD | Migración | P1 | 8h |
| 8.8 | Modal de confirmación reutilizable (reemplazar `confirm()`) | Componente | P1 | 2h |

**Entregable Sprint 8:** Toda la sección admin con nueva UI enterprise.

### Sprint 9 — Operations Redesign (Semana 5-6) ✅ COMPLETADO

| # | Item | Tipo | Prioridad | Est. | Estado |
|---|------|------|-----------|------|--------|
| 9.1 | Detalle de Orden: split-panel layout | Feature | P0 | 10h | ✅ |
| 9.2 | Product tile mejorado con search, animaciones | Componente | P0 | 4h | ✅ |
| 9.3 | Cart panel sticky con subtotal/IVA/total | Componente | P0 | 6h | ✅ |
| 9.4 | Seleccionar Mesa: color-coded grid + estados + zonas | Feature | P0 | 6h | ✅ |
| 9.5 | Meseros Dashboard: cards grid + urgency borders | Feature | P1 | 6h | ✅ |
| 9.6 | Pago redesign completo (multi-pago, propinas, quick cash) | Feature | P0 | 10h | ✅ |
| 9.7 | Historial del día: route + export CSV + operations layout | Bugfix | P2 | 3h | ✅ |

**Entregable Sprint 9:** Flujo completo de operaciones rediseñado. ✅

**Archivos modificados Sprint 9:**
- `meseros.py` — nuevas rutas: `historial_dia`, `historial_csv`, `pago_view`; `seleccionar_mesa` mejorada con `mesa_order_map`/`zonas`; `view_meseros` con `now_utc`
- `meseros.html` — reescritura completa: accordion → cards grid con urgencia visual
- `seleccionar_mesa.html` — reescritura completa: botones verdes → grid color-coded por estado
- `detalle_orden.html` — reescritura completa: tabs+dropdown → split-panel 60/40
- `historial_dia.html` — reescritura completa: operations layout + KPIs + CSV export
- `pago.html` — reescritura completa: broken template → full-page multi-payment
- `meseros.js` — updated: verificarEstadoParaCobro + init loop + badge classes

### Sprint 10 — KDS, Polish & Dark Mode (Semana 7-8) ✅ COMPLETADO

| # | Item | Tipo | Prioridad | Est. | Estado |
|---|------|------|-----------|------|--------|
| 10.1 | KDS rediseño: conveyor layout, urgency gradients | Feature | P0 | 8h | ✅ |
| 10.2 | KDS: eliminar jQuery, migrar a fetch | Refactor | P1 | 4h | ✅ |
| 10.3 | KDS: sonido configurable para nuevas órdenes | Feature | P2 | 3h | ✅ |
| 10.4 | Dashboard admin: trends, sparklines, período selector | Feature | P1 | 6h | ✅ |
| 10.5 | Migrar dark mode a `data-bs-theme` nativo | Refactor | P1 | 6h | ✅ |
| 10.6 | Reportes: cargar Lucide, daterange picker | Fix | P1 | 4h | ✅ |
| 10.7 | Facturación templates: nueva UI | Migración | P1 | 6h | ✅ |
| 10.8 | Corte de Caja: paginación historial, mejoras visuales | Feature | P2 | 3h | ✅ |

**Entregable Sprint 10:** Cocina enterprise, dark mode nativo, pulido general. ✅

**Archivos modificados Sprint 10:**
- `cocina.py` — STATION_CONFIG dict, DRY helpers (`_get_items`, `_emit_item_listo`), unified `kds_station` route
- `kds_station.html` — unified KDS template with conveyor layout, 4-tier urgency gradients, configurable sound
- `cocina/_kds_cards_fragment.html` — AJAX fragment for KDS cards
- `cocina_timers.js` — rewritten: 4-tier urgency system, fetch API (no jQuery), audio notifications
- `admin/dashboard.html` — period selector pills (Hoy/Ayer/7 días/30 días)
- `admin-dashboard.js` — currentPeriod state, api() appends ?period=, initPeriodSelector()
- `admin_routes.py` — _period_range() helper, 5 endpoints date-filtered, corte_caja pagination (.paginate)
- `base.html` — dual data-bs-theme + data-theme attributes, toggle guard
- `dark-mode.css` — rewritten 291→160 lines, cl-* overrides only
- `reportes/_filtro.html`, `dashboard.html`, `ventas.html`, `productos.html`, `meseros.html`, `pagos.html`, `inventario.html`, `rentabilidad.html`, `delivery.html` — migrated to _layout_admin.html + Lucide + cl-* classes
- `facturacion/lista.html`, `crear.html`, `detalle.html`, `nota_credito.html`, `notas_credito.html`, `complemento_pago.html` — migrated to _layout_admin.html + Lucide + cl-* classes
- `corte_caja.html` — pagination controls for historial table

### Sprint 11 — Accessibility, Animation & QA (Semana 9-10)

| # | Item | Tipo | Prioridad | Est. | Estado |
|---|------|------|-----------|------|--------|
| 11.1 | Auditoría WCAG 2.1 AA completa | QA | P0 | 6h | ✅ |
| 11.2 | Focus management: trap modals, skip nav, visible focus ring | A11y | P0 | 4h | ✅ |
| 11.3 | `aria-live` regions en: KPIs dashboard, timers cocina, toasts, carrito | A11y | P0 | 3h | ✅ |
| 11.4 | Keyboard navigation: floor plan, product tiles, cart, tables | A11y | P1 | 6h | ✅ |
| 11.5 | Animaciones refinadas: page transitions, card hover, loading states | Polish | P2 | 4h | ✅ |
| 11.6 | Print CSS para reportes y tickets | Feature | P2 | 3h | ✅ |
| 11.7 | Performance audit: eliminar CSS/JS no usado, optimizar carga | Perf | P1 | 4h | ✅ |
| 11.8 | Cross-browser testing (Chrome, Safari, Firefox) + tablet testing | QA | P0 | 6h | ✅ |

**Entregable Sprint 11:** App WCAG AA compliant, animaciones pulidas, lista para producción. ✅

**Archivos modificados Sprint 11:**
- `_layout_admin.html` — skip-to-content, aria-current on sidebar, `<main>` landmark, focus trap mobile sidebar, toast pause 5s
- `_layout_operations.html` — skip-to-content, aria-current on tabs, toast pause 5s
- `_layout_kds.html` — skip-to-content, `<main>` with aria-live, role=status stats, overflow-y:auto, prefers-reduced-motion
- `tokens.css` — global `*:focus-visible` red-500, forced-colors fallback, skip-to-content styles, `@media print` (full layout + tables + pago ticket), `@media (prefers-reduced-motion: reduce)`
- `dark-mode.css` — removed focus ring (consolidated to tokens.css), removed skip-to-content (moved to tokens.css), fixed syntax error
- `styles.css` — removed redundant Bootstrap utilities (.m-*, .p-*, .d-flex, .hidden), added prefers-reduced-motion
- `tablet.css` — iOS touch-action:manipulation, -webkit-touch-callout:none, -webkit-tap-highlight-color
- `_modal.html` — aria-describedby, role=dialog, aria-label on cancel
- `_toast.html` — aria-live=polite, 5s auto-dismiss with pause on hover/focus
- `_data_table.html` — sortable headers: tabindex, role=columnheader, aria-sort, keyboard activation
- `dashboard.html` — KPI grid aria-live=polite, role=region
- `detalle_orden.html` — cart panel aria-live, keyboard activation for product tiles
- `base.html` — removed ghost script refs (bebidas/taqueros/comal.js), pinned Lucide to 0.263.1
- `taqueros.html` — socket.io.js → socket.io.min.js
- Deleted: `base.css` (orphan 177 lines), `estaciones.js` (orphan 54 lines)

---

## 9. Métricas de Éxito

### Cuantitativas

| Métrica | Actual | Objetivo v6.0 |
|---------|--------|----------------|
| Lighthouse Performance | ~65 | >85 |
| Lighthouse Accessibility | ~55 | >90 |
| Lighthouse Best Practices | ~70 | >90 |
| First Contentful Paint | ~2.5s | <1.5s |
| CSS total (gzipped) | ~45 KB | <35 KB |
| JS total (gzipped) | ~80 KB | <60 KB (eliminar jQuery) |
| Templates con paginación | 0/15 | 15/15 |
| Templates con empty state | 3/30 | 30/30 |
| Templates con search/filter | 0/12 CRUD | 12/12 |
| Touch targets ≥48px | ~60% | 100% |
| WCAG 2.1 AA compliance | ~40% | 95%+ |

### Cualitativas

- Admin: Encontrar un usuario toma < 5 segundos (vs scroll actual)
- Mesero: Crear orden completa en < 30 segundos (incluyendo agregar items)
- Cocina: Identificar orden urgente en < 2 segundos a 1.5m de distancia
- Pago: Completar cobro multi-método en < 15 segundos
- Todos los flujos tienen feedback visual positivo (loading → success/error)

---

## 10. Restricciones Técnicas

| Restricción | Razón | Mitigación |
|-------------|-------|------------|
| Sin framework JS (React/Vue) | Stack Jinja2 establecido, cero apetito de migración | Macros Jinja2 + vanilla JS modular |
| Bootstrap 5.3 obligatorio | Base CSS del proyecto | Extender con CSS custom, no reemplazar |
| Sin build step (Webpack/Vite) | Simplicidad de deploy Docker | CDN para libs externas, CSS/JS raw |
| Python 3.12 + Flask | Backend estable | Solo cambios frontend |
| PostgreSQL + Redis | Infra establecida | Sin impacto en UI redesign |

---

## 11. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Regresiones visuales en temas existentes | Alta | Alto | Tests visuales por página antes/después |
| Dark mode breaks con nuevo design system | Media | Alto | Implementar tokens dark mode desde Sprint 7 |
| Performance degrada con más CSS | Baja | Medio | Monitor bundle size, eliminar código muerto |
| Templates Jinja2 se vuelven complejos con macros | Media | Medio | Documentar macros, limitar anidamiento a 2 niveles |
| Scope creep (agregar features durante redesign) | Alta | Alto | PRD aprobado = scope congelado. Features nuevas van a v7 |

---

## 12. Fuera de Alcance (v6.0)

Los siguientes items **NO** están incluidos en este redesign:

- [ ] Migración a React/Vue/HTMX
- [ ] Internacionalización (i18n) — la app es solo español
- [ ] Rediseño de backend (API, modelos, lógica)
- [ ] Nuevas features funcionales (solo mejora visual de existentes)
- [ ] Rediseño de logo o branding
- [ ] App nativa iOS/Android
- [ ] Sistema de notificaciones push real
- [ ] Integración con servicios de diseño (Figma export)

---

## 13. Definición de Done

Un sprint se considera completado cuando:

1. ✅ Todos los items del sprint están implementados
2. ✅ No hay errores de consola en ninguna página modificada
3. ✅ Dark mode funciona correctamente en todas las páginas modificadas
4. ✅ Responsive funciona en: mobile (375px), tablet (768px), desktop (1280px+)
5. ✅ Lighthouse Accessibility ≥ 85 para cada página modificada
6. ✅ Touch targets ≥ 48px en todos los elementos interactivos
7. ✅ Sin regresiones en funcionalidad existente
8. ✅ Commit atómico con mensaje descriptivo

---

## Apéndice A: Paleta de Colores Visual

```
PRIMARIOS                  NEUTRALES
┌──────────┐               ┌──────────┐
│ Red 500  │ #C41E3A       │ Gray 50  │ #F9FAFB
│ Red 600  │ #A6192E       │ Gray 100 │ #F2F4F7
│ Red 700  │ #8B1525       │ Gray 300 │ #D0D5DD
└──────────┘               │ Gray 500 │ #667085
                           │ Gray 700 │ #344054
SEMÁNTICOS                 │ Gray 900 │ #101828
┌──────────┐               └──────────┘
│ Success  │ #12B76A
│ Warning  │ #F79009
│ Error    │ #F04438       SURFACE (Light)
│ Info     │ #2E90FA       ┌──────────┐
└──────────┘               │ bg-prim  │ #FFFFFF
                           │ bg-sec   │ #F9FAFB
ACCENT                     │ bg-tert  │ #F2F4F7
┌──────────┐               └──────────┘
│ Gold     │ #C29E59
│ Agave    │ #507C36       SURFACE (Dark)
└──────────┘               ┌──────────┐
                           │ bg-prim  │ #101828
                           │ bg-sec   │ #1D2939
                           │ bg-tert  │ #344054
                           └──────────┘
```

## Apéndice B: Mapa de Navegación Sidebar Admin

```
📊 Dashboard
──────────────
OPERACIONES
  🍽  Órdenes Activas
  🗺  Mapa de Mesas
  📋 Historial del Día
──────────────
CATÁLOGO
  📦 Productos
  🏷  Categorías
  🔧 Estaciones
──────────────
INVENTARIO
  🧪 Ingredientes
  📝 Recetas
  📊 Movimientos
  ⚠️  Alertas Stock
──────────────
VENTAS
  💰 Corte de Caja
  📊 Reportes
    ├─ Ventas
    ├─ Productos
    ├─ Meseros
    ├─ Pagos
    ├─ Inventario
    ├─ Rentabilidad
    └─ Delivery
──────────────
CRM
  👥 Clientes
  📅 Reservaciones
──────────────
FISCAL
  🧾 Facturación
  📄 Notas de Crédito
──────────────
CONFIGURACIÓN
  👤 Usuarios
  🏢 Sucursales
  🚚 Delivery
  📋 Auditoría
```

## Apéndice C: Checklist de Accesibilidad WCAG 2.1 AA

| Criterio | Estado Actual | Requerido v6.0 |
|----------|--------------|----------------|
| 1.1.1 Texto alternativo | Parcial (logo ok, íconos no) | Completo |
| 1.3.1 Info y relaciones | Parcial (forms ok, tablas sin scope) | Completo |
| 1.4.1 Uso del color | Falla (estados solo por color) | Color + texto/ícono |
| 1.4.3 Contraste mínimo (4.5:1) | No verificado | Verificado con tokens |
| 1.4.11 Contraste no-texto (3:1) | No verificado | Verificado |
| 2.1.1 Teclado | Falla (product cards, floor plan) | Completo |
| 2.4.1 Bypass blocks | Parcial (skip-to-content existe) | Completo |
| 2.4.3 Orden de foco | No verificado | Verificado |
| 2.4.7 Foco visible | Parcial (focus-visible existe) | Completo |
| 3.3.1 Identificación de error | Falla (solo flash global) | Inline por campo |
| 3.3.2 Etiquetas/instrucciones | Parcial | Completo |
| 4.1.2 Nombre, rol, valor | Falla (custom widgets sin ARIA) | Completo |
| 4.1.3 Mensajes de estado | Falla (toasts sin aria-live) | `aria-live="polite"` |

---

*Documento generado el 2026-02-15. Próximo paso: aprobación del PRD y inicio de Sprint 7.*
