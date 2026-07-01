import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AppState {
  sidebarOpen: boolean;
  apiVersion: string;
}

const initialState: AppState = {
  sidebarOpen: true,
  apiVersion: 'v1',
};

const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
  },
});

export const { toggleSidebar, setSidebarOpen } = appSlice.actions;
export default appSlice.reducer;
