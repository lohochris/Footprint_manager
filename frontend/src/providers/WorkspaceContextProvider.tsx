/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState } from 'react';

interface WorkspaceContextType {
  organizationId: string | null;
  workspaceId: string | null;
  permissions: string[];
  setWorkspace: (orgId: string, wsId: string) => void;
  setPermissions: (perms: string[]) => void;
}

const WorkspaceContext = createContext<WorkspaceContextType>({
  organizationId: null,
  workspaceId: null,
  permissions: [],
  setWorkspace: () => {},
  setPermissions: () => {},
});

export const useWorkspaceContext = () => useContext(WorkspaceContext);

export const WorkspaceContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [organizationId, setOrganizationId] = useState<string | null>(null);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [permissions, setPermissions] = useState<string[]>([]);

  const setWorkspace = (orgId: string, wsId: string) => {
    setOrganizationId(orgId);
    setWorkspaceId(wsId);
  };

  return (
    <WorkspaceContext.Provider
      value={{
        organizationId,
        workspaceId,
        permissions,
        setWorkspace,
        setPermissions,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
};
