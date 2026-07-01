import { createTheme } from '@mui/material/styles';

import { BREAKPOINT_VALUES } from './breakpoints';
import { darkTheme } from './dark';
import { muiTypography } from './typography';
import { COLOR, RADIUS, SHADOW } from './tokens';

export const lightTheme = createTheme({
  breakpoints: {
    values: BREAKPOINT_VALUES,
  },
  palette: {
    mode: 'light',
    primary: {
      main: COLOR.brand[700],
      light: COLOR.brand[400],
      dark: COLOR.brand[800],
      contrastText: COLOR.neutral[0],
    },
    secondary: {
      main: COLOR.teal[500],
      light: '#4FB3BF',
      dark: COLOR.teal[700],
      contrastText: COLOR.neutral[0],
    },
    background: {
      default: COLOR.neutral[50],
      paper: COLOR.neutral[0],
    },
    error: {
      main: COLOR.error,
    },
    warning: {
      main: COLOR.warning,
    },
    success: {
      main: COLOR.success,
    },
    info: {
      main: COLOR.info,
    },
    text: {
      primary: COLOR.neutral[900],
      secondary: COLOR.neutral[600],
      disabled: COLOR.neutral[400],
    },
    divider: COLOR.neutral[200],
  },
  typography: muiTypography,
  shape: {
    borderRadius: RADIUS.md,
  },
  components: {
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
          boxShadow: SHADOW.sm,
        },
      },
    },
  },
});

export const theme = lightTheme;
export { darkTheme };
export type AppTheme = typeof lightTheme;
