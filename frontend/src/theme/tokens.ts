/**
 * Design tokens for Footprint Manager.
 *
 * All spacing, sizing, shadow, z-index, border-radius, opacity, and transition
 * values are defined here as constants. Components must reference these tokens
 * rather than hard-coding raw values.
 *
 * Naming convention: TOKEN_CATEGORY_VARIANT
 */

// ---------------------------------------------------------------------------
// Spacing (multiples of 4px base unit)
// ---------------------------------------------------------------------------

export const SPACING_BASE = 4; // px

export const SPACING = {
  /** 2px */
  xxs: SPACING_BASE * 0.5,
  /** 4px */
  xs: SPACING_BASE,
  /** 8px */
  sm: SPACING_BASE * 2,
  /** 12px */
  md: SPACING_BASE * 3,
  /** 16px */
  lg: SPACING_BASE * 4,
  /** 24px */
  xl: SPACING_BASE * 6,
  /** 32px */
  '2xl': SPACING_BASE * 8,
  /** 48px */
  '3xl': SPACING_BASE * 12,
  /** 64px */
  '4xl': SPACING_BASE * 16,
  /** 96px */
  '5xl': SPACING_BASE * 24,
} as const;

// ---------------------------------------------------------------------------
// Border radius
// ---------------------------------------------------------------------------

export const RADIUS = {
  none: 0,
  /** 2px — subtle rounding */
  xs: 2,
  /** 4px — default input / tag */
  sm: 4,
  /** 8px — card / button (platform default) */
  md: 8,
  /** 12px — modal / panel */
  lg: 12,
  /** 16px — sheet / drawer */
  xl: 16,
  /** 24px — pill / badge */
  '2xl': 24,
  /** 9999px — fully rounded */
  full: 9999,
} as const;

// ---------------------------------------------------------------------------
// Elevation / Shadows
// ---------------------------------------------------------------------------

export const SHADOW = {
  none: 'none',
  /** Subtle surface lift */
  xs: '0 1px 2px rgba(0, 0, 0, 0.06)',
  /** Card resting state */
  sm: '0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.12)',
  /** Card hover / focused */
  md: '0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06)',
  /** Modal / dropdown */
  lg: '0 10px 15px rgba(0, 0, 0, 0.07), 0 4px 6px rgba(0, 0, 0, 0.05)',
  /** Sidebar / overlay panel */
  xl: '0 20px 25px rgba(0, 0, 0, 0.10), 0 10px 10px rgba(0, 0, 0, 0.04)',
  /** Full-screen overlay */
  '2xl': '0 25px 50px rgba(0, 0, 0, 0.25)',
  /** Inner shadow for inset elements */
  inner: 'inset 0 2px 4px rgba(0, 0, 0, 0.06)',
} as const;

// ---------------------------------------------------------------------------
// Z-index layers
// ---------------------------------------------------------------------------

export const Z_INDEX = {
  /** Below everything — background elements */
  behind: -1,
  /** Normal stacking context */
  base: 0,
  /** Raised surfaces (cards, panels) */
  raised: 10,
  /** Dropdown menus, autocomplete */
  dropdown: 100,
  /** Sticky headers, toolbars */
  sticky: 200,
  /** Fixed overlays (sidebar) */
  overlay: 300,
  /** Modals and drawers */
  modal: 400,
  /** Notifications and toasts */
  notification: 500,
  /** Tooltips */
  tooltip: 600,
} as const;

// ---------------------------------------------------------------------------
// Opacity
// ---------------------------------------------------------------------------

export const OPACITY = {
  /** Fully transparent */
  none: 0,
  /** Hover overlay */
  ghost: 0.04,
  /** Disabled state */
  disabled: 0.38,
  /** Subtle tint */
  dim: 0.6,
  /** Medium visibility */
  medium: 0.8,
  /** Near opaque */
  high: 0.92,
  /** Fully opaque */
  full: 1,
} as const;

// ---------------------------------------------------------------------------
// Transition / Animation
// ---------------------------------------------------------------------------

export const TRANSITION = {
  /** Duration in milliseconds */
  duration: {
    instant: 0,
    fast: 100,
    /** Default micro-interactions */
    base: 200,
    slow: 350,
    /** Page-level transitions */
    page: 500,
  },
  /** Easing functions */
  easing: {
    linear: 'linear',
    /** Standard material-like easing */
    standard: 'cubic-bezier(0.4, 0, 0.2, 1)',
    /** Enter animations */
    decelerate: 'cubic-bezier(0.0, 0.0, 0.2, 1)',
    /** Exit animations */
    accelerate: 'cubic-bezier(0.4, 0, 1, 1)',
    /** Spring-like bounce */
    spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
  },
} as const;

// ---------------------------------------------------------------------------
// Colour palette (raw tokens — not MUI theme values)
// ---------------------------------------------------------------------------

export const COLOR = {
  // Brand blues
  brand: {
    50: '#E3F2FD',
    100: '#BBDEFB',
    200: '#90CAF9',
    300: '#64B5F6',
    400: '#42A5F5',
    500: '#2196F3',
    600: '#1E88E5',
    700: '#1565C0',
    800: '#003C8F',
    900: '#0D2D6B',
  },
  // Teal accent
  teal: {
    500: '#00838F',
    600: '#006064',
    700: '#005662',
  },
  // Neutral greys
  neutral: {
    0: '#FFFFFF',
    50: '#F5F7FA',
    100: '#EDF0F5',
    200: '#E0E4ED',
    300: '#C4CAD8',
    400: '#9CA3B0',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
    1000: '#000000',
  },
  // Semantic
  success: '#2E7D32',
  warning: '#ED6C02',
  error: '#D32F2F',
  info: '#0288D1',
} as const;
