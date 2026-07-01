import {
  AppBar,
  Box,
  IconButton,
  Toolbar,
  Typography,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import FingerprintIcon from '@mui/icons-material/Fingerprint';

import { useAppDispatch } from '@/hooks/useAppDispatch';
import { toggleSidebar } from '@/store/slices/appSlice';

export function AppHeader() {
  const dispatch = useAppDispatch();

  return (
    <AppBar
      position="fixed"
      elevation={0}
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        bgcolor: 'background.paper',
        color: 'text.primary',
        borderBottom: 1,
        borderColor: 'divider',
      }}
    >
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="toggle sidebar"
          onClick={() => dispatch(toggleSidebar())}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>
        <FingerprintIcon color="primary" sx={{ mr: 1 }} />
        <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
          Footprint Manager
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Typography variant="body2" color="text.secondary">
          Sprint 0 — Infrastructure
        </Typography>
      </Toolbar>
    </AppBar>
  );
}
