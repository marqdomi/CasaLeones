# UI/UX Best Practices for Modern Enterprise Restaurant POS Systems

> **Purpose**: Research compilation for CasaLeones POS redesign PRD.  
> **Date**: February 2026  
> **Stack**: Flask + Jinja2 + Bootstrap 5.3 + Chart.js + Socket.IO  
> **Current state audit**: CasaLeones v5.5 — functional but design-inconsistent, CSS duplicated across `base.css`/`styles.css`, no formal design token system, limited typography hierarchy.

---

## Table of Contents

1. [Industry Leader Benchmarking](#1-industry-leader-benchmarking)
2. [Design System Best Practices](#2-design-system-best-practices)
3. [Dashboard Design Patterns](#3-dashboard-design-patterns)
4. [Kitchen Display System (KDS)](#4-kitchen-display-system-kds)
5. [Table & Order Management](#5-table--order-management)
6. [Admin / Back-Office Design](#6-admin--back-office-design)
7. [Modern CSS/Frontend for Jinja2+Bootstrap](#7-modern-cssfrontend-for-jinja2bootstrap)
8. [Accessibility Requirements](#8-accessibility-requirements)
9. [Progressive Web App Patterns](#9-progressive-web-app-patterns)
10. [Animation & Micro-Interactions](#10-animation--micro-interactions)
11. [CasaLeones Gap Analysis & Migration Path](#11-casaleones-gap-analysis--migration-path)

---

## 1. Industry Leader Benchmarking

### 1.1 Toast POS
**What makes it great:**
- **Category-first navigation**: Large colored category pills across the top; products displayed as a grid of large touchable cards (~120×100px) beneath.
- **Split-panel layout**: Left 60–65% for the menu/product grid, right 35–40% for the active order. This two-panel paradigm is now industry-standard.
- **Quick-modifiers**: Tapping a product immediately shows modifier options in a half-sheet modal — no full page navigation.
- **Color-coded order status**: Green (new), yellow (in-progress), red (delayed), gray (completed) — consistent across KDS, server view, and manager view.
- **Smart search**: Fuzzy search bar at the top of the product grid with recent items.
- **Payment flow**: Full-screen takeover with large denomination buttons and running total.

**Key takeaway for CasaLeones**: Adopt the split-panel layout (product grid left, order summary right) for the mesero view.

### 1.2 Square POS
**What makes it great:**
- **Minimalist aesthetic**: White space is generous; maximum 6–8 items visible at once to avoid cognitive overload.
- **Icon-forward design**: Each product tile can have a photo or auto-generated icon. Tiles are ~96×96px with label below.
- **One-tap favorites**: Star to pin frequently ordered items on a "Favorites" tab.
- **Accessible color palette**: High-contrast navy (#00298E) + white. Passes WCAG AAA for text.
- **Unified checkout**: Single flow handles splits, tips, discounts, and multiple payment methods without modal stacking.
- **Smooth animations**: 200ms ease-out transitions on all interactive elements.

**Key takeaway for CasaLeones**: Reduce visual clutter; use generous white space; unify the checkout into a single coherent flow.

### 1.3 Lightspeed Restaurant
**What makes it great:**
- **Floor plan first**: Start screen IS the floor plan. Tables are the primary navigation, not a secondary page.
- **Table state color coding**: Available (green), Occupied with timer (orange/red gradient based on elapsed time), Reserved (blue).
- **Course management**: Visual course separation (appetizer → main → dessert) with drag-and-drop reordering.
- **Multi-screen awareness**: Manager can see all terminals in real time; layout adapts for tablet (landscape) vs phone (portrait).
- **Performance dashboard inline**: Mini sparklines shown directly on the floor plan (revenue today, avg ticket).

**Key takeaway for CasaLeones**: Make the mapa de mesas the default landing page; add time-based color gradient to occupied tables.

### 1.4 Aloha POS (NCR)
**What makes it great:**
- **Enterprise KDS**: The gold standard. Orders displayed as cards in a horizontal conveyor, with automatic bump-bar support and configurable time thresholds (green → yellow at 8 min → red at 15 min).
- **Station routing**: Items automatically route to the correct station (grill, fry, salad) based on modifiers.
- **Recall/priority system**: Special orders get a red flag and move to the left of the conveyor.
- **80pt+ font on KDS**: Category headers at 80pt, item names at 48–60pt, modifiers at 36pt.

**Key takeaway for CasaLeones**: Implement time-gradient coloring and increase KDS font sizes dramatically.

### 1.5 Clover
**What makes it great:**
- **App ecosystem**: Modular approach where each feature (inventory, loyalty, reporting) is a separate "app" with its own icon.
- **Widget-based dashboard**: Drag-and-drop dashboard widgets (today's sales, top items, recent transactions).
- **Quick keys**: Physical + on-screen shortcut buttons for the top 12 items.
- **Receipt customization**: Visual WYSIWYG editor for receipt layouts.

**Key takeaway for CasaLeones**: Widget-based admin dashboard; quick-key grid for high-velocity items.

### 1.6 Revel Systems
**What makes it great:**
- **Enterprise reporting**: Multi-location drill-down reports with comparison views. Sidebar filters that persist across report types.
- **Inventory visual indicators**: Traffic-light badges on products when stock is low. Inline reorder suggestions.
- **Role-based views**: Clean separation — servers see only their tables/orders; managers see the whole floor + metrics.
- **Offline resilience**: Full offline mode with automatic sync indicator in the status bar.

**Key takeaway for CasaLeones**: Persistent filter sidebar in reports; traffic-light badges on inventory items; visible sync status.

### 1.7 TouchBistro
**What makes it great:**
- **Built for iPad**: Every element optimized for touch. No element smaller than 44pt.
- **Swipe gestures**: Swipe left to void, swipe right to mark ready. Long-press for modifiers.
- **Visual bill splitting**: Drag items between split sections visually — not just numerically.
- **Table timeline**: Visual timeline showing how long each course has been at a table.
- **Staff performance**: Photo + name + stats on the server dashboard.

**Key takeaway for CasaLeones**: Consider swipe gestures for mobile; visual bill splitting; table timeline.

### 1.8 Consolidated Industry Patterns

| Pattern | Used By | Priority for CasaLeones |
|---------|---------|------------------------|
| Split-panel (menu + order) | Toast, Square, Lightspeed, TouchBistro | **P0 — Critical** |
| Floor plan as home | Lightspeed, TouchBistro, Aloha | **P0 — Critical** |
| Category pill navigation | Toast, Square, Clover | **P1 — High** |
| Time-gradient order cards (KDS) | Aloha, Toast, Lightspeed | **P0 — Critical** |
| Quick-key favorites | Square, Clover, Toast | **P1 — High** |
| Widget dashboard | Clover, Revel, Toast | **P1 — High** |
| Persistent filter sidebar | Revel, Lightspeed | **P2 — Medium** |
| Swipe gestures | TouchBistro | **P3 — Future** |

---

## 2. Design System Best Practices

### 2.1 Color System

#### 2.1.1 Primary Palette (CasaLeones-specific)

```css
:root {
  /* ── Brand ── */
  --cl-red-50:  #FEF2F3;
  --cl-red-100: #FDE3E5;
  --cl-red-200: #FCCCD0;
  --cl-red-300: #F9A3AB;
  --cl-red-400: #F46D7A;
  --cl-red-500: #E8394D;  /* Primary — evolved from #A6192E for better accessibility */
  --cl-red-600: #D4253A;
  --cl-red-700: #B21D30;  /* Hover state */
  --cl-red-800: #951B2D;
  --cl-red-900: #7E1B2C;
  --cl-red-950: #450A13;

  /* Current brand #A6192E maps closest to --cl-red-800. 
     Recommend lightening primary to --cl-red-500 (#E8394D) 
     for better contrast ratios as a background color. 
     Or keep #A6192E but ONLY on dark/light backgrounds (never as text bg with white). */

  /* ── Neutral ── */
  --cl-gray-0:   #FFFFFF;
  --cl-gray-50:  #FAFAF9;   /* replaces --color-light #FAF3E0 */
  --cl-gray-100: #F5F5F4;
  --cl-gray-200: #E7E5E4;
  --cl-gray-300: #D6D3D1;
  --cl-gray-400: #A8A29E;
  --cl-gray-500: #78716C;
  --cl-gray-600: #57534E;
  --cl-gray-700: #44403C;
  --cl-gray-800: #292524;
  --cl-gray-900: #1C1917;
  --cl-gray-950: #0C0A09;

  /* ── Semantic ── */
  --cl-success-light: #ECFDF5;
  --cl-success:       #10B981;  /* green for available/success */
  --cl-success-dark:  #065F46;

  --cl-warning-light: #FFFBEB;
  --cl-warning:       #F59E0B;  /* amber for in-progress/caution */
  --cl-warning-dark:  #92400E;

  --cl-danger-light:  #FEF2F2;
  --cl-danger:        #EF4444;  /* red for errors/urgent */
  --cl-danger-dark:   #991B1B;

  --cl-info-light:    #EFF6FF;
  --cl-info:          #3B82F6;  /* blue for informational */
  --cl-info-dark:     #1E40AF;

  /* ── Kitchen status (time-based) ── */
  --cl-kds-fresh:    #22C55E;  /* 0–5 min: green */
  --cl-kds-normal:   #84CC16;  /* 5–10 min: yellow-green */
  --cl-kds-aging:    #EAB308;  /* 10–15 min: yellow */
  --cl-kds-warning:  #F97316;  /* 15–20 min: orange */
  --cl-kds-critical: #EF4444;  /* 20+ min: red */
  --cl-kds-overdue:  #DC2626;  /* 25+ min: dark red + pulse */

  /* ── Table states ── */
  --cl-mesa-disponible:   #22C55E;
  --cl-mesa-ocupada:      #EF4444;
  --cl-mesa-reservada:    #3B82F6;
  --cl-mesa-mantenimiento:#6B7280;
}
```

#### 2.1.2 Dark Mode Palette

```css
[data-bs-theme="dark"] {
  --cl-bg-body:     #0C0A09;
  --cl-bg-surface:  #1C1917;
  --cl-bg-elevated: #292524;
  --cl-bg-overlay:  #44403C;
  --cl-text-primary:   #FAFAF9;
  --cl-text-secondary: #A8A29E;
  --cl-text-muted:     #78716C;
  --cl-border:         #44403C;

  /* Semantic colors shift slightly for dark backgrounds */
  --cl-success: #34D399;
  --cl-warning: #FBBF24;
  --cl-danger:  #F87171;
  --cl-info:    #60A5FA;
}
```

#### 2.1.3 Contrast Ratios (WCAG 2.1 AA)

| Combination | Ratio | Passes AA? | Passes AAA? |
|-------------|-------|-----------|-------------|
| `#A6192E` on `#FFFFFF` | 7.2:1 | ✅ | ✅ |
| `#A6192E` on `#FAF3E0` | 6.4:1 | ✅ | ❌ |
| `#FFFFFF` on `#A6192E` | 7.2:1 | ✅ | ✅ |
| `#FFFFFF` on `#E8394D` | 3.6:1 | ❌ (large text only) | ❌ |
| `#1C1917` on `#FAFAF9` | 17.4:1 | ✅ | ✅ |
| `#A8A29E` on `#1C1917` | 6.1:1 | ✅ | ❌ |
| `#F0F0F0` on `#333333` | 10.3:1 | ✅ | ✅ |

**Recommendation**: Keep `#A6192E` as the brand color. Use it for accents, buttons, and borders — **not** as a background with white text for small type (14px or smaller). For backgrounds needing white text, darken to `#8A1325` (11.3:1 ratio).

### 2.2 Typography

#### 2.2.1 Font Stack

```css
:root {
  /* Primary — Inter is the modern standard for UI. 
     Available via Google Fonts CDN or self-hosted. */
  --cl-font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
                  Roboto, Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', 
                  Arial, sans-serif;

  /* Monospace — for tickets, kitchen orders, prices */
  --cl-font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', 
                  'Fira Code', 'Consolas', monospace;

  /* Display — optional, for logo/brand headers only */
  --cl-font-display: 'DM Serif Display', 'Playfair Display', Georgia, serif;
}
```

**Why Inter?**
- Designed specifically for screens at small sizes
- Open-source, no licensing cost
- Tabular numbers feature (`font-variant-numeric: tabular-nums`) — critical for POS price alignment
- Variable font support (single file, all weights)
- Excellent Latin Extended coverage (Spanish accents ñ, á, é, í, ó, ú)

#### 2.2.2 Type Scale (Major Third — 1.250 ratio)

```css
:root {
  /* ── Type scale ── */
  --cl-text-xs:   0.75rem;   /* 12px — labels, captions */
  --cl-text-sm:   0.875rem;  /* 14px — secondary text, table cells */
  --cl-text-base: 1rem;      /* 16px — body text */
  --cl-text-md:   1.125rem;  /* 18px — emphasized body */
  --cl-text-lg:   1.25rem;   /* 20px — card headers */
  --cl-text-xl:   1.5rem;    /* 24px — section headers */
  --cl-text-2xl:  1.875rem;  /* 30px — page titles */
  --cl-text-3xl:  2.25rem;   /* 36px — KPI values */
  --cl-text-4xl:  3rem;      /* 48px — KDS items */
  --cl-text-5xl:  3.75rem;   /* 60px — KDS category headers */

  /* ── Font weights ── */
  --cl-font-regular:  400;
  --cl-font-medium:   500;
  --cl-font-semibold: 600;
  --cl-font-bold:     700;

  /* ── Line heights ── */
  --cl-leading-tight:  1.25;
  --cl-leading-normal: 1.5;
  --cl-leading-relaxed:1.75;

  /* ── Letter spacing ── */
  --cl-tracking-tight: -0.025em;
  --cl-tracking-normal: 0;
  --cl-tracking-wide:   0.025em;
  --cl-tracking-wider:  0.05em;
}
```

#### 2.2.3 Context-Specific Typography

| Context | Size | Weight | Notes |
|---------|------|--------|-------|
| KDS: Category header | 48–60px | 700 | ALL CAPS, `letter-spacing: 0.05em` |
| KDS: Item name | 36–48px | 600 | Sentence case |
| KDS: Modifier/notes | 24–30px | 400 | Italic for special instructions |
| KDS: Timer | 48px | 700 | Monospace, tabular nums |
| Order screen: Product name | 16–18px | 500 | |
| Order screen: Price | 16px | 600 | Monospace, right-aligned |
| Admin table: Cell | 14px | 400 | |
| Admin table: Header | 12–13px | 600 | ALL CAPS, `letter-spacing: 0.05em` |
| KPI card: Value | 30–36px | 700 | Mono for currency |
| KPI card: Label | 12–13px | 500 | Muted color |
| Form: Label | 14px | 500 | |
| Form: Input | 16px | 400 | 16px minimum prevents iOS zoom |
| Button: Default | 14–16px | 600 | |
| Button: Large (POS) | 16–18px | 600 | |

### 2.3 Spacing System (8px Grid)

```css
:root {
  --cl-space-0:  0;
  --cl-space-px: 1px;
  --cl-space-0-5: 0.125rem;  /* 2px */
  --cl-space-1:  0.25rem;    /* 4px */
  --cl-space-1-5: 0.375rem;  /* 6px */
  --cl-space-2:  0.5rem;     /* 8px ← base unit */
  --cl-space-3:  0.75rem;    /* 12px */
  --cl-space-4:  1rem;       /* 16px */
  --cl-space-5:  1.25rem;    /* 20px */
  --cl-space-6:  1.5rem;     /* 24px */
  --cl-space-8:  2rem;       /* 32px */
  --cl-space-10: 2.5rem;     /* 40px */
  --cl-space-12: 3rem;       /* 48px */
  --cl-space-16: 4rem;       /* 64px */
  --cl-space-20: 5rem;       /* 80px */
  --cl-space-24: 6rem;       /* 96px */
}
```

**Spacing rules:**
- **Component internal padding**: `--cl-space-4` (16px) for cards, `--cl-space-3` (12px) for compact cards.
- **Between sibling components**: `--cl-space-4` (16px) minimum, `--cl-space-6` (24px) for section separation.
- **Page margins**: `--cl-space-6` on desktop, `--cl-space-4` on mobile.
- **Form field spacing**: `--cl-space-5` (20px) between fields, `--cl-space-8` (32px) between sections.
- **Touch target padding**: Ensure button padding creates a minimum 48×48px tap area.

### 2.4 Border Radius

```css
:root {
  --cl-radius-none: 0;
  --cl-radius-sm:   0.25rem;   /* 4px — inputs, small badges */
  --cl-radius-md:   0.5rem;    /* 8px — cards, buttons */
  --cl-radius-lg:   0.75rem;   /* 12px — modals, large cards */
  --cl-radius-xl:   1rem;      /* 16px — popovers, sheets */
  --cl-radius-2xl:  1.5rem;    /* 24px — pill buttons */
  --cl-radius-full: 9999px;    /* Circle/pill */
}
```

### 2.5 Shadows (Elevation System)

```css
:root {
  --cl-shadow-xs:  0 1px 2px 0 rgb(0 0 0 / 0.05);
  --cl-shadow-sm:  0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
  --cl-shadow-md:  0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --cl-shadow-lg:  0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --cl-shadow-xl:  0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  --cl-shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);

  /* Colored shadows for status cards */
  --cl-shadow-success: 0 4px 14px 0 rgb(16 185 129 / 0.25);
  --cl-shadow-danger:  0 4px 14px 0 rgb(239 68 68 / 0.25);
  --cl-shadow-warning: 0 4px 14px 0 rgb(245 158 11 / 0.25);
}
```

### 2.6 Component Patterns

#### 2.6.1 Card Component

```html
<!-- Standard Card -->
<div class="cl-card">
  <div class="cl-card__header">
    <h3 class="cl-card__title">Title</h3>
    <span class="cl-badge cl-badge--success">Active</span>
  </div>
  <div class="cl-card__body">
    <!-- Content -->
  </div>
  <div class="cl-card__footer">
    <button class="cl-btn cl-btn--secondary cl-btn--sm">Cancel</button>
    <button class="cl-btn cl-btn--primary cl-btn--sm">Save</button>
  </div>
</div>
```

```css
.cl-card {
  background: var(--cl-gray-0);
  border: 1px solid var(--cl-gray-200);
  border-radius: var(--cl-radius-lg);
  box-shadow: var(--cl-shadow-sm);
  overflow: hidden;
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.cl-card:hover {
  box-shadow: var(--cl-shadow-md);
}
.cl-card--interactive:hover {
  transform: translateY(-2px);
  box-shadow: var(--cl-shadow-lg);
}
.cl-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--cl-space-4) var(--cl-space-4) var(--cl-space-3);
  border-bottom: 1px solid var(--cl-gray-100);
}
.cl-card__body {
  padding: var(--cl-space-4);
}
.cl-card__footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--cl-space-2);
  padding: var(--cl-space-3) var(--cl-space-4);
  border-top: 1px solid var(--cl-gray-100);
  background: var(--cl-gray-50);
}
```

#### 2.6.2 Product Tile (POS Grid)

```html
<button class="cl-product-tile" data-product-id="42">
  <div class="cl-product-tile__image">
    <img src="..." alt="Taco al Pastor" loading="lazy">
    <!-- fallback: colored circle with initials -->
  </div>
  <span class="cl-product-tile__name">Taco al Pastor</span>
  <span class="cl-product-tile__price">$45.00</span>
  <span class="cl-product-tile__badge" aria-label="Low stock">3</span>
</button>
```

```css
.cl-product-tile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--cl-space-1);
  padding: var(--cl-space-3);
  min-height: 100px;
  min-width: 100px;
  background: var(--cl-gray-0);
  border: 2px solid var(--cl-gray-200);
  border-radius: var(--cl-radius-md);
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
  -webkit-tap-highlight-color: transparent;
}
.cl-product-tile:hover {
  border-color: var(--cl-red-500);
  box-shadow: var(--cl-shadow-md);
  transform: translateY(-2px);
}
.cl-product-tile:active {
  transform: scale(0.96);
  box-shadow: var(--cl-shadow-xs);
}
.cl-product-tile__name {
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-medium);
  text-align: center;
  line-height: var(--cl-leading-tight);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.cl-product-tile__price {
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-semibold);
  font-variant-numeric: tabular-nums;
  color: var(--cl-gray-600);
}
```

#### 2.6.3 KPI Card

```html
<div class="cl-kpi" style="--kpi-accent: var(--cl-success)">
  <div class="cl-kpi__icon">
    <svg><!-- icon --></svg>
  </div>
  <div class="cl-kpi__content">
    <span class="cl-kpi__value">$24,580</span>
    <span class="cl-kpi__label">Ventas Hoy</span>
  </div>
  <div class="cl-kpi__trend cl-kpi__trend--up">
    <svg><!-- arrow up --></svg>
    <span>+12.5%</span>
  </div>
</div>
```

```css
.cl-kpi {
  display: flex;
  align-items: center;
  gap: var(--cl-space-4);
  padding: var(--cl-space-5);
  background: var(--cl-gray-0);
  border-radius: var(--cl-radius-lg);
  border-left: 4px solid var(--kpi-accent, var(--cl-gray-300));
  box-shadow: var(--cl-shadow-sm);
}
.cl-kpi__icon {
  width: 48px;
  height: 48px;
  border-radius: var(--cl-radius-md);
  background: color-mix(in srgb, var(--kpi-accent) 10%, transparent);
  display: grid;
  place-items: center;
  color: var(--kpi-accent);
}
.cl-kpi__value {
  font-size: var(--cl-text-3xl);
  font-weight: var(--cl-font-bold);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  display: block;
}
.cl-kpi__label {
  font-size: var(--cl-text-xs);
  font-weight: var(--cl-font-medium);
  color: var(--cl-gray-500);
  text-transform: uppercase;
  letter-spacing: var(--cl-tracking-wider);
}
.cl-kpi__trend {
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-semibold);
  display: flex;
  align-items: center;
  gap: var(--cl-space-1);
}
.cl-kpi__trend--up { color: var(--cl-success); }
.cl-kpi__trend--down { color: var(--cl-danger); }
```

#### 2.6.4 Table Component (Admin)

```css
.cl-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: var(--cl-text-sm);
}
.cl-table thead th {
  font-size: var(--cl-text-xs);
  font-weight: var(--cl-font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--cl-tracking-wider);
  color: var(--cl-gray-500);
  background: var(--cl-gray-50);
  padding: var(--cl-space-3) var(--cl-space-4);
  border-bottom: 2px solid var(--cl-gray-200);
  position: sticky;
  top: 0;
  z-index: 10;
  white-space: nowrap;
}
.cl-table tbody td {
  padding: var(--cl-space-3) var(--cl-space-4);
  border-bottom: 1px solid var(--cl-gray-100);
  vertical-align: middle;
}
.cl-table tbody tr {
  transition: background-color 0.15s ease;
}
.cl-table tbody tr:hover {
  background-color: var(--cl-gray-50);
}

/* Sortable header */
.cl-table th[data-sort] {
  cursor: pointer;
  user-select: none;
}
.cl-table th[data-sort]::after {
  content: '↕';
  margin-left: var(--cl-space-1);
  opacity: 0.3;
}
.cl-table th[data-sort="asc"]::after {
  content: '↑';
  opacity: 1;
}
.cl-table th[data-sort="desc"]::after {
  content: '↓';
  opacity: 1;
}
```

#### 2.6.5 Modal Component

```css
.cl-modal {
  --modal-width: 480px;
}
.cl-modal .modal-content {
  border: none;
  border-radius: var(--cl-radius-xl);
  box-shadow: var(--cl-shadow-2xl);
  overflow: hidden;
}
.cl-modal .modal-header {
  padding: var(--cl-space-5) var(--cl-space-6);
  border-bottom: 1px solid var(--cl-gray-100);
}
.cl-modal .modal-title {
  font-size: var(--cl-text-lg);
  font-weight: var(--cl-font-semibold);
}
.cl-modal .modal-body {
  padding: var(--cl-space-6);
}
.cl-modal .modal-footer {
  padding: var(--cl-space-4) var(--cl-space-6);
  border-top: 1px solid var(--cl-gray-100);
  background: var(--cl-gray-50);
}
/* Full-screen modal on mobile */
@media (max-width: 576px) {
  .cl-modal .modal-dialog {
    margin: 0;
    max-width: 100%;
    min-height: 100vh;
  }
  .cl-modal .modal-content {
    border-radius: 0;
    min-height: 100vh;
  }
}
```

#### 2.6.6 Button System

```css
/* Sizes */
.cl-btn--xs  { padding: 0.25rem 0.5rem; font-size: var(--cl-text-xs); min-height: 28px; }
.cl-btn--sm  { padding: 0.375rem 0.75rem; font-size: var(--cl-text-sm); min-height: 36px; }
.cl-btn--md  { padding: 0.5rem 1rem; font-size: var(--cl-text-base); min-height: 44px; }
.cl-btn--lg  { padding: 0.75rem 1.5rem; font-size: var(--cl-text-md); min-height: 52px; }
.cl-btn--xl  { padding: 1rem 2rem; font-size: var(--cl-text-lg); min-height: 60px; }

/* POS-specific: extra large for touch */
.cl-btn--pos {
  min-height: 56px;
  min-width: 56px;
  font-size: var(--cl-text-md);
  font-weight: var(--cl-font-semibold);
  border-radius: var(--cl-radius-md);
}

/* Variants */
.cl-btn--primary   { background: var(--cl-red-700); color: #fff; }
.cl-btn--secondary { background: var(--cl-gray-100); color: var(--cl-gray-700); border: 1px solid var(--cl-gray-300); }
.cl-btn--success   { background: var(--cl-success); color: #fff; }
.cl-btn--danger    { background: var(--cl-danger); color: #fff; }
.cl-btn--ghost     { background: transparent; color: var(--cl-gray-600); }
.cl-btn--ghost:hover { background: var(--cl-gray-100); }
```

---

## 3. Dashboard Design Patterns

### 3.1 Layout Grid

```css
/* Dashboard grid using CSS Grid */
.cl-dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--cl-space-6);
  padding: var(--cl-space-6);
}

/* KPI row: always 4 columns on desktop */
.cl-dashboard__kpis {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--cl-space-4);
}
@media (max-width: 1024px) {
  .cl-dashboard__kpis {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 576px) {
  .cl-dashboard__kpis {
    grid-template-columns: 1fr;
  }
}

/* Chart panels: 2-column on desktop */
.cl-dashboard__charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--cl-space-6);
}
@media (max-width: 768px) {
  .cl-dashboard__charts {
    grid-template-columns: 1fr;
  }
}
```

### 3.2 KPI Best Practices

1. **Maximum 6–8 KPIs visible** without scrolling. More = cognitive overload.
2. **Order by importance**: Revenue → Orders → Avg Ticket → Tips (left-to-right, top-to-bottom).
3. **Comparison context**: Always show % change vs yesterday/last week. Without comparison, raw numbers are meaningless.
4. **Sparklines**: Embed 7-day sparklines (using Chart.js or inline SVG) inside each KPI card for trend visualization.
5. **Loading states**: Use skeleton screens (shimmer), never spinners, for KPI cards.
6. **Real-time badge**: Show a pulsing green dot + "En vivo" indicator when data auto-refreshes.

```html
<!-- KPI with sparkline and trend -->
<div class="cl-kpi">
  <div class="cl-kpi__content">
    <span class="cl-kpi__label">Ventas Hoy</span>
    <span class="cl-kpi__value">$24,580</span>
    <div class="cl-kpi__meta">
      <span class="cl-kpi__trend cl-kpi__trend--up">↑ 12.5% vs ayer</span>
      <canvas class="cl-kpi__sparkline" width="80" height="32"></canvas>
    </div>
  </div>
</div>
```

### 3.3 Chart Best Practices

| Chart Type | Use Case | CasaLeones Context |
|------------|----------|-------------------|
| Line | Trends over time | Ventas por hora, ventas 7 días |
| Bar (vertical) | Comparison across categories | Ventas por mesero, ventas por hora |
| Bar (horizontal) | Ranked lists | Top 20 productos, mermas por ingrediente |
| Donut | Part-of-whole (max 5 segments) | Métodos de pago, canales de venta |
| Scatter | Correlation | Precio vs margen (rentabilidad) |
| Sparkline | Inline trend | KPI cards, table cells |
| Heatmap | Intensity over 2D | Ventas por hora × día de semana |

**Chart.js configuration best practices:**
```javascript
const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 16,
        font: { family: 'Inter', size: 12 }
      }
    },
    tooltip: {
      backgroundColor: '#1C1917',
      titleFont: { family: 'Inter', size: 13, weight: '600' },
      bodyFont: { family: 'Inter', size: 12 },
      padding: 12,
      cornerRadius: 8,
      displayColors: true,
      callbacks: {
        label: ctx => `${ctx.dataset.label}: $${ctx.parsed.y.toLocaleString('es-MX')}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(0,0,0,0.06)' },
      ticks: {
        font: { family: 'Inter', size: 11 },
        callback: v => `$${v.toLocaleString('es-MX')}`
      }
    },
    x: {
      grid: { display: false },
      ticks: { font: { family: 'Inter', size: 11 } }
    }
  }
};
```

### 3.4 Real-Time Data Display

```css
/* Live indicator */
.cl-live-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--cl-space-1-5);
  font-size: var(--cl-text-xs);
  font-weight: var(--cl-font-medium);
  color: var(--cl-success);
}
.cl-live-badge::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cl-success);
  animation: pulse-live 2s ease infinite;
}
@keyframes pulse-live {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgb(16 185 129 / 0.4); }
  50%      { opacity: 0.8; box-shadow: 0 0 0 6px rgb(16 185 129 / 0); }
}

/* Auto-refresh progress bar */
.cl-refresh-progress {
  height: 2px;
  background: var(--cl-gray-200);
  position: relative;
  overflow: hidden;
}
.cl-refresh-progress::after {
  content: '';
  position: absolute;
  inset: 0;
  background: var(--cl-info);
  animation: refresh-countdown 30s linear infinite;
  transform-origin: left;
}
@keyframes refresh-countdown {
  from { transform: scaleX(1); }
  to   { transform: scaleX(0); }
}
```

### 3.5 Information Hierarchy

**Three-tier layout (top to bottom):**
1. **Tier 1 — Glanceable** (top): KPI cards (revenue, orders, avg ticket, alerts). Viewable from 2m away on a manager's monitor.
2. **Tier 2 — Scannable** (middle): Charts + comparison data. Requires 1m proximity.
3. **Tier 3 — Detailed** (bottom): Tables, lists, recent activity. Requires sitting down and reading.

---

## 4. Kitchen Display System (KDS)

### 4.1 Readability at Distance (1–2 meters)

**Font size minimums for KDS:**
```css
.cl-kds {
  /* Base font for KDS context */
  font-size: 24px;
}
.cl-kds__station-name {
  font-size: 36px;   /* readable at 3m */
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.cl-kds__order-number {
  font-size: 48px;   /* readable at 3m */
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.cl-kds__item-name {
  font-size: 28px;   /* readable at 2m */
  font-weight: 600;
}
.cl-kds__item-qty {
  font-size: 32px;
  font-weight: 700;
  min-width: 48px;
  text-align: center;
}
.cl-kds__modifier {
  font-size: 22px;
  font-weight: 400;
  font-style: italic;
  padding-left: 20px; /* indent modifiers under items */
}
.cl-kds__special-note {
  font-size: 24px;
  font-weight: 700;
  color: var(--cl-danger);
  background: var(--cl-danger-light);
  padding: 8px 12px;
  border-radius: 6px;
  border-left: 4px solid var(--cl-danger);
}
.cl-kds__timer {
  font-family: var(--cl-font-mono);
  font-size: 36px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
```

### 4.2 Color Coding for Time Urgency

```css
/* Time-based card borders and backgrounds */
.cl-kds-card { border-left: 6px solid var(--cl-kds-fresh); }
.cl-kds-card[data-age="normal"]   { border-left-color: var(--cl-kds-normal); }
.cl-kds-card[data-age="aging"]    { border-left-color: var(--cl-kds-aging); }
.cl-kds-card[data-age="warning"]  { border-left-color: var(--cl-kds-warning); background: #FFF7ED; }
.cl-kds-card[data-age="critical"] { border-left-color: var(--cl-kds-critical); background: #FEF2F2; }
.cl-kds-card[data-age="overdue"]  { 
  border-left-color: var(--cl-kds-overdue); 
  background: #FEE2E2;
  animation: kds-pulse 1s ease infinite;
}

@keyframes kds-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgb(220 38 38 / 0.3); }
  50%      { box-shadow: 0 0 0 8px rgb(220 38 38 / 0); }
}
```

**Time thresholds (configurable per restaurant):**

| Time Elapsed | Status | Border Color | Background | Alert |
|-------------|--------|-------------|------------|-------|
| 0–5 min | Fresh | Green `#22C55E` | White | None |
| 5–10 min | Normal | Yellow-Green `#84CC16` | White | None |
| 10–15 min | Aging | Yellow `#EAB308` | White | None |
| 15–20 min | Warning | Orange `#F97316` | Light orange | None |
| 20–25 min | Critical | Red `#EF4444` | Light red | Visual pulse |
| 25+ min | Overdue | Dark Red `#DC2626` | Red bg | Pulse + sound |

### 4.3 Sound/Visual Alerts

```javascript
// KDS alert system
const KDSAlerts = {
  newOrder: {
    sound: '/static/audio/new-order.mp3',     // Short chime, 0.5s
    visual: 'flash-border',                    // Border flash 3 times
    duration: 3000,
  },
  rush: {
    sound: '/static/audio/rush-alert.mp3',     // Urgent double-beep, 1s
    visual: 'full-screen-flash',               // Red flash overlay
    duration: 2000,
  },
  allDay: {
    sound: null,                                // No sound for running counts
    visual: 'badge-update',                     // Badge counter animation
    duration: 500,
  },
};

// Notification permission (PWA)
function requestKDSNotifications() {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }
}
```

### 4.4 KDS Card Layout

```html
<div class="cl-kds-card" data-age="fresh" data-order-id="1234">
  <div class="cl-kds-card__header">
    <span class="cl-kds__order-number">#1234</span>
    <div class="cl-kds-card__meta">
      <span class="cl-kds__mesa">Mesa 5</span>
      <span class="cl-kds__timer">04:32</span>
    </div>
    <span class="cl-badge cl-badge--info">Para llevar</span>
  </div>
  <ul class="cl-kds-card__items">
    <li class="cl-kds__item">
      <span class="cl-kds__item-qty">2×</span>
      <span class="cl-kds__item-name">Taco al Pastor</span>
    </li>
    <li class="cl-kds__modifier">Sin cebolla, extra cilantro</li>
    <li class="cl-kds__item">
      <span class="cl-kds__item-qty">1×</span>
      <span class="cl-kds__item-name">Quesadilla</span>
    </li>
  </ul>
  <button class="cl-btn cl-btn--success cl-btn--pos cl-kds__bump-btn" 
          aria-label="Marcar orden 1234 como lista">
    ✓ LISTO
  </button>
</div>
```

### 4.5 KDS Dark Mode (Default for Kitchen)

```css
/* Kitchen screens default to dark mode */
.cl-kds {
  background: #0C0A09;
  color: #FAFAF9;
}
.cl-kds-card {
  background: #1C1917;
  border-radius: var(--cl-radius-md);
}
.cl-kds-card__header {
  background: #292524;
  padding: 12px 16px;
  border-radius: var(--cl-radius-md) var(--cl-radius-md) 0 0;
}
```

### 4.6 KDS Layout Pattern

```css
/* Horizontal conveyor layout (Aloha-style) */
.cl-kds-conveyor {
  display: flex;
  gap: var(--cl-space-4);
  overflow-x: auto;
  padding: var(--cl-space-4);
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}
.cl-kds-conveyor .cl-kds-card {
  flex: 0 0 320px;
  scroll-snap-align: start;
}

/* Or grid layout for larger screens */
@media (min-width: 1200px) {
  .cl-kds-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: var(--cl-space-4);
    padding: var(--cl-space-4);
  }
}
```

---

## 5. Table & Order Management

### 5.1 Floor Plan Visualization

**Best practices from Lightspeed + TouchBistro:**

```css
/* Floor plan container */
.cl-floorplan {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 10;            /* consistent proportions */
  background: var(--cl-gray-50);
  border: 2px solid var(--cl-gray-200);
  border-radius: var(--cl-radius-lg);
  overflow: hidden;
  touch-action: pan-x pan-y;         /* allow panning but not zoom */
  background-image: 
    radial-gradient(circle, var(--cl-gray-200) 1px, transparent 1px);
  background-size: 24px 24px;        /* dot grid for positioning */
}

/* Table element */
.cl-mesa {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: var(--cl-radius-md);
  font-weight: var(--cl-font-semibold);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

/* Table shapes */
.cl-mesa--square   { width: 80px; height: 80px; border-radius: var(--cl-radius-md); }
.cl-mesa--round    { width: 80px; height: 80px; border-radius: 50%; }
.cl-mesa--rect     { width: 120px; height: 80px; border-radius: var(--cl-radius-md); }
.cl-mesa--long     { width: 180px; height: 60px; border-radius: var(--cl-radius-md); }

/* State colors with subtle gradients */
.cl-mesa--disponible {
  background: linear-gradient(135deg, #22C55E, #16A34A);
  color: white;
  box-shadow: 0 2px 8px rgb(34 197 94 / 0.3);
}
.cl-mesa--ocupada {
  background: linear-gradient(135deg, #EF4444, #DC2626);
  color: white;
  box-shadow: 0 2px 8px rgb(239 68 68 / 0.3);
}
.cl-mesa--reservada {
  background: linear-gradient(135deg, #3B82F6, #2563EB);
  color: white;
  box-shadow: 0 2px 8px rgb(59 130 246 / 0.3);
}
.cl-mesa--mantenimiento {
  background: linear-gradient(135deg, #9CA3AF, #6B7280);
  color: white;
  opacity: 0.7;
}

/* Hover/focus */
.cl-mesa:hover, .cl-mesa:focus-visible {
  transform: scale(1.08);
  box-shadow: 0 4px 16px rgb(0 0 0 / 0.2);
  z-index: 10;
}

/* Timer overlay on occupied tables */
.cl-mesa__timer {
  position: absolute;
  bottom: -8px;
  right: -8px;
  background: var(--cl-gray-900);
  color: white;
  font-size: 11px;
  font-family: var(--cl-font-mono);
  padding: 2px 6px;
  border-radius: var(--cl-radius-full);
  font-variant-numeric: tabular-nums;
}

/* Guest count badge */
.cl-mesa__guests {
  position: absolute;
  top: -6px;
  left: -6px;
  width: 22px;
  height: 22px;
  background: var(--cl-gray-900);
  color: white;
  font-size: 11px;
  font-weight: 700;
  border-radius: 50%;
  display: grid;
  place-items: center;
}
```

### 5.2 Order Flow (User Journey)

**Optimal flow based on industry leaders:**

```
1. SELECT TABLE          → Floor plan (default landing)
   └─ Tap available table → Opens order screen

2. ADD ITEMS             → Split-panel layout
   ├─ Left: Category tabs + product grid
   │   ├─ Category pills (scrollable horizontal)
   │   ├─ Search bar (fuzzy)
   │   ├─ Product tiles (grid 3×4 or 4×4)
   │   └─ Quick-add bar (top 6 items, always visible)
   └─ Right: Order summary (sticky)
       ├─ Table info + timer
       ├─ Items list (editable qty, removable)
       ├─ Running subtotal / IVA / total
       └─ Action buttons: Enviar a cocina, Cobrar

3. SEND TO KITCHEN       → Sends via Socket.IO
   └─ Visual confirmation (green check animation)
   └─ Items appear on KDS in < 1 second

4. PAYMENT               → Full-screen modal or panel
   ├─ Order summary (read-only)
   ├─ Payment method buttons (large, touch-friendly)
   ├─ Split bill option (drag items between tickets)
   ├─ Tip section (0%, 10%, 15%, 20%, custom)
   ├─ Discount (admin PIN required)
   └─ Confirm → Success animation → Print ticket
```

### 5.3 Split-Panel Order Screen

```css
/* Split-panel layout */
.cl-order-layout {
  display: grid;
  grid-template-columns: 1fr 380px;  /* menu | order summary */
  height: calc(100vh - 64px);         /* full height minus navbar */
  overflow: hidden;
}
@media (max-width: 768px) {
  .cl-order-layout {
    grid-template-columns: 1fr;
    height: auto;
  }
}

/* Menu panel */
.cl-order-menu {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.cl-order-menu__categories {
  display: flex;
  gap: var(--cl-space-2);
  padding: var(--cl-space-3) var(--cl-space-4);
  overflow-x: auto;
  scrollbar-width: none;
  border-bottom: 1px solid var(--cl-gray-200);
  flex-shrink: 0;
}
.cl-order-menu__search {
  padding: var(--cl-space-3) var(--cl-space-4);
  border-bottom: 1px solid var(--cl-gray-100);
  flex-shrink: 0;
}
.cl-order-menu__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--cl-space-3);
  padding: var(--cl-space-4);
  overflow-y: auto;
  flex: 1;
}

/* Order summary panel */
.cl-order-summary {
  display: flex;
  flex-direction: column;
  background: var(--cl-gray-50);
  border-left: 1px solid var(--cl-gray-200);
  overflow: hidden;
}
.cl-order-summary__header {
  padding: var(--cl-space-4);
  border-bottom: 1px solid var(--cl-gray-200);
  flex-shrink: 0;
}
.cl-order-summary__items {
  flex: 1;
  overflow-y: auto;
  padding: var(--cl-space-3) var(--cl-space-4);
}
.cl-order-summary__totals {
  padding: var(--cl-space-4);
  border-top: 2px solid var(--cl-gray-300);
  background: var(--cl-gray-0);
  flex-shrink: 0;
}
.cl-order-summary__actions {
  padding: var(--cl-space-3) var(--cl-space-4);
  display: flex;
  gap: var(--cl-space-2);
  flex-shrink: 0;
}
```

### 5.4 Category Pills

```css
.cl-category-pill {
  display: inline-flex;
  align-items: center;
  gap: var(--cl-space-1-5);
  padding: var(--cl-space-2) var(--cl-space-4);
  border-radius: var(--cl-radius-full);
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-medium);
  white-space: nowrap;
  cursor: pointer;
  border: 2px solid var(--cl-gray-200);
  background: var(--cl-gray-0);
  color: var(--cl-gray-600);
  transition: all 0.15s ease;
  -webkit-tap-highlight-color: transparent;
}
.cl-category-pill:hover {
  border-color: var(--cl-red-300);
  color: var(--cl-red-700);
}
.cl-category-pill--active {
  background: var(--cl-red-700);
  border-color: var(--cl-red-700);
  color: white;
}
.cl-category-pill__count {
  background: rgb(255 255 255 / 0.2);
  padding: 0 6px;
  border-radius: var(--cl-radius-full);
  font-size: var(--cl-text-xs);
  font-weight: var(--cl-font-semibold);
}
```

### 5.5 Split Bill UI

```css
/* Visual split bill: two columns with items draggable between */
.cl-split-bill {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: var(--cl-space-4);
  height: 60vh;
}
.cl-split-bill__ticket {
  background: var(--cl-gray-50);
  border: 2px dashed var(--cl-gray-300);
  border-radius: var(--cl-radius-lg);
  padding: var(--cl-space-4);
  overflow-y: auto;
}
.cl-split-bill__ticket--active {
  border-color: var(--cl-info);
  border-style: solid;
  box-shadow: var(--cl-shadow-md);
}
.cl-split-bill__divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--cl-space-2);
}
.cl-split-bill__move-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--cl-gray-200);
  display: grid;
  place-items: center;
  cursor: pointer;
  font-size: 18px;
}
```

### 5.6 Quick-Add Bar

```css
/* Pinned favorites bar at the top of the product grid */
.cl-quick-add {
  display: flex;
  gap: var(--cl-space-2);
  padding: var(--cl-space-2) var(--cl-space-4);
  overflow-x: auto;
  scrollbar-width: none;
  background: var(--cl-gray-100);
  border-bottom: 1px solid var(--cl-gray-200);
}
.cl-quick-add__item {
  flex: 0 0 auto;
  padding: var(--cl-space-2) var(--cl-space-3);
  background: var(--cl-gray-0);
  border: 1px solid var(--cl-gray-300);
  border-radius: var(--cl-radius-md);
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-medium);
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
  min-height: 44px;
  display: flex;
  align-items: center;
}
.cl-quick-add__item:active {
  transform: scale(0.95);
  background: var(--cl-red-50);
}
```

---

## 6. Admin / Back-Office Design

### 6.1 Navigation Pattern: Sidebar

**Recommendation:** Migrate from the current dropdown-based top nav to a **collapsible sidebar** for admin views.

```css
/* Admin sidebar layout */
.cl-admin-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  min-height: 100vh;
}
@media (max-width: 1024px) {
  .cl-admin-layout {
    grid-template-columns: 1fr;
  }
}

.cl-sidebar {
  background: var(--cl-gray-900);
  color: var(--cl-gray-300);
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 50;
}
.cl-sidebar__brand {
  padding: var(--cl-space-5) var(--cl-space-4);
  border-bottom: 1px solid var(--cl-gray-800);
}
.cl-sidebar__nav {
  flex: 1;
  padding: var(--cl-space-3) 0;
}
.cl-sidebar__section {
  padding: var(--cl-space-2) var(--cl-space-4);
}
.cl-sidebar__section-title {
  font-size: var(--cl-text-xs);
  font-weight: var(--cl-font-semibold);
  text-transform: uppercase;
  letter-spacing: var(--cl-tracking-wider);
  color: var(--cl-gray-500);
  margin-bottom: var(--cl-space-2);
}
.cl-sidebar__link {
  display: flex;
  align-items: center;
  gap: var(--cl-space-3);
  padding: var(--cl-space-2) var(--cl-space-4);
  color: var(--cl-gray-400);
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-medium);
  border-radius: var(--cl-radius-md);
  transition: all 0.15s ease;
  text-decoration: none;
}
.cl-sidebar__link:hover {
  background: var(--cl-gray-800);
  color: var(--cl-gray-100);
}
.cl-sidebar__link--active {
  background: var(--cl-red-700);
  color: white;
}

/* Sidebar groupings for CasaLeones */
/*
  OPERACIONES
    ├─ Dashboard
    ├─ Mesas
    ├─ Órdenes Activas
    └─ Corte de Caja
  CATÁLOGOS
    ├─ Productos
    ├─ Ingredientes (Inventario)
    └─ Usuarios
  CLIENTES
    ├─ Directorio
    ├─ Reservaciones
    └─ Facturación
  REPORTES
    ├─ Ventas
    ├─ Productos
    ├─ Meseros
    ├─ Rentabilidad
    ├─ Delivery
    └─ Inventario/Mermas
  CONFIGURACIÓN
    ├─ Sucursales
    ├─ Delivery
    └─ Auditoría
*/
```

### 6.2 CRUD List Page Pattern

```html
<!-- Standard CRUD list page -->
<div class="cl-page">
  <!-- Page header: title + primary action -->
  <div class="cl-page__header">
    <div>
      <nav class="cl-breadcrumbs">
        <a href="/admin">Admin</a> / <span>Productos</span>
      </nav>
      <h1 class="cl-page__title">Productos</h1>
      <p class="cl-page__subtitle">248 productos en total</p>
    </div>
    <div class="cl-page__actions">
      <button class="cl-btn cl-btn--secondary">Exportar CSV</button>
      <button class="cl-btn cl-btn--primary">+ Nuevo Producto</button>
    </div>
  </div>

  <!-- Filters bar -->
  <div class="cl-filters">
    <div class="cl-search">
      <svg class="cl-search__icon"><!-- search icon --></svg>
      <input type="search" class="cl-search__input" 
             placeholder="Buscar por nombre, categoría...">
    </div>
    <div class="cl-filters__group">
      <select class="cl-select">
        <option>Todas las categorías</option>
      </select>
      <select class="cl-select">
        <option>Todos los estados</option>
      </select>
    </div>
    <span class="cl-filters__count">Mostrando 24 de 248</span>
  </div>

  <!-- Bulk actions (shown when items selected) -->
  <div class="cl-bulk-actions" hidden>
    <span>3 seleccionados</span>
    <button class="cl-btn cl-btn--sm cl-btn--ghost">Activar</button>
    <button class="cl-btn cl-btn--sm cl-btn--ghost">Desactivar</button>
    <button class="cl-btn cl-btn--sm cl-btn--danger">Eliminar</button>
  </div>

  <!-- Table -->
  <table class="cl-table">
    <thead>
      <tr>
        <th><input type="checkbox" aria-label="Seleccionar todo"></th>
        <th data-sort="asc">Nombre</th>
        <th data-sort>Categoría</th>
        <th data-sort>Precio</th>
        <th data-sort>Stock</th>
        <th>Estado</th>
        <th>Acciones</th>
      </tr>
    </thead>
    <tbody><!-- rows --></tbody>
  </table>

  <!-- Pagination -->
  <div class="cl-pagination">
    <span>Página 1 de 11</span>
    <div class="cl-pagination__buttons">
      <button disabled>Anterior</button>
      <button>1</button>
      <button class="active">2</button>
      <button>3</button>
      <button>Siguiente</button>
    </div>
    <select>
      <option>25 por página</option>
      <option>50 por página</option>
      <option>100 por página</option>
    </select>
  </div>
</div>
```

```css
.cl-page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: var(--cl-space-6);
  border-bottom: 1px solid var(--cl-gray-200);
  margin-bottom: var(--cl-space-6);
}
.cl-page__title {
  font-size: var(--cl-text-2xl);
  font-weight: var(--cl-font-bold);
  margin: 0;
}
.cl-page__subtitle {
  font-size: var(--cl-text-sm);
  color: var(--cl-gray-500);
  margin-top: var(--cl-space-1);
}
.cl-page__actions {
  display: flex;
  gap: var(--cl-space-3);
}

/* Filters bar */
.cl-filters {
  display: flex;
  gap: var(--cl-space-4);
  align-items: center;
  padding: var(--cl-space-4) 0;
  flex-wrap: wrap;
}
.cl-search {
  position: relative;
  flex: 1;
  max-width: 400px;
}
.cl-search__input {
  width: 100%;
  padding: var(--cl-space-2) var(--cl-space-4) var(--cl-space-2) 40px;
  border: 1px solid var(--cl-gray-300);
  border-radius: var(--cl-radius-md);
  font-size: var(--cl-text-sm);
}
.cl-search__icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--cl-gray-400);
  width: 16px;
  height: 16px;
}

/* Bulk actions bar */
.cl-bulk-actions {
  display: flex;
  align-items: center;
  gap: var(--cl-space-3);
  padding: var(--cl-space-3) var(--cl-space-4);
  background: var(--cl-info-light);
  border: 1px solid var(--cl-info);
  border-radius: var(--cl-radius-md);
  margin-bottom: var(--cl-space-4);
  animation: slideDown 0.2s ease;
}

/* Pagination */
.cl-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--cl-space-4) 0;
  font-size: var(--cl-text-sm);
  color: var(--cl-gray-500);
}
```

### 6.3 Form Design Patterns

**Grouped sections with inline validation:**

```css
/* Form section */
.cl-form-section {
  margin-bottom: var(--cl-space-8);
}
.cl-form-section__title {
  font-size: var(--cl-text-lg);
  font-weight: var(--cl-font-semibold);
  padding-bottom: var(--cl-space-3);
  border-bottom: 1px solid var(--cl-gray-200);
  margin-bottom: var(--cl-space-5);
}
.cl-form-section__description {
  font-size: var(--cl-text-sm);
  color: var(--cl-gray-500);
  margin-top: var(--cl-space-1);
}

/* Form grid */
.cl-form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--cl-space-4) var(--cl-space-6);
}
.cl-form-grid--full {
  grid-column: 1 / -1;
}
@media (max-width: 768px) {
  .cl-form-grid {
    grid-template-columns: 1fr;
  }
}

/* Form field */
.cl-field {
  display: flex;
  flex-direction: column;
  gap: var(--cl-space-1-5);
}
.cl-field__label {
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-medium);
  color: var(--cl-gray-700);
}
.cl-field__required {
  color: var(--cl-danger);
}
.cl-field__input {
  padding: var(--cl-space-2-5) var(--cl-space-3);
  border: 1px solid var(--cl-gray-300);
  border-radius: var(--cl-radius-md);
  font-size: 16px; /* prevent iOS zoom */
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.cl-field__input:focus {
  border-color: var(--cl-red-500);
  box-shadow: 0 0 0 3px rgb(232 57 77 / 0.15);
  outline: none;
}
.cl-field__input--error {
  border-color: var(--cl-danger);
}
.cl-field__error {
  font-size: var(--cl-text-xs);
  color: var(--cl-danger);
  display: flex;
  align-items: center;
  gap: var(--cl-space-1);
}
.cl-field__hint {
  font-size: var(--cl-text-xs);
  color: var(--cl-gray-500);
}
```

### 6.4 Report Layout Pattern

```css
/* Report page layout */
.cl-report {
  display: flex;
  flex-direction: column;
  gap: var(--cl-space-6);
}

/* Report controls bar */
.cl-report__controls {
  display: flex;
  align-items: center;
  gap: var(--cl-space-4);
  padding: var(--cl-space-4);
  background: var(--cl-gray-50);
  border-radius: var(--cl-radius-lg);
  border: 1px solid var(--cl-gray-200);
  flex-wrap: wrap;
}

/* Date range picker styling */
.cl-date-range {
  display: flex;
  align-items: center;
  gap: var(--cl-space-2);
}
.cl-date-range__preset {
  display: flex;
  gap: var(--cl-space-1);
}
.cl-date-range__preset-btn {
  padding: var(--cl-space-1) var(--cl-space-3);
  border-radius: var(--cl-radius-full);
  font-size: var(--cl-text-xs);
  font-weight: var(--cl-font-medium);
  cursor: pointer;
  border: 1px solid var(--cl-gray-300);
  background: white;
}
.cl-date-range__preset-btn--active {
  background: var(--cl-red-700);
  border-color: var(--cl-red-700);
  color: white;
}

/* Export buttons */
.cl-report__exports {
  display: flex;
  gap: var(--cl-space-2);
  margin-left: auto;
}

/* Chart + table toggle */
.cl-view-toggle {
  display: inline-flex;
  border: 1px solid var(--cl-gray-300);
  border-radius: var(--cl-radius-md);
  overflow: hidden;
}
.cl-view-toggle__btn {
  padding: var(--cl-space-2) var(--cl-space-3);
  border: none;
  background: white;
  cursor: pointer;
  font-size: var(--cl-text-sm);
}
.cl-view-toggle__btn--active {
  background: var(--cl-gray-900);
  color: white;
}
```

### 6.5 Breadcrumbs

```css
.cl-breadcrumbs {
  display: flex;
  align-items: center;
  gap: var(--cl-space-1-5);
  font-size: var(--cl-text-sm);
  color: var(--cl-gray-500);
  margin-bottom: var(--cl-space-2);
}
.cl-breadcrumbs a {
  color: var(--cl-gray-500);
  text-decoration: none;
}
.cl-breadcrumbs a:hover {
  color: var(--cl-red-700);
}
.cl-breadcrumbs__separator::before {
  content: '/';
  margin: 0 var(--cl-space-1);
  color: var(--cl-gray-400);
}
.cl-breadcrumbs__current {
  color: var(--cl-gray-900);
  font-weight: var(--cl-font-medium);
}
```

---

## 7. Modern CSS/Frontend for Jinja2 + Bootstrap

### 7.1 CSS Custom Properties (Design Tokens)

**Consolidation strategy** (currently tokens are duplicated in `base.css` + `styles.css`):

```css
/* tokens.css — SINGLE SOURCE OF TRUTH */
:root {
  /* ── Colors (as defined in Section 2.1) ── */
  /* ── Typography (as defined in Section 2.2) ── */
  /* ── Spacing (as defined in Section 2.3) ── */
  /* ── Radii (as defined in Section 2.4) ── */
  /* ── Shadows (as defined in Section 2.5) ── */
  
  /* ── Z-index scale ── */
  --cl-z-dropdown:  1000;
  --cl-z-sticky:    1020;
  --cl-z-fixed:     1030;
  --cl-z-modal-bg:  1040;
  --cl-z-modal:     1050;
  --cl-z-popover:   1060;
  --cl-z-tooltip:   1070;
  --cl-z-toast:     1080;

  /* ── Transitions ── */
  --cl-transition-fast: 0.1s ease;
  --cl-transition-base: 0.2s ease;
  --cl-transition-slow: 0.3s ease;

  /* ── Container widths ── */
  --cl-container-sm: 640px;
  --cl-container-md: 768px;
  --cl-container-lg: 1024px;
  --cl-container-xl: 1280px;
}
```

### 7.2 Bootstrap 5.3 Dark Mode Integration

**Current approach** (CasaLeones uses `[data-theme="dark"]`):
- Works but requires maintaining a parallel stylesheet.

**Recommended approach** (Bootstrap 5.3 native):
```html
<html lang="es" data-bs-theme="light">
```

```css
/* Override just the Bootstrap CSS variables */
[data-bs-theme="dark"] {
  --bs-body-bg: #0C0A09;
  --bs-body-color: #FAFAF9;
  --bs-emphasis-color: #FAFAF9;
  --bs-secondary-bg: #1C1917;
  --bs-tertiary-bg: #292524;
  --bs-border-color: #44403C;
  --bs-primary: var(--cl-red-600);
  --bs-primary-rgb: 212, 37, 58;
}
/* Bootstrap cards, modals, tables automatically adapt */
```

**Migration path:**
1. Replace `data-theme="dark"` with `data-bs-theme="dark"` in `base.html`.
2. Map your `--cl-*` tokens to `--bs-*` variables.
3. Remove 80% of `dark-mode.css` — Bootstrap handles the rest.
4. Keep only CasaLeones-specific dark overrides (KDS, mapa mesas, etc.).

### 7.3 Font Stack (Inter via Variable Font)

```html
<!-- In base.html <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" 
      rel="stylesheet">
```

```css
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 
               Roboto, Oxygen, Ubuntu, sans-serif;
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  /* cv02: Alternate a, cv03: Alternate g, cv11: Single-story l */
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Tabular numbers for prices and timers */
.price, .timer, .kpi-value, [data-numeric] {
  font-variant-numeric: tabular-nums;
}
```

**Alternative:** System font stack (zero network cost):
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               Oxygen, Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
}
```

### 7.4 CSS Grid for Dashboards

```css
/* Auto-responsive grid without media queries */
.cl-auto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(var(--grid-min, 280px), 1fr));
  gap: var(--cl-space-6);
}

/* Named areas for complex layouts */
.cl-dashboard-layout {
  display: grid;
  grid-template-areas:
    "kpi1 kpi2 kpi3 kpi4"
    "chart-main chart-main chart-side chart-side"
    "table table alerts alerts";
  grid-template-columns: repeat(4, 1fr);
  gap: var(--cl-space-6);
}
@media (max-width: 768px) {
  .cl-dashboard-layout {
    grid-template-areas:
      "kpi1 kpi2"
      "kpi3 kpi4"
      "chart-main chart-main"
      "chart-side chart-side"
      "table table"
      "alerts alerts";
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### 7.5 Container Queries

```css
/* Container queries for truly component-responsive design */
.cl-card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .cl-kpi {
    flex-direction: row;
  }
}
@container card (max-width: 399px) {
  .cl-kpi {
    flex-direction: column;
    text-align: center;
  }
}
```

**Browser support:** Chrome 105+, Firefox 110+, Safari 16+. Safe for new development in 2026.

### 7.6 View Transitions API

```css
/* Enable view transitions for page navigations */
@view-transition {
  navigation: auto;
}

/* Cross-fade default transition */
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 0.25s;
}

/* Named transitions for specific elements */
.cl-page__title {
  view-transition-name: page-title;
}
::view-transition-group(page-title) {
  animation-duration: 0.3s;
}

/* Keep sidebar stable during transitions */
.cl-sidebar {
  view-transition-name: sidebar;
}
::view-transition-old(sidebar),
::view-transition-new(sidebar) {
  animation: none;
}
```

**Usage in Jinja2:** Since CasaLeones is a server-rendered MPA, the View Transitions API for MPAs (cross-document) is available in Chrome 126+ with the `@view-transition` CSS rule. No JavaScript needed.

### 7.7 CSS File Architecture (Recommended)

```
static/css/
├── tokens.css          # Design tokens (variables) — loaded FIRST
├── base.css            # Reset, typography, body defaults
├── components/
│   ├── buttons.css
│   ├── cards.css
│   ├── forms.css
│   ├── tables.css
│   ├── modals.css
│   ├── badges.css
│   ├── navigation.css
│   ├── pagination.css
│   └── toasts.css
├── layouts/
│   ├── sidebar.css
│   ├── split-panel.css
│   ├── dashboard.css
│   └── floorplan.css
├── pages/
│   ├── kds.css          # Kitchen display system
│   ├── meseros.css      # Server view
│   ├── admin.css        # Back-office
│   └── login.css
├── utilities/
│   ├── animations.css
│   └── a11y.css         # Accessibility
└── dark-mode.css        # Reduced to BS 5.3 overrides only
```

---

## 8. Accessibility Requirements

### 8.1 WCAG 2.1 AA Minimum Checklist

| Criterion | Requirement | CasaLeones Status | Action |
|-----------|-------------|-------------------|--------|
| 1.1.1 Non-text Content | Alt text on all images | ⚠️ Partial | Audit all `<img>` tags |
| 1.3.1 Info & Relationships | Semantic HTML (headings, lists, tables) | ⚠️ Partial | Use `<nav>`, `<main>`, `<section>` consistently |
| 1.4.1 Use of Color | Color not sole indicator | ❌ Missing (table states) | Add icons/text alongside color in mesa states |
| 1.4.3 Contrast (Minimum) | 4.5:1 for normal text, 3:1 for large | ✅ Mostly | Fix any `#999` on white (2.85:1) |
| 1.4.4 Resize Text | Usable at 200% zoom | ⚠️ Untested | Test with browser zoom |
| 1.4.11 Non-text Contrast | 3:1 for UI components | ⚠️ Partial | Check button borders, form borders |
| 2.1.1 Keyboard | All functionality via keyboard | ⚠️ Partial (mesa map) | Add keyboard nav to floor plan |
| 2.4.1 Bypass Blocks | Skip navigation link | ✅ Done | `.skip-to-content` exists |
| 2.4.3 Focus Order | Logical focus order | ⚠️ Partial | Audit modals, tab order |
| 2.4.7 Focus Visible | Visible focus indicator | ✅ Done | `focus-visible` outline exists |
| 4.1.2 Name, Role, Value | ARIA labels on interactive elements | ⚠️ Partial | Add `aria-label` to all icon buttons |

### 8.2 Touch Targets

```css
/* Minimum touch targets per WCAG 2.5.5 (Enhanced) and Apple HIG */
.cl-touch-target {
  min-width: 48px;
  min-height: 48px;
  /* If visual element is smaller, add padding: */
  padding: max(0px, calc((48px - 100%) / 2));
}

/* Critical POS buttons — even larger for speed */
.cl-btn--pos {
  min-height: 56px;
  min-width: 56px;
}

/* Kitchen bump buttons */
.cl-kds .cl-btn {
  min-height: 64px;
  font-size: 20px;
}

/* Spacing between tap targets: minimum 8px gap */
.cl-btn + .cl-btn {
  margin-left: var(--cl-space-2);
}
```

### 8.3 Color-Independent Status Indicators

```html
<!-- Bad: Color only -->
<span class="badge bg-success">●</span>

<!-- Good: Color + text + icon -->
<span class="cl-badge cl-badge--success">
  <svg aria-hidden="true"><!-- check icon --></svg>
  Disponible
</span>

<!-- For mesas on the floor plan: -->
<div class="cl-mesa cl-mesa--disponible" 
     role="button" 
     tabindex="0"
     aria-label="Mesa 5, disponible, capacidad 4 personas">
  <span class="cl-mesa__number">5</span>
  <span class="cl-mesa__status">✓</span> <!-- icon reinforces green -->
  <span class="cl-mesa__capacity">4p</span>
</div>
```

### 8.4 Screen Reader Support

```html
<!-- Announce dynamic updates -->
<div aria-live="polite" aria-atomic="true" class="visually-hidden" id="order-announcer">
  <!-- JS: "Taco al Pastor agregado. Total: $325.00" -->
</div>

<!-- KDS: announce new orders -->
<div aria-live="assertive" aria-atomic="true" class="visually-hidden" id="kds-announcer">
  <!-- "Nueva orden #1234 para Mesa 5" -->
</div>
```

### 8.5 Keyboard Navigation for Floor Plan

```javascript
// Arrow key navigation between tables
document.querySelector('.cl-floorplan').addEventListener('keydown', (e) => {
  const mesas = [...document.querySelectorAll('.cl-mesa')];
  const current = document.activeElement;
  const idx = mesas.indexOf(current);
  if (idx < 0) return;

  let next;
  switch(e.key) {
    case 'ArrowRight': next = mesas[idx + 1]; break;
    case 'ArrowLeft':  next = mesas[idx - 1]; break;
    case 'Enter':
    case ' ':
      e.preventDefault();
      current.click();
      return;
  }
  if (next) {
    e.preventDefault();
    next.focus();
  }
});
```

---

## 9. Progressive Web App Patterns

### 9.1 Offline-First Strategy

**Current CasaLeones PWA** (`sw.js`): Network-first with cache fallback.

**Recommended: Stale-While-Revalidate for static assets, Network-first for API:**

```javascript
// sw.js — Enhanced strategy
const CACHE_NAME = 'casaleones-v2';
const STATIC_ASSETS = [
  '/static/css/tokens.css',
  '/static/css/base.css',
  '/static/css/components/',
  '/static/js/',
  '/static/img/',
  '/static/manifest.json',
];

// Install: pre-cache critical assets
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Fetch strategy
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // API calls: Network-first, cache fallback (critical for POS)
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/admin/')) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request))
    );
    return;
  }

  // Static assets: Stale-while-revalidate
  if (url.pathname.startsWith('/static/')) {
    e.respondWith(
      caches.match(e.request).then(cached => {
        const fetched = fetch(e.request).then(res => {
          const clone = res.clone();
          caches.open(CACHE_NAME).then(c => c.put(e.request, clone));
          return res;
        });
        return cached || fetched;
      })
    );
    return;
  }

  // Pages: Network-first
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request) || caches.match('/offline.html'))
  );
});
```

### 9.2 Offline Queue for Orders

```javascript
// Queue orders when offline, sync when back online
class OfflineOrderQueue {
  constructor() {
    this.dbName = 'casaleones-offline';
    this.storeName = 'pending-orders';
  }

  async save(orderData) {
    const db = await this.openDB();
    const tx = db.transaction(this.storeName, 'readwrite');
    tx.objectStore(this.storeName).add({
      ...orderData,
      timestamp: Date.now(),
      synced: false
    });
  }

  async syncPending() {
    const db = await this.openDB();
    const tx = db.transaction(this.storeName, 'readonly');
    const store = tx.objectStore(this.storeName);
    const pending = await store.getAll();
    
    for (const order of pending.filter(o => !o.synced)) {
      try {
        await fetch('/api/ordenes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(order)
        });
        // Mark synced
        const writeTx = db.transaction(this.storeName, 'readwrite');
        order.synced = true;
        writeTx.objectStore(this.storeName).put(order);
      } catch { /* Will retry next sync */ }
    }
  }
}

// Background sync registration
if ('serviceWorker' in navigator && 'SyncManager' in window) {
  navigator.serviceWorker.ready.then(reg => {
    return reg.sync.register('sync-orders');
  });
}
```

### 9.3 Push Notifications for Kitchen

```javascript
// Request permission on KDS page load
async function setupKDSNotifications() {
  if (!('Notification' in window)) return;
  
  const permission = await Notification.requestPermission();
  if (permission !== 'granted') return;

  const reg = await navigator.serviceWorker.ready;
  const sub = await reg.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: VAPID_PUBLIC_KEY
  });
  
  // Send subscription to backend
  await fetch('/api/push/subscribe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subscription: sub, station: 'taqueros' })
  });
}
```

### 9.4 Install Prompt

```javascript
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  
  // Show custom install banner
  document.getElementById('install-banner').hidden = false;
});

document.getElementById('install-btn').addEventListener('click', async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  deferredPrompt = null;
  document.getElementById('install-banner').hidden = true;
});
```

### 9.5 Network Status Indicator

```css
.cl-offline-banner {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: var(--cl-warning);
  color: var(--cl-warning-dark);
  text-align: center;
  padding: var(--cl-space-2);
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-semibold);
  z-index: var(--cl-z-toast);
  transform: translateY(-100%);
  transition: transform 0.3s ease;
}
.cl-offline-banner--visible {
  transform: translateY(0);
}
```

```javascript
window.addEventListener('online', () => {
  document.getElementById('offline-banner').classList.remove('cl-offline-banner--visible');
  // Trigger sync
  offlineQueue.syncPending();
});
window.addEventListener('offline', () => {
  document.getElementById('offline-banner').classList.add('cl-offline-banner--visible');
});
```

---

## 10. Animation & Micro-Interactions

### 10.1 Principles

1. **Duration**: 100–300ms for UI feedback, 300–500ms for state transitions.
2. **Easing**: Use `ease-out` for entering elements, `ease-in` for exiting, `ease-in-out` for movement.
3. **Purpose**: Every animation must serve a purpose — confirm action, show relationship, or guide attention.
4. **Reduce motion**: Always respect `prefers-reduced-motion`.

```css
/* Global motion reduction */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### 10.2 Meaningful Transitions

```css
/* Product added to order — bounce on the cart count */
@keyframes cart-bounce {
  0%   { transform: scale(1); }
  25%  { transform: scale(1.3); }
  50%  { transform: scale(0.9); }
  75%  { transform: scale(1.1); }
  100% { transform: scale(1); }
}
.cl-cart-badge--animate {
  animation: cart-bounce 0.4s ease;
}

/* Item entering the order list */
@keyframes slide-in-right {
  from { transform: translateX(20px); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}
.cl-order-item--new {
  animation: slide-in-right 0.25s ease-out;
}

/* Item removal — slide out + collapse */
@keyframes slide-out-left {
  to { transform: translateX(-100%); opacity: 0; height: 0; margin: 0; padding: 0; }
}
.cl-order-item--removing {
  animation: slide-out-left 0.3s ease-in forwards;
  overflow: hidden;
}

/* Table status change */
@keyframes status-flash {
  0%, 100% { opacity: 1; }
  50%      { opacity: 0.5; }
}
.cl-mesa--status-change {
  animation: status-flash 0.3s ease 3;
}

/* Payment success */
@keyframes payment-success {
  0%   { transform: scale(0); opacity: 0; }
  50%  { transform: scale(1.15); }
  100% { transform: scale(1); opacity: 1; }
}
.cl-payment-success-icon {
  animation: payment-success 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

### 10.3 Loading States

```css
/* Skeleton screen (improved from current) */
.cl-skeleton {
  background: linear-gradient(
    90deg,
    var(--cl-gray-200) 0%,
    var(--cl-gray-100) 40%,
    var(--cl-gray-200) 80%
  );
  background-size: 200% 100%;
  animation: cl-shimmer 1.5s ease-in-out infinite;
  border-radius: var(--cl-radius-sm);
}
@keyframes cl-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Skeleton variants */
.cl-skeleton--text   { height: 1em; width: 75%; }
.cl-skeleton--text-sm{ height: 0.75em; width: 50%; }
.cl-skeleton--title  { height: 1.5em; width: 40%; }
.cl-skeleton--avatar { width: 40px; height: 40px; border-radius: 50%; }
.cl-skeleton--card   { height: 120px; width: 100%; border-radius: var(--cl-radius-md); }
.cl-skeleton--kpi    { height: 100px; border-radius: var(--cl-radius-lg); }
.cl-skeleton--chart  { height: 300px; border-radius: var(--cl-radius-lg); }

/* Dark mode skeleton */
[data-bs-theme="dark"] .cl-skeleton {
  background: linear-gradient(
    90deg,
    var(--cl-gray-800) 0%,
    var(--cl-gray-700) 40%,
    var(--cl-gray-800) 80%
  );
  background-size: 200% 100%;
}
```

### 10.4 Success/Error Feedback

```css
/* Inline success (form save, order sent) */
.cl-feedback {
  display: inline-flex;
  align-items: center;
  gap: var(--cl-space-2);
  padding: var(--cl-space-2) var(--cl-space-3);
  border-radius: var(--cl-radius-md);
  font-size: var(--cl-text-sm);
  font-weight: var(--cl-font-medium);
  animation: cl-feedback-in 0.3s ease-out;
}
@keyframes cl-feedback-in {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}
.cl-feedback--success {
  background: var(--cl-success-light);
  color: var(--cl-success-dark);
  border: 1px solid var(--cl-success);
}
.cl-feedback--error {
  background: var(--cl-danger-light);
  color: var(--cl-danger-dark);
  border: 1px solid var(--cl-danger);
}

/* Error shake on invalid form submission */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  20%      { transform: translateX(-6px); }
  40%      { transform: translateX(6px); }
  60%      { transform: translateX(-4px); }
  80%      { transform: translateX(4px); }
}
.cl-field--shake {
  animation: shake 0.4s ease;
}
```

### 10.5 Toast Notifications (Enhanced)

```javascript
function showToast(message, type = 'info', duration = 3000) {
  const icons = {
    success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️', celebration: '🎉'
  };
  
  const toast = document.createElement('div');
  toast.className = `cl-toast cl-toast--${type}`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', type === 'error' ? 'assertive' : 'polite');
  toast.innerHTML = `
    <span class="cl-toast__icon" aria-hidden="true">${icons[type]}</span>
    <span class="cl-toast__message">${message}</span>
    <button class="cl-toast__close" aria-label="Cerrar notificación">&times;</button>
  `;
  
  document.getElementById('toast-container').appendChild(toast);
  
  // Auto-dismiss
  const timer = setTimeout(() => removeToast(toast), duration);
  
  // Manual dismiss
  toast.querySelector('.cl-toast__close').addEventListener('click', () => {
    clearTimeout(timer);
    removeToast(toast);
  });
}

function removeToast(toast) {
  toast.classList.add('cl-toast--exiting');
  toast.addEventListener('animationend', () => toast.remove());
}
```

```css
.cl-toast {
  display: flex;
  align-items: center;
  gap: var(--cl-space-3);
  padding: var(--cl-space-3) var(--cl-space-4);
  background: var(--cl-gray-900);
  color: white;
  border-radius: var(--cl-radius-lg);
  box-shadow: var(--cl-shadow-xl);
  animation: cl-toast-in 0.3s ease-out;
  margin-bottom: var(--cl-space-2);
  max-width: 400px;
}
@keyframes cl-toast-in {
  from { transform: translateX(100%); opacity: 0; }
  to   { transform: translateX(0); opacity: 1; }
}
.cl-toast--exiting {
  animation: cl-toast-out 0.2s ease-in forwards;
}
@keyframes cl-toast-out {
  to { transform: translateX(100%); opacity: 0; }
}
.cl-toast--success { border-left: 4px solid var(--cl-success); }
.cl-toast--error   { border-left: 4px solid var(--cl-danger); }
.cl-toast--warning { border-left: 4px solid var(--cl-warning); }
.cl-toast--info    { border-left: 4px solid var(--cl-info); }
```

---

## 11. CasaLeones Gap Analysis & Migration Path

### 11.1 Current Issues Identified

| Issue | Severity | Location | Fix |
|-------|----------|----------|-----|
| CSS tokens duplicated | High | `base.css` & `styles.css` both define `:root` vars | Consolidate into `tokens.css` |
| Body background conflict | High | `base.css`: `#FAF3E0`, `styles.css`: `#000` | Single source; `#000` overrides warm theme |
| No formal type scale | Medium | Ad-hoc font sizes throughout | Implement `--cl-text-*` tokens |
| KDS fonts too small | High | Current cocina: 1.1–2rem | Need 1.5–3.75rem minimum |
| No split-panel layout | High | Mesero view is single-column | Implement industry-standard split-panel |
| Dropdown nav for admin | Medium | All admin in one dropdown | Migrate to sidebar for admin views |
| Dark mode = 291 lines | Medium | Full override stylesheet | Reduce to ~50 lines with BS 5.3 |
| No breadcrumbs | Low | Admin pages lack context | Add breadcrumbs to all admin pages |
| Limited skeleton variants | Low | Only 4 skeleton classes | Expand to KPI, chart, table row skeletons |
| Mesa map: no keyboard nav | High (a11y) | `mapa_mesas.js` | Add arrow key + Enter support |
| Color-only state indicators | Medium (a11y) | Mesa states, order status | Add text/icon labels |

### 11.2 Migration Priority

**Phase 1 — Foundation (Week 1–2):**
- [ ] Create `tokens.css` with all design tokens
- [ ] Consolidate `base.css` + `styles.css` (remove duplication)
- [ ] Implement Inter font with proper type scale
- [ ] Migrate dark mode to Bootstrap 5.3 `data-bs-theme`
- [ ] Define 8px spacing system

**Phase 2 — Core Components (Week 3–4):**
- [ ] Redesign button system with POS-appropriate sizes
- [ ] Card component with consistent styling
- [ ] Table component with sortable headers, sticky thead
- [ ] Form field component with inline validation
- [ ] Toast notification system (improved)

**Phase 3 — Key Views (Week 5–8):**
- [ ] Split-panel order screen (mesero view)
- [ ] Floor plan as default landing page
- [ ] KDS redesign (larger fonts, time-gradient cards, conveyor layout)
- [ ] Admin sidebar navigation
- [ ] CRUD list page pattern (search, filter, bulk, pagination)

**Phase 4 — Polish (Week 9–10):**
- [ ] Skeleton loading for all async content
- [ ] Animation system (product add, payment success, status change)
- [ ] Accessibility audit (keyboard nav, ARIA, contrast)
- [ ] PWA enhancement (offline queue, push notifications)
- [ ] Responsive testing (tablet, mobile, desktop)

### 11.3 Jinja2 Template Strategy

```html
<!-- Recommended: component macros for reuse -->
{% macro kpi_card(label, value, trend, trend_pct, icon, accent_color) %}
<div class="cl-kpi" style="--kpi-accent: var(--cl-{{ accent_color }})">
  <div class="cl-kpi__icon">{{ icon|safe }}</div>
  <div class="cl-kpi__content">
    <span class="cl-kpi__label">{{ label }}</span>
    <span class="cl-kpi__value">{{ value }}</span>
    {% if trend_pct %}
    <span class="cl-kpi__trend cl-kpi__trend--{{ trend }}">
      {{ '↑' if trend == 'up' else '↓' }} {{ trend_pct }}
    </span>
    {% endif %}
  </div>
</div>
{% endmacro %}

<!-- Usage: -->
{{ kpi_card('Ventas Hoy', '$24,580', 'up', '12.5%', '💰', 'success') }}
```

**Recommended macro library file:**
```
templates/
├── macros/
│   ├── kpi.html
│   ├── table.html
│   ├── form_field.html
│   ├── pagination.html
│   ├── breadcrumbs.html
│   └── badges.html
```

### 11.4 Performance Budget

| Metric | Target | Current (estimated) |
|--------|--------|-------------------|
| First Contentful Paint | < 1.5s | ~2.0s |
| Total CSS size | < 60KB (gzip) | ~45KB (but duplicated) |
| Total JS size | < 100KB (gzip) | ~80KB + Chart.js |
| Font files | < 50KB (Inter variable) | 0KB (system fonts) |
| Lighthouse Performance | > 90 | ~70 |
| Lighthouse Accessibility | > 95 | ~75 |

---

## Appendix A: Quick Reference — CSS Values

```css
/* Copy-paste reference for the PRD */

/* Colors */
--brand-primary: #A6192E;
--brand-primary-hover: #8A1325;
--brand-secondary: #0A3D62;
--brand-accent: #507C36;
--brand-warm-bg: #FAF3E0;

/* Type */
--font-body: 'Inter', system-ui, sans-serif;
--font-mono: 'JetBrains Mono', monospace;
--font-size-body: 16px;
--font-size-small: 14px;
--font-size-kds-item: 28–36px;
--font-size-kds-header: 48–60px;

/* Spacing */
--space-unit: 8px;
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;

/* Borders */
--radius-button: 8px;
--radius-card: 12px;
--radius-modal: 16px;
--radius-pill: 9999px;

/* Touch targets */
--min-touch-desktop: 44px;
--min-touch-tablet: 48px;
--min-touch-pos: 56px;
--min-touch-kds: 64px;

/* Transitions */
--transition-fast: 150ms ease;
--transition-normal: 250ms ease;
--transition-slow: 350ms ease;

/* Breakpoints */
--bp-mobile: 576px;
--bp-tablet: 768px;
--bp-desktop: 1024px;
--bp-wide: 1280px;
--bp-ultra: 1536px;

/* Z-index scale */
--z-base: 0;
--z-dropdown: 1000;
--z-sticky: 1020;
--z-modal: 1050;
--z-toast: 1080;
```

## Appendix B: Icon Recommendations

Use **Lucide Icons** (open-source fork of Feather Icons):
- Consistent 24×24 grid, 2px stroke
- MIT licensed, 1500+ icons
- Available as SVG sprites or individual imports
- Perfect for POS: `utensils`, `receipt`, `wallet`, `clock`, `users`, `chef-hat`, `flame`, `table`

```html
<!-- CDN usage in Jinja2 -->
<script src="https://unpkg.com/lucide@latest"></script>
<script>lucide.createIcons();</script>

<!-- Usage -->
<i data-lucide="utensils" class="cl-icon"></i>
```

## Appendix C: Recommended Libraries (compatible with Flask+Jinja2)

| Library | Purpose | Size (gzip) | CDN? |
|---------|---------|-------------|------|
| Bootstrap 5.3 | Component framework | 25KB CSS + 16KB JS | ✅ |
| Chart.js 4.x | Charts/graphs | 65KB | ✅ |
| Lucide Icons | Icon set | 0KB (SVG inline) | ✅ |
| Sortable.js | Drag-and-drop | 12KB | ✅ |
| Fuse.js | Client-side fuzzy search | 6KB | ✅ |
| Day.js | Date formatting | 3KB | ✅ |
| html5-qrcode | QR code scanning | 85KB | ✅ |
| hotkeys-js | Keyboard shortcuts | 3KB | ✅ |

---

*This document provides actionable specifications that can be directly incorporated into the CasaLeones POS redesign PRD. Every CSS value, component pattern, and recommendation has been tailored to the Flask+Jinja2+Bootstrap stack and the specific needs identified in the existing codebase.*
