import { Alert, Card, CardContent, CircularProgress, Typography } from '@mui/material';

import { useGetHealthQuery } from '@/store/api/apiSlice';

export function HealthStatus() {
  const { data, isLoading, isError, error } = useGetHealthQuery();

  if (isLoading) {
    return (
      <Card>
        <CardContent sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CircularProgress size={24} />
          <Typography>Checking backend health...</Typography>
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return (
      <Alert severity="error">
        Backend unreachable:{' '}
        {'status' in (error as object) ? String((error as { status: unknown }).status) : 'Network error'}
      </Alert>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Backend Health
        </Typography>
        <Alert severity={data?.status === 'healthy' ? 'success' : 'warning'}>
          Service: {data?.service} — Status: {data?.status}
        </Alert>
      </CardContent>
    </Card>
  );
}
