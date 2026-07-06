import React from 'react';
import { useRouteError, isRouteErrorResponse } from 'react-router-dom';
import { Box, Typography, Button } from '@mui/material';

export const GlobalErrorBoundary: React.FC = () => {
  const error = useRouteError();
  
  let errorMessage = 'An unexpected error occurred.';
  if (isRouteErrorResponse(error)) {
    errorMessage = error.statusText || error.data;
  } else if (error instanceof Error) {
    errorMessage = error.message;
  }

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      height: '100vh',
      padding: 4,
      textAlign: 'center'
    }}>
      <Typography variant="h4" color="error" gutterBottom>
        Oops! Something went wrong.
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
        {errorMessage}
      </Typography>
      <Button variant="contained" onClick={() => window.location.href = '/'}>
        Return to Home
      </Button>
    </Box>
  );
};
