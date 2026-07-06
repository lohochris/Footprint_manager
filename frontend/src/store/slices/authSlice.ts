import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type BootstrapStatus = 'idle' | 'loading' | 'success' | 'failed';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  profile: any;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  description: string;
}

export interface Workspace {
  id: number;
  name: string;
  slug: string;
  description: string;
}

export interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  organizations: Organization[];
  workspaces: Workspace[];
  activeWorkspaceId: string | null;
  isAuthenticated: boolean;
  bootstrapStatus: BootstrapStatus;
}

// Retrieve initial state from local storage securely
const initialAccessToken = localStorage.getItem('accessToken');
const initialRefreshToken = localStorage.getItem('refreshToken');
const initialWorkspaceId = localStorage.getItem('activeWorkspaceId');

const initialState: AuthState = {
  accessToken: initialAccessToken,
  refreshToken: initialRefreshToken,
  user: null,
  organizations: [],
  workspaces: [],
  activeWorkspaceId: initialWorkspaceId,
  isAuthenticated: !!initialAccessToken,
  bootstrapStatus: 'idle',
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (
      state,
      action: PayloadAction<{ accessToken: string; refreshToken: string }>
    ) => {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      state.isAuthenticated = true;
      localStorage.setItem('accessToken', action.payload.accessToken);
      localStorage.setItem('refreshToken', action.payload.refreshToken);
    },
    setBootstrapData: (
      state,
      action: PayloadAction<{ user: User; organizations: Organization[]; workspaces: Workspace[] }>
    ) => {
      state.user = action.payload.user;
      state.organizations = action.payload.organizations;
      state.workspaces = action.payload.workspaces;
      state.bootstrapStatus = 'success';
      
      // Validate workspace against payload
      if (state.activeWorkspaceId) {
        const isValid = state.workspaces.some(w => w.id.toString() === state.activeWorkspaceId || w.slug === state.activeWorkspaceId);
        if (!isValid) {
            state.activeWorkspaceId = null;
            localStorage.removeItem('activeWorkspaceId');
        }
      }
    },
    setBootstrapStatus: (state, action: PayloadAction<BootstrapStatus>) => {
      state.bootstrapStatus = action.payload;
    },
    setActiveWorkspace: (state, action: PayloadAction<string>) => {
      state.activeWorkspaceId = action.payload;
      localStorage.setItem('activeWorkspaceId', action.payload);
    },
    logout: (state) => {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.organizations = [];
      state.workspaces = [];
      state.activeWorkspaceId = null;
      state.isAuthenticated = false;
      state.bootstrapStatus = 'idle';
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('activeWorkspaceId');
    },
  },
});

export const { setCredentials, setBootstrapData, setBootstrapStatus, setActiveWorkspace, logout } = authSlice.actions;

export default authSlice.reducer;
