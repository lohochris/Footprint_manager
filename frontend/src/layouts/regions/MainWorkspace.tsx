import React, { Suspense } from 'react';
import { Box, CircularProgress } from '@mui/material';
import { Outlet } from 'react-router-dom';

export const MainWorkspace: React.FC = () => {
  return (
    <Box sx={{ 
      flexGrow: 1, 
      display: 'flex', 
      flexDirection: 'column',
      overflow: 'hidden',
      backgroundColor: 'background.default'
    }}>
      <Suspense fallback={
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
          <CircularProgress />
        </Box>
      }>
        <Outlet />
      </Suspense>
    </Box>
  );
};
