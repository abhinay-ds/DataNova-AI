# DataNova AI — Frontend UI & Design System

The DataNova AI frontend is built with React 19, Vite, and Tailwind CSS v4, adhering to modern UX standards and WCAG AAA color contrast guidelines.

---

## 1. Design Token Architecture

The design system uses CSS custom properties defined in `frontend/src/styles/globals.css`. It supports both light and dark themes with zero flash of unstyled content (FOUC).

### Core Semantic Variables
| CSS Variable | Light Theme | Dark Theme | Purpose |
|---|---|---|---|
| `--dn-bg` | `#f8fafc` (Slate 50) | `#080d19` (Deep Navy) | Global application background |
| `--dn-surface` | `#ffffff` (White) | `#0f172a` (Slate 900) | Card and modal surface background |
| `--dn-border` | `#e2e8f0` (Slate 200) | `#1e293b` (Slate 800) | Container border and divider stroke |
| `--dn-text` | `#0f172a` (Slate 900) | `#f8fafc` (Slate 50) | High-contrast primary body text |
| `--dn-muted` | `#64748b` (Slate 500) | `#94a3b8` (Slate 400) | Subtitle and secondary metadata text |
| `--dn-primary` | `#2563eb` (Blue 600) | `#3b82f6` (Blue 500) | Primary CTA buttons and brand elements |
| `--dn-nav-active-bg`| `#eff6ff` (Blue 50) | `rgba(59, 130, 246, 0.18)` | Active navigation link pill |
| `--dn-nav-active-text`| `#1d4ed8` (Blue 700) | `#60a5fa` (Blue 400) | Active navigation link icon and label |

---

## 2. Navigation & ChatGPT-Style Sidebar

- **Collapsed State (Default):** Compact 72px rail displaying navigation icons only.
- **Hover Expansion:** Hovering over the sidebar smoothly expands it to 260px via a cubic-bezier transition (`transition: width 220ms cubic-bezier(0.4, 0, 0.2, 1)`), revealing section headers and descriptive text.
- **Pin / Collapse Toggle:** Topbar pin button allows users to manually lock the sidebar in the expanded state or collapse it.
- **Zero Content Disruption:** Main layout recalculates margin-left dynamically so content flows naturally without jarring overlays.

---

## 3. Conversational Message Cards

The workspace chat area maps stored backend message payloads to specialized React cards:
- **`AnalysisCard`:** Renders dataset profiling metrics, column data types, missing value warnings, and data quality indicators.
- **`ChartCard`:** Displays high-resolution generated visualizations with full-screen zoom, download capabilities, and dark-mode backdrop safety.
- **`CodeCard`:** Syntax-highlighted Python/SQL snippets with one-click copy and dark-mode inline `<code>` contrast styling.
- **`ModelCard`:** Model evaluation metrics (R², accuracy, precision, recall, F1, ROC-AUC) and cross-validation summaries.
