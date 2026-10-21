---
name: Logistics Operations & Fleet Matrix
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#45464d'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#545f73'
  on-secondary: '#ffffff'
  secondary-container: '#d5e0f8'
  on-secondary-container: '#586377'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#00174b'
  on-tertiary-container: '#497cff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d8e3fb'
  secondary-fixed-dim: '#bcc7de'
  on-secondary-fixed: '#111c2d'
  on-secondary-fixed-variant: '#3c475a'
  tertiary-fixed: '#dbe1ff'
  tertiary-fixed-dim: '#b4c5ff'
  on-tertiary-fixed: '#00174b'
  on-tertiary-fixed-variant: '#003ea8'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-xl:
    fontFamily: Inter
    fontSize: 2rem
    fontWeight: '700'
    lineHeight: 2.5rem
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.02em
  headline-sm:
    fontFamily: Inter
    fontSize: 1.125rem
    fontWeight: '600'
    lineHeight: 1.5rem
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 1rem
    fontWeight: '400'
    lineHeight: 1.5rem
    letterSpacing: '0'
  body-md:
    fontFamily: Inter
    fontSize: 0.875rem
    fontWeight: '400'
    lineHeight: 1.25rem
    letterSpacing: '0'
  body-sm:
    fontFamily: Inter
    fontSize: 0.75rem
    fontWeight: '400'
    lineHeight: 1rem
    letterSpacing: 0.01em
  tabular-data:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: '500'
    lineHeight: 1.125rem
    letterSpacing: -0.01em
  label-md:
    fontFamily: Inter
    fontSize: 0.8125rem
    fontWeight: '600'
    lineHeight: 1rem
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Inter
    fontSize: 0.6875rem
    fontWeight: '600'
    lineHeight: 0.875rem
    letterSpacing: 0.04em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-compact: 0.5rem
  margin: 1.5rem
  margin-compact: 0.75rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 1.75rem
---

## Brand & Style
The design system establishes an operational cockpit built for dispatchers, fleet coordinators, and logistics directors transitioning away from legacy spreadsheets. The aesthetic is utilitarian, precise, and authoritative. It combines clean modern enterprise ergonomics with high visual stability.

- **Brand Personality**: Systematic, dependable, unyielding, and punctual. Every interface element reinforces control, velocity, and zero ambiguity.
- **Visual Style**: High-density Modern Enterprise with architectural discipline. Clear structural boundaries replace decorative fluff, using hairline dividers, crisp panel contrasts, and explicit visual anchoring.
- **Emotional Response**: Absolute operational clarity, rapid decision confidence, and visual comfort during continuous 8-to-12 hour dispatch shifts.

## Colors
The palette is calibrated for high information density without chromatic fatigue. The workspace relies on neutral cool slates to build functional layers, utilizing color purposefully as state indicators rather than ornamentation.

### Core Canvas & Structure
- **App Canvas**: `#f8fafc` (Slate 50) establishes a low-glare working backdrop.
- **Surface Elevation**: `#ffffff` (Pure White) for actionable card modules, dense data tables, and slide-over drawers.
- **Subtle Partitioning**: `#e2e8f0` (Slate 200) for structural lines, grid cells, and form field perimeters.
- **Muted Surfaces**: `#f1f5f9` (Slate 100) for table headers, frozen columns, summary ribbons, and inactive toggle tracks.

### Brand & Focus Hierarchy
- **Primary Operational (`#0f172a`)**: Slate 900 serves as the primary ground for global navigation bars, top-level headings, metric values, and primary command triggers.
- **Secondary Slate (`#1e293b`)**: Slate 800 for active navigation states, subheadings, and secondary actionable controls.
- **Operational Accent Blue (`#2563eb`)**: High-visibility blue reserved for active links, primary system focus rings, active step progress, and primary table row selections.
- **Logistics Alert Amber (`#d97706`)**: Amber 600 reserved for route friction, pending load confirmations, and cautionary vehicle telemetry.

### Semantic Status Identifiers
To maintain instant legibility across high-density shipment grids:
- **Activo / En Ruta (Success)**: Text `#15803d` (Green 700), Background `#f0fdf4` (Green 50), Border `#bbf7d0` (Green 200).
- **En tránsito (Active Logistics)**: Text `#1d4ed8` (Blue 700), Background `#eff6ff` (Blue 50), Border `#bfdbfe` (Blue 200).
- **Pendiente (Warning / Staging)**: Text `#b45309` (Amber 700), Background `#fffbeb` (Amber 50), Border `#fde68a` (Amber 200).
- **Inactivo / Neutral**: Text `#475569` (Slate 600), Background `#f1f5f9` (Slate 100), Border `#cbd5e1` (Slate 300).
- **Completado**: Text `#0f766e` (Teal 700), Background `#f0fdfa` (Teal 50), Border `#99f6e4` (Teal 200).
- **Cancelado / Siniestro (Critical)**: Text `#b91c1c` (Red 700), Background `#fef2f2` (Red 50), Border `#fecaca` (Red 200).

## Typography
Typographic clarity drives this system. Inter is employed across all hierarchy tiers, enforcing tabular numeral alignments (`font-feature-settings: 'tnum' on, 'cv05' on, 'cv11' on`) across all metric readouts, pricing matrices, fuel indexes, and tracking tallies to eradicate horizontal jitter when values refresh dynamically.

- **Headlines**: Set tightly with negative tracking to conserve vertical footprint and frame modules cleanly.
- **Data Tables & Feeds**: Rendered via `tabular-data` (13px/18px) to maximize row efficiency without sacrificing legibility during extended scan-reading.
- **Labels & Micro-headers**: Transformed to uppercase via CSS when set in `label-sm` for column sorting markers, inventory categories, and status chips.

## Layout & Spacing
The layout employs an enterprise-grade fluid workspace with rigid structural anchor points:

- **Operational Layout**: 12-column dynamic grid with a fixed collapsible left-rail operational nav (240px expanded, 64px icon-only). The central stage flexes to occupy 100% of the viewport width with minimum content boundaries set at 1280px to avoid table crunch.
- **Vertical Rhythm**: Built around a strict 4px base step (`0.25rem`). Data cells leverage `0.5rem` (8px) vertical padding for compact mode and `0.75rem` (12px) for comfortable mode.
- **Responsive Adaptations**:
  - **Desktop Large (≥1440px)**: 3-column split view permitted (Master Nav > Filtered Shipment List > Live Telemetry Drawer). Margin: `1.5rem`.
  - **Desktop Standard (1024px - 1439px)**: 2-column core view with right-side modal or slide-over overlays. Margin: `1rem`.
  - **Field Tablet / Operations Console (768px - 1023px)**: Left rail collapses into an off-canvas drawer; tables switch to high-priority columns with expanded nested drawer inspection. Margin: `0.75rem`.

## Elevation & Depth
Depth is strictly structured through surface contrast and structural borders rather than heavy atmospheric shadows, mirroring professional CAD and financial software:

- **Level 0 (Floor)**: Canvas background (`#f8fafc`). No elevation.
- **Level 1 (Cards & Data Grids)**: White surface (`#ffffff`) surrounded by a 1px uniform structural border (`#e2e8f0`). Zero ambient shadow. This establishes explicit boundaries identical to physical ledger lines.
- **Level 2 (Dropdowns, Popovers, Segment Filters)**: White surface with a 1px border (`#cbd5e1`) and a tight functional shadow: `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)`.
- **Level 3 (Modal Windows & Action Drawers)**: Pure white surface overlaid on top of a slate backdrop veil (`#0f172a` at 45% opacity). Elevated with `0 20px 25px -5px rgba(15, 23, 42, 0.14), 0 8px 10px -6px rgba(15, 23, 42, 0.06)`. Border is maintained via `#cbd5e1` to preserve edge definition against maps or dynamic tables behind it.

## Shapes
To reinforce the institutional, high-accuracy tone of fleet operations, corner radiuses are restrained:

- **Soft Form Factors**: Baseline components (inputs, table shells, primary cards, and buttons) use an exact `0.25rem` (4px) corner radius.
- **Outer Shells & Drawers**: Modals, slide-out quotation trays, and primary screen cards employ `0.375rem` (6px) max radius.
- **Pill Exception**: Status indicator badges uniquely use full pill radius (`9999px`) to immediately distinguish contextual metadata from interactive square-cornered buttons and actionable input containers.

## Components

### Data Tables (The Master Ledger)
- **Header**: `#f1f5f9` (Slate 100) background, 36px height, font: `label-sm`, text color: `#475569`, border-bottom: 2px solid `#cbd5e1`. Table headers feature persistent sorting indicator arrows.
- **Rows**: Alternating hover state with `#f8fafc`. Row height default: 44px (Compact: 36px). Cell borders: hairline 1px solid `#e2e8f0`.
- **Row Selected**: Left border 3px solid `#2563eb`, background: `#eff6ff`.
- **Action Column**: Pinned sticky to the far right with a subtle white-to-transparent gradient shadow mask, exposing inline quick-action icon buttons.

### Status Badges (Meticulous Pill Matrix)
- Height: 22px, padding: `0 8px`, border-width: 1px, solid style.
- Typography: `label-sm`, uppercase, semibold, tabular spacing.
- Includes a 6px solid circular status dot positioned left-of-text for non-verbal color recognition:
  - *Activo*: Dot `#16a34a`
  - *En tránsito*: Dot `#2563eb` with optional subtle pulse animation
  - *Pendiente*: Dot `#d97706`
  - *Inactivo*: Dot `#64748b`
  - *Completado*: Dot `#0d9488`
  - *Cancelado*: Dot `#dc2626`

### Buttons & Operational Triggers
- **Primary**: Solid `#0f172a`, white text, 1px border `#0f172a`. Hover: `#1e293b`. Active: `#334155`. Height: 36px (Compact: 32px).
- **Secondary**: Solid `#ffffff`, text `#1e293b`, 1px border `#cbd5e1`. Hover: `#f8fafc`, border `#94a3b8`.
- **Accent / Dispatch Action**: Solid `#2563eb`, white text. Hover: `#1d4ed8`.
- **Destructive**: White background, text `#dc2626`, border `#fecaca`. Hover: background `#fef2f2`, border `#dc2626`.

### Inputs, Search & Filters
- **Input Height**: 36px. Border: 1px solid `#cbd5e1`. Background: `#ffffff`.
- **Focus State**: Border `#2563eb`, paired with a 2px offset ring in `#93c5fd` (`box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15)`).
- **Table Global Search Bar**: Prefixed with a neutral search icon (`#64748b`), featuring an integrated keyboard shortcut badge (`⌘K` or `Ctrl+K`) right-aligned.

### Multi-Step Quotation & Dispatch Drawer
- **Structure**: Right-docked slide-over panel, fixed 540px width on desktop.
- **Header**: Persistent 64px header with route ID, status badge, and dismiss trigger.
- **Step Indicator**: Linear horizontal progress ribbon at the top: Step circles (24px) linked via 2px structural lines. Active step: `#2563eb`; Completed: `#0f172a`; Upcoming: `#cbd5e1`.
- **Form Layout**: 2-column paired parameter inputs (e.g., *Origen/Destino*, *Peso/Volumen*, *Tipo de Camión/Remolque*, *Tarifa Base/Casetas*).
- **Footer**: Sticky bottom bar with live calculated subtotal in tabular numbers and dual actions (*Guardar Borrador*, *Emitir Cotización*).