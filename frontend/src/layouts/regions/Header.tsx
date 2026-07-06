import React from 'react';
import { Box, Typography, IconButton } from '@mui/material';
import { useThemeContext } from '@/providers';
import { Menu, Search, Notifications, Brightness4, Brightness7 } from '@mui/icons-material';

export const Header: React.FC = () => {
  const { mode, toggleTheme } = useThemeContext();

  return (
    <Box sx={{ 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      padding: '0 24px',
      height: '64px',
      borderBottom: '1px solid',
      borderColor: 'divider',
      backgroundColor: 'background.paper'
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton edge="start" color="inherit" aria-label="menu">
          <Menu />
        </IconButton>
        <Typography variant="h6" noWrap component="div">
          Footprint Manager
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton color="inherit"><Search /></IconButton>
        <IconButton color="inherit"><Notifications /></IconButton>
        <IconButton color="inherit" onClick={toggleTheme}>
          {mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
      </Box>
    </Box>
  );
};
