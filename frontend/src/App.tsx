import React from 'react';
import { RouterProvider } from 'react-router-dom';
import { Provider } from 'react-redux';

import { store } from '@/store';
import { AppThemeProvider, TelemetryProvider } from '@/providers';
import { router } from '@/router';

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <TelemetryProvider>
        <AppThemeProvider>
          <RouterProvider router={router} />
        </AppThemeProvider>
      </TelemetryProvider>
    </Provider>
  );
};

export default App;
