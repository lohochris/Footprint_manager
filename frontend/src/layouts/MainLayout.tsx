import { Outlet } from 'react-router-dom';
import { Box, Container } from '@mui/material';

import { AppHeader } from '@/components/AppHeader';
import { AppSidebar } from '@/components/AppSidebar';
import { useAppSelector } from '@/hooks/useAppSelector';

export function MainLayout() {
  const sidebarOpen = useAppSelector((state) => state.app.sidebarOpen);

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <AppHeader />
      <AppSidebar open={sidebarOpen} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          pt: 8,
          pl: sidebarOpen ? '240px' : '64px',
          transition: 'padding-left 0.2s ease',
        }}
      >
        <Container maxWidth="xl" sx={{ py: 3 }}>
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
}
