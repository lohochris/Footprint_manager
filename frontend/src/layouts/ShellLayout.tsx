import React from 'react';
import { Box } from '@mui/material';
import { Header, LeftNav, MainWorkspace, InspectorPanel, ActivityPanel } from './regions';

export const ShellLayout: React.FC = () => {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      <Header />
      <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
        <LeftNav />
        <MainWorkspace />
        <InspectorPanel />
        <ActivityPanel />
      </Box>
    </Box>
  );
};
