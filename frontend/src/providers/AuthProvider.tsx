import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Box, CircularProgress } from '@mui/material';

import { RootState } from '@/store';
import { useLazyBootstrapQuery } from '@/store/api/authApi';
import { setBootstrapData, setBootstrapStatus, logout } from '@/store/slices/authSlice';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const dispatch = useDispatch();
  const { isAuthenticated, bootstrapStatus } = useSelector((state: RootState) => state.auth);
  const [triggerBootstrap] = useLazyBootstrapQuery();

  useEffect(() => {
    if (isAuthenticated && bootstrapStatus === 'idle') {
      dispatch(setBootstrapStatus('loading'));
      triggerBootstrap()
        .unwrap()
        .then((data) => {
          dispatch(setBootstrapData(data));
        })
        .catch((err) => {
          console.error('Bootstrap failed', err);
          dispatch(logout());
        });
    }
  }, [isAuthenticated, bootstrapStatus, triggerBootstrap, dispatch]);

  if (bootstrapStatus === 'loading') {
    return (
      <Box sx={{ display: 'flex', height: '100vh', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  return <>{children}</>;
};
