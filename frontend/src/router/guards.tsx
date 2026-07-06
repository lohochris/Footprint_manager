import React from 'react';
import { Navigate, Outlet, useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '@/store';
import { setActiveWorkspace } from '@/store/slices/authSlice';

export const RequireAuth: React.FC = () => {
  const { isAuthenticated, bootstrapStatus } = useSelector((state: RootState) => state.auth);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Ensure bootstrap is successful before rendering protected content
  if (bootstrapStatus !== 'success') {
    // AuthProvider will render a loader while bootstrapping
    return null;
  }

  return <Outlet />;
};

export const RequireGuest: React.FC = () => {
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

export const RequireWorkspace: React.FC = () => {
  const { workspaceId } = useParams<{ workspaceId: string }>();
  const dispatch = useDispatch();
  const { activeWorkspaceId, workspaces } = useSelector((state: RootState) => state.auth);

  // Validate the URL parameter against user's actual workspaces
  const isValidWorkspace = workspaces.some(w => w.id.toString() === workspaceId || w.slug === workspaceId);

  if (!isValidWorkspace) {
    // If not a valid workspace, redirect to a workspace selector or a default workspace
    if (workspaces.length > 0) {
      return <Navigate to={`/workspace/${workspaces[0].slug}/dashboard`} replace />;
    }
    // Handle the case where they have no workspaces
    return <div>You do not belong to any workspaces.</div>;
  }

  // Ensure Redux state is synced with the validated URL
  if (workspaceId && workspaceId !== activeWorkspaceId) {
    // Using setTimeout to avoid update-during-render warning
    setTimeout(() => {
        dispatch(setActiveWorkspace(workspaceId));
    }, 0);
  }

  return <Outlet />;
};
