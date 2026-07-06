import React from 'react';
import { Box, Typography } from '@mui/material';

export const ActivityPanel: React.FC = () => {
  // In the future, this component will subscribe to real-time activity and alerts
  const isVisible = false;

  if (!isVisible) return null;

  return (
    <Box sx={{ 
      width: 280, 
      borderLeft: '1px solid', 
      borderColor: 'divider',
      backgroundColor: 'background.paper',
      padding: 2
    }}>
      <Typography variant="h6">Activity</Typography>
      <Typography variant="body2" color="text.secondary">Recent activity stream.</Typography>
    </Box>
  );
};
