/**
 * Dark theme for Footprint Manager.
 *
 * Extends the platform design tokens to provide a fully-realised dark mode
 * variant.  The dark theme uses the same design language as the light theme
 * (same MUI component overrides, same typography) with adjusted colour values
 * for the dark surface context.
 *
 * Usage:
 *   import { darkTheme } from './dark';
 *   <ThemeProvider theme={darkTheme}>...</ThemeProvider>
 */

import { createTheme } from '@mui/material/styles';
import { BREAKPOINT_VALUES } from './breakpoints';
import { muiTypography } from './typography';
import { RADIUS, SHADOW } from './tokens';

export const darkTheme = createTheme({
  breakpoints: {
    values: BREAKPOINT_VALUES,
  },
  palette: {
    mode: 'dark',
    primary: {
      main: '#5E92F3',
      light: '#90B9F8',
      dark: '#1565C0',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#4FB3BF',
      light: '#80D8E0',
      dark: '#00838F',
      contrastText: '#000000',
    },
    background: {
      default: '#0D1117',
      paper: '#161B22',
    },
    error: {
      main: '#F44336',
      light: '#EF9A9A',
      dark: '#C62828',
    },
    warning: {
      main: '#FFA726',
      light: '#FFCC80',
      dark: '#EF6C00',
    },
    success: {
      main: '#66BB6A',
      light: '#A5D6A7',
      dark: '#2E7D32',
    },
    info: {
      main: '#29B6F6',
      light: '#81D4FA',
      dark: '#0277BD',
    },
    text: {
      primary: '#E6EDF3',
      secondary: '#8D96A0',
      disabled: '#484F58',
    },
    divider: 'rgba(255, 255, 255, 0.08)',
    action: {
      hover: 'rgba(255, 255, 255, 0.04)',
      selected: 'rgba(255, 255, 255, 0.08)',
      disabled: 'rgba(255, 255, 255, 0.26)',
      disabledBackground: 'rgba(255, 255, 255, 0.12)',
    },
  },

  typography: muiTypography,

  shape: {
    borderRadius: RADIUS.md,
  },

  shadows: [
    'none',
    SHADOW.xs,
    SHADOW.sm,
    SHADOW.md,
    SHADOW.md,
    SHADOW.lg,
    SHADOW.lg,
    SHADOW.xl,
    SHADOW.xl,
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
    SHADOW['2xl'],
  ],

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: '#30363D #0D1117',
          '&::-webkit-scrollbar': { width: 8 },
          '&::-webkit-scrollbar-track': { background: '#0D1117' },
          '&::-webkit-scrollbar-thumb': {
            borderRadius: RADIUS.sm,
            background: '#30363D',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: RADIUS.md,
          padding: '8px 20px',
          boxShadow: 'none',
          '&:hover': { boxShadow: 'none' },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          boxShadow: SHADOW.sm,
          border: '1px solid rgba(255, 255, 255, 0.06)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
        },
      },
    },
    MuiInputBase: {
      styleOverrides: {
        root: {
          '& fieldset': {
            borderColor: 'rgba(255, 255, 255, 0.12)',
          },
        },
      },
    },
  },
});

export type DarkTheme = typeof darkTheme;
