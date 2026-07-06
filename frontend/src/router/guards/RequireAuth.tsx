import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';

// In a real application, this would check the Redux state or AuthContext
const useAuth = () => {
  // Placeholder implementation
  return { isAuthenticated: true };
};

export const RequireAuth: React.FC = () => {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
