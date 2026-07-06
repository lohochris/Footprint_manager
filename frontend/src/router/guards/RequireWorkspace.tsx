import React from 'react';
import { Navigate, Outlet, useParams } from 'react-router-dom';
import { useWorkspaceContext } from '@/providers';

export const RequireWorkspace: React.FC = () => {
  const { workspaceId } = useParams();
  const { setWorkspace } = useWorkspaceContext();

  React.useEffect(() => {
    if (workspaceId) {
      // In a real implementation, you might fetch orgId from backend based on workspaceId
      setWorkspace('org-123', workspaceId);
    }
  }, [workspaceId, setWorkspace]);

  if (!workspaceId) {
    return <Navigate to="/select-workspace" replace />;
  }

  return <Outlet />;
};
