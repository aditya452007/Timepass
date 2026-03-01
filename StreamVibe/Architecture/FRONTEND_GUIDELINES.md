# FRONTEND_GUIDELINES.md — Design System

> StreamVibe is a dark-mode-only streaming platform. The palette is inspired by video/cinema UIs: deep navy background, bright red accent, clean white text. NO purple backgrounds, NO glassmorphism, NO gradient overload, NO Google Fonts web requests.

---

## COLOR PALETTE (CSS Custom Properties)

Define these in `src/styles/global.css` under `:root {}`.

```css
:root {
  /* Backgrounds */
  --color-bg-primary:    #0d0f14;   /* Main page background — near black with blue tint */
  --color-bg-secondary:  #161922;   /* Cards, panels, inputs */
  --color-bg-hover:      #1e2330;   /* Hover state on cards/buttons */
  --color-bg-overlay:    #000000cc; /* Semi-transparent overlay (e.g., on thumbnails) */

  /* Text */
  --color-text-primary:  #f0f2f5;   /* Main content text */
  --color-text-secondary:#9aa0ad;   /* Meta info: timestamps, view counts */
  --color-text-muted:    #555e6e;   /* Placeholder text, disabled states */

  /* Accent — Red (used for buttons, likes, active states) */
  --color-accent:        #e5222e;   /* Primary red — StreamVibe brand color */
  --color-accent-hover:  #c41c27;   /* Darker red on hover */
  --color-accent-light:  #ff4450;   /* Lighter red for icons/highlights */

  /* Borders */
  --color-border:        #252b38;   /* Subtle card/input borders */
  --color-border-focus:  #e5222e;   /* Red border on focused inputs */

  /* Status */
  --color-success:       #27ae60;
  --color-error:         #e74c3c;
}
```

---

## TYPOGRAPHY

Use **system fonts only** — no web font CDN requests.

```css
:root {
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                 Helvetica, Arial, sans-serif;

  --font-size-xs:   0.75rem;   /* 12px — tags, labels */
  --font-size-sm:   0.875rem;  /* 14px — meta info, secondary text */
  --font-size-base: 1rem;      /* 16px — body text */
  --font-size-md:   1.125rem;  /* 18px — card titles */
  --font-size-lg:   1.5rem;    /* 24px — page headings */
  --font-size-xl:   2rem;      /* 32px — hero text */

  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold:   700;

  --line-height-body: 1.5;
  --line-height-heading: 1.2;
}
```

---

## SPACING SCALE

Use multiples of 4px.

```css
:root {
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
}
```

---

## BORDER RADIUS

```css
:root {
  --radius-sm:   4px;
  --radius-md:   8px;
  --radius-lg:   12px;
  --radius-full: 9999px;  /* Pills, avatars */
}
```

---

## SHADOWS

```css
:root {
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.4);
  --shadow-modal: 0 8px 32px rgba(0, 0, 0, 0.7);
}
```

---

## LAYOUT

```css
:root {
  --max-width: 1280px;     /* Page content max width */
  --navbar-height: 60px;
  --grid-gap: 20px;
}
```

Video card grid: CSS Grid, 3 columns on desktop (>1024px), 2 on tablet (600–1024px), 1 on mobile.

```css
.video-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--grid-gap);
}

@media (max-width: 1024px) {
  .video-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .video-grid { grid-template-columns: 1fr; }
}
```

---

## COMPONENTS (Visual Spec)

### Navbar
- Background: `--color-bg-secondary`
- Height: 60px
- Logo: `StreamVibe` in `--color-accent`, bold, 20px
- Sticky top, `z-index: 100`
- Search bar: `--color-bg-primary` background, `--color-border` border, 36px height, border-radius `--radius-md`
- Buttons right-aligned

### Video Card
- Background: `--color-bg-secondary`
- Border: 1px solid `--color-border`
- Border-radius: `--radius-lg`
- Thumbnail: 16:9 aspect ratio, `object-fit: cover`, top of card
- Card body: `--space-4` padding
- Title: `--font-size-md`, `--font-weight-medium`, `--color-text-primary`, max 2 lines (line-clamp)
- Meta row: username + view count in `--color-text-secondary`, `--font-size-sm`
- Hover: background changes to `--color-bg-hover`, slight transform `translateY(-2px)`

### Buttons

**Primary Button** (Upload, Submit, Follow):
```css
background: var(--color-accent);
color: white;
border: none;
padding: var(--space-2) var(--space-5);
border-radius: var(--radius-md);
font-weight: var(--font-weight-medium);
cursor: pointer;
transition: background 0.15s;

:hover { background: var(--color-accent-hover); }
:disabled { background: var(--color-text-muted); cursor: not-allowed; }
```

**Ghost Button** (Cancel, Unfollow):
```css
background: transparent;
color: var(--color-text-primary);
border: 1px solid var(--color-border);
/* same padding + radius */
:hover { background: var(--color-bg-hover); }
```

### Form Inputs
```css
background: var(--color-bg-secondary);
border: 1px solid var(--color-border);
border-radius: var(--radius-md);
color: var(--color-text-primary);
padding: var(--space-3) var(--space-4);
font-size: var(--font-size-base);
width: 100%;

:focus {
  outline: none;
  border-color: var(--color-border-focus);
}
::placeholder { color: var(--color-text-muted); }
```

### Like Button
- Heart icon (Unicode ♥ or SVG)
- Unliked: `--color-text-secondary`
- Liked: `--color-accent-light` (red)
- Animate: scale 1.2 on click, then back to 1

### Avatar (initials fallback)
- Circle, 36px diameter
- Background: `--color-accent`
- Text: white, `--font-size-sm`, uppercase
- `border-radius: --radius-full`

### Progress Bar (upload)
- Full width bar below upload button
- Track: `--color-border`
- Fill: `--color-accent`
- Height: 4px
- Border-radius: `--radius-full`
- Animate width with CSS transition

### Tag/Chip
- Background: `--color-bg-hover`
- Color: `--color-text-secondary`
- Padding: `--space-1` `--space-3`
- Border-radius: `--radius-full`
- Font-size: `--font-size-xs`

---

## FORBIDDEN PATTERNS

These are explicitly banned from the codebase:

- ❌ Glassmorphism (no `backdrop-filter`, no frosted glass)
- ❌ Purple, violet, or indigo as primary colors
- ❌ Google Fonts imports or any external font CDN
- ❌ Gradient backgrounds on cards or pages
- ❌ Box shadows with colored glow effects
- ❌ Animations longer than 300ms for interactions
- ❌ Inline styles (use CSS classes or CSS variables only)
- ❌ `!important` anywhere in stylesheets

---

## CSS FILE ORGANIZATION

```
src/styles/
  global.css        ← :root variables, body reset, base typography
  components.css    ← Navbar, VideoCard, Button, Input, Avatar styles
```

Each page can have its own `<style>` section or `.module.css` if preferred, but no exceptions to the color system above.
