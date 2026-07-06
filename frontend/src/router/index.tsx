/* eslint-disable react-refresh/only-export-components */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ShellLayout } from '@/layouts/ShellLayout';
import { RequireAuth, RequireGuest, RequireWorkspace } from './guards';
import { GlobalErrorBoundary } from '@/components/GlobalErrorBoundary';
import { LoginView } from '@/features/auth/views/LoginView';

// Placeholder empty components to satisfy Phase 1 routing structure
// In subsequent phases, these will be replaced with actual Lazy-loaded feature components
const PlaceholderComponent = ({ title }: { title: string }) => (
  <div style={{ padding: 24 }}><h2>{title}</h2></div>
);

export const router = createBrowserRouter([
  {
    path: '/',
    errorElement: <GlobalErrorBoundary />,
    element: <RequireAuth />,
    children: [
      {
        index: true,
        element: <Navigate to="/workspace/default/dashboard" replace />
      },
      {
        path: 'select-workspace',
        element: <PlaceholderComponent title="Workspace Selection" />
      },
      {
        path: 'workspace/:workspaceId',
        element: <RequireWorkspace />,
        children: [
          {
            element: <ShellLayout />,
            children: [
              { index: true, element: <Navigate to="dashboard" replace /> },
              { path: 'dashboard', element: <PlaceholderComponent title="Dashboard" /> },
              { path: 'investigations', element: <PlaceholderComponent title="Investigations" /> },
              { path: 'investigations/:id', element: <PlaceholderComponent title="Investigation Details" /> },
              { path: 'evidence', element: <PlaceholderComponent title="Evidence Workspace" /> },
              { path: 'identity', element: <PlaceholderComponent title="Identity Resolution" /> },
              { path: 'graph', element: <PlaceholderComponent title="Graph Intelligence" /> },
              { path: 'timeline', element: <PlaceholderComponent title="Timeline Intelligence" /> },
              { path: 'intelligence', element: <PlaceholderComponent title="Intelligence" /> },
              { path: 'integrations', element: <PlaceholderComponent title="Integrations" /> },
            ]
          }
        ]
      },
      {
        path: 'admin',
        // element: <RequireAdmin><AdminLayout /></RequireAdmin>,
        element: <PlaceholderComponent title="Admin Settings" />,
        children: [
          { path: 'settings', element: <PlaceholderComponent title="Settings" /> },
          { path: 'observability', element: <PlaceholderComponent title="Observability" /> },
        ]
      }
    ]
  },
  {
    path: '/login',
    element: <RequireGuest />,
    children: [
      { index: true, element: <LoginView /> }
    ]
  }
]);
