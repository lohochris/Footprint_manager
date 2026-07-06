import React from 'react';
import { Box, Typography } from '@mui/material';

export const InspectorPanel: React.FC = () => {
  // In the future, this component will subscribe to a state showing currently inspected entity
  const isVisible = false;

  if (!isVisible) return null;

  return (
    <Box sx={{ 
      width: 320, 
      borderLeft: '1px solid', 
      borderColor: 'divider',
      backgroundColor: 'background.paper',
      padding: 2
    }}>
      <Typography variant="h6">Inspector</Typography>
      <Typography variant="body2" color="text.secondary">Select an entity to view details.</Typography>
    </Box>
  );
};
