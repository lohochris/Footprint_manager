/**
 * Responsive breakpoints for Footprint Manager.
 *
 * These constants mirror the MUI breakpoint system and extend it with
 * semantic names for use in non-MUI contexts (CSS-in-JS, media queries,
 * container queries).
 *
 * Breakpoint system:
 *   xs  — 0px     → Mobile portrait
 *   sm  — 600px   → Mobile landscape / small tablet
 *   md  — 900px   → Tablet
 *   lg  — 1200px  → Desktop
 *   xl  — 1536px  → Large desktop / ultra-wide
 */

// ---------------------------------------------------------------------------
// Breakpoint values in pixels (lower bounds)
// ---------------------------------------------------------------------------

export const BREAKPOINT_VALUES = {
  xs: 0,
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536,
} as const;

export type BreakpointKey = keyof typeof BREAKPOINT_VALUES;

// ---------------------------------------------------------------------------
// Media query helpers (min-width)
// ---------------------------------------------------------------------------

/**
 * Returns a CSS min-width media query string for the given breakpoint.
 *
 * Usage in styled-components or emotion:
 *   `${mediaUp('md')} { display: flex; }`
 */
export const mediaUp = (bp: BreakpointKey): string =>
  `@media (min-width: ${BREAKPOINT_VALUES[bp]}px)`;

/**
 * Returns a CSS max-width media query string for the given breakpoint.
 *
 * Usage:
 *   `${mediaDown('sm')} { display: none; }`
 */
export const mediaDown = (bp: BreakpointKey): string => {
  const keys = Object.keys(BREAKPOINT_VALUES) as BreakpointKey[];
  const index = keys.indexOf(bp);
  if (index <= 0) return '@media (max-width: 0px)';
  const nextBp = keys[index] as BreakpointKey;
  return `@media (max-width: ${BREAKPOINT_VALUES[nextBp] - 0.05}px)`;
};

// ---------------------------------------------------------------------------
// Semantic layout constants
// ---------------------------------------------------------------------------

/**
 * Maximum content width for centred layouts.
 */
export const LAYOUT = {
  /** Global sidebar width (collapsed: icon-only) */
  sidebarWidth: 240,
  sidebarCollapsedWidth: 64,
  /** App header height */
  headerHeight: 64,
  /** Maximum readable content width */
  contentMaxWidth: 1440,
  /** Standard page padding (responsive) */
  pagePaddingDesktop: 32,
  pagePaddingMobile: 16,
} as const;
