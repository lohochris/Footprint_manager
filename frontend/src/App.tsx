import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { Provider } from 'react-redux';

import { store } from '@/store';
import { AppThemeProvider, TelemetryProvider } from '@/providers';
import { AuthProvider } from '@/providers/AuthProvider';
import { router } from '@/router';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <TelemetryProvider>
        <AppThemeProvider>
          <AuthProvider>
            <RouterProvider router={router} />
          </AuthProvider>
        </AppThemeProvider>
      </TelemetryProvider>
    </Provider>
  );
};

export default App;
