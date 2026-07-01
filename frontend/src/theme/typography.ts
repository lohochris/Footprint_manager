/**
 * Typography scale for Footprint Manager.
 *
 * Defines font families, weights, and the full type scale used by the
 * MUI theme and any custom typography components.  Import these into the
 * MUI theme configuration rather than duplicating values.
 */

// ---------------------------------------------------------------------------
// Font families
// ---------------------------------------------------------------------------

export const FONT_FAMILY = {
  /** Primary UI font — modern, highly legible at all sizes */
  sans: '"Inter", "Roboto", "Helvetica Neue", "Arial", sans-serif',
  /** Monospace — code, identifiers, technical data */
  mono: '"JetBrains Mono", "Fira Code", "Cascadia Code", "Consolas", monospace',
  /** Display / headings — used for hero text only */
  display: '"Inter", "Roboto", sans-serif',
} as const;

// ---------------------------------------------------------------------------
// Font weights
// ---------------------------------------------------------------------------

export const FONT_WEIGHT = {
  thin: 100,
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
  extrabold: 800,
} as const;

// ---------------------------------------------------------------------------
// Type scale (rem values assuming 16px root)
// ---------------------------------------------------------------------------

export const FONT_SIZE = {
  '2xs': '0.625rem',  //  10px
  xs:    '0.75rem',   //  12px
  sm:    '0.875rem',  //  14px
  base:  '1rem',      //  16px
  md:    '1.0625rem', // ~17px
  lg:    '1.125rem',  //  18px
  xl:    '1.25rem',   //  20px
  '2xl': '1.5rem',    //  24px
  '3xl': '1.875rem',  //  30px
  '4xl': '2.25rem',   //  36px
  '5xl': '3rem',      //  48px
  '6xl': '3.75rem',   //  60px
} as const;

// ---------------------------------------------------------------------------
// Line heights
// ---------------------------------------------------------------------------

export const LINE_HEIGHT = {
  none: 1,
  tight: 1.25,
  snug: 1.375,
  normal: 1.5,
  relaxed: 1.625,
  loose: 2,
} as const;

// ---------------------------------------------------------------------------
// Letter spacing
// ---------------------------------------------------------------------------

export const LETTER_SPACING = {
  tighter: '0em',
  tight: '0em',
  normal: '0em',
  wide: '0em',
  wider: '0em',
  widest: '0em',
} as const;

// ---------------------------------------------------------------------------
// MUI typography overrides object (imported by theme)
// ---------------------------------------------------------------------------

export const muiTypography = {
  fontFamily: FONT_FAMILY.sans,
  h1: {
    fontWeight: FONT_WEIGHT.bold,
    fontSize: FONT_SIZE['4xl'],
    lineHeight: LINE_HEIGHT.tight,
    letterSpacing: LETTER_SPACING.tighter,
  },
  h2: {
    fontWeight: FONT_WEIGHT.semibold,
    fontSize: FONT_SIZE['3xl'],
    lineHeight: LINE_HEIGHT.tight,
    letterSpacing: LETTER_SPACING.tight,
  },
  h3: {
    fontWeight: FONT_WEIGHT.semibold,
    fontSize: FONT_SIZE['2xl'],
    lineHeight: LINE_HEIGHT.snug,
  },
  h4: {
    fontWeight: FONT_WEIGHT.semibold,
    fontSize: FONT_SIZE.xl,
    lineHeight: LINE_HEIGHT.snug,
  },
  h5: {
    fontWeight: FONT_WEIGHT.medium,
    fontSize: FONT_SIZE.lg,
    lineHeight: LINE_HEIGHT.normal,
  },
  h6: {
    fontWeight: FONT_WEIGHT.medium,
    fontSize: FONT_SIZE.base,
    lineHeight: LINE_HEIGHT.normal,
  },
  subtitle1: {
    fontWeight: FONT_WEIGHT.medium,
    fontSize: FONT_SIZE.base,
    lineHeight: LINE_HEIGHT.relaxed,
  },
  subtitle2: {
    fontWeight: FONT_WEIGHT.medium,
    fontSize: FONT_SIZE.sm,
    lineHeight: LINE_HEIGHT.relaxed,
  },
  body1: {
    fontWeight: FONT_WEIGHT.regular,
    fontSize: FONT_SIZE.base,
    lineHeight: LINE_HEIGHT.normal,
  },
  body2: {
    fontWeight: FONT_WEIGHT.regular,
    fontSize: FONT_SIZE.sm,
    lineHeight: LINE_HEIGHT.normal,
  },
  caption: {
    fontWeight: FONT_WEIGHT.regular,
    fontSize: FONT_SIZE.xs,
    lineHeight: LINE_HEIGHT.normal,
    letterSpacing: LETTER_SPACING.wide,
  },
  overline: {
    fontWeight: FONT_WEIGHT.semibold,
    fontSize: FONT_SIZE['2xs'],
    lineHeight: LINE_HEIGHT.loose,
    letterSpacing: LETTER_SPACING.widest,
    textTransform: 'uppercase' as const,
  },
  button: {
    fontWeight: FONT_WEIGHT.medium,
    fontSize: FONT_SIZE.sm,
    letterSpacing: LETTER_SPACING.wide,
    textTransform: 'none' as const,
  },
} as const;
