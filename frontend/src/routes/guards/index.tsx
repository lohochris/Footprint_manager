import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export const RequireAuth: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuthStore();
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export const RequirePermission: React.FC<{ permission: string; children: React.ReactNode }> = ({ permission, children }) => {
  const { user } = useAuthStore();
  
  // Example permission check
  if (!user?.permissions?.includes(permission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export const RequireOrganization: React.FC<{ organizationId: string; children: React.ReactNode }> = ({ organizationId, children }) => {
  const { user } = useAuthStore();
  
  if (user?.organizationId !== organizationId) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};

export const RequireWorkspace: React.FC<{ workspaceId: string; children: React.ReactNode }> = ({ workspaceId, children }) => {
  const { user } = useAuthStore();
  
  if (user?.workspaceId !== workspaceId) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
