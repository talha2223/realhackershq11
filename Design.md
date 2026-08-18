# Design — Visual Identity & UI Guidelines

## Theme

Cyberpunk / Hacker Terminal aesthetic. Dark backgrounds, monospace typography, sharp edges, high contrast. The UI should feel like a command-line interface wrapped in a modern web framework.

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg-primary` | `#000000` | Page backgrounds |
| `--bg-card` | `#0a0a0a` | Card surfaces |
| `--bg-elevated` | `#111111` | Elevated panels, modals |
| `--border` | `#333333` | Default borders |
| `--border-focus` | `#ffffff` | Focused inputs, active elements |
| `--text-primary` | `#ffffff` | Primary text |
| `--text-secondary` | `#888888` | Muted text, labels |
| `--text-dim` | `rgba(255,255,255,0.5)` | Placeholder text, hints |
| `--accent-indigo` | `#4F46E5` | Primary actions, links |
| `--accent-emerald` | `#10B981` | Success states, online status |
| `--accent-amber` | `#F59E0B` | Warnings, pending states |
| `--accent-red` | `#EF4444` | Danger actions, errors, offline |
| `--accent-slate` | `#64748B` | Muted UI elements |

## Typography

| Element | Font | Size | Weight | Letter Spacing |
|---------|------|------|--------|----------------|
| Page title | Monospace | 1.5rem | 900 | 4px |
| Card heading | Monospace | 1rem | 700 | 2px |
| Body text | Sans-serif | 0.85rem | 400 | Normal |
| Code / terminal | Monospace | 0.75rem | 400 | 0.5px |
| Label / hint | Sans-serif | 0.7rem | 400 | Normal |
| Button text | Monospace | 0.8rem | 700 | 2px |

## Component Patterns

### Card

```css
.card {
  background: #0a0a0a;
  border: 1px solid #333;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}
```

### Button

```css
.btn {
  background: transparent;
  border: 1px solid #fff;
  color: #fff;
  font-family: monospace;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 0.8rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:hover {
  background: #fff;
  color: #000;
}
```

### Input

```css
input {
  width: 100%;
  padding: 0.8rem 1rem;
  background: #000;
  border: 1px solid #333;
  color: #fff;
  font-size: 0.8rem;
  font-family: monospace;
}

input:focus {
  border-color: #fff;
  outline: none;
}
```

### CRT Overlay Effect

```css
.crt-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15) 0px,
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 2px
  );
  z-index: 1000;
}

.crt-flicker {
  position: fixed;
  inset: 0;
  pointer-events: none;
  animation: flicker 0.15s infinite;
  opacity: 0.02;
  z-index: 1000;
}

@keyframes flicker {
  0% { opacity: 0.02; }
  50% { opacity: 0.04; }
  100% { opacity: 0.02; }
}
```

## A-Dex Discord Bot Colors

| Panel | Color | Hex |
|-------|-------|-----|
| System Control | Indigo | `#4F46E5` |
| Data Extraction | Red | `#EF4444` |
| Monitoring | Indigo | `#6366F1` |
| Pranks & Fun | Slate | `#64748B` |
| Advanced | Danger | `#EF4444` |
| Success/Online | Emerald | `#10B981` |
| Warning | Amber | `#F59E0B` |
| Error/Offline | Red | `#EF4444` |

## A-Dex Discord Bot Embed Footer

```
Text: "H-DEX Ultra v3.0"
Icon: https://i.imgur.com/7jTTxlT.png
```

## Layout Principles

1. **Full-viewport auth screens** — login form centered, black background, CRT overlay active
2. **Dense information display** — maximize data per screen, minimize whitespace
3. **Terminal-inspired forms** — monospace inputs, ALL_CAPS labels, no rounded corners
4. **Status indicators** — green dot for online, red dot for offline, amber for pending
5. **Minimal animation** — only Framer Motion for page transitions and card reveals; no bouncing or elastic effects
6. **Responsive but desktop-first** — optimize for 1920x1080, support down to 768px

## Assets

- Source: `assest for website/` directory
- Icons: Lucide React (lock, shield, user, terminal, etc.)
- Maps: Leaflet with dark tile layer
- Logo: Custom SVG or text-based logo (no image dependency)
