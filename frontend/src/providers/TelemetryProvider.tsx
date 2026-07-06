/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect } from 'react';

interface TelemetryContextType {
  trackEvent: (eventName: string, properties?: Record<string, any>) => void;
  trackPageView: (pageName: string) => void;
  trackError: (error: Error, info?: any) => void;
}

const TelemetryContext = createContext<TelemetryContextType>({
  trackEvent: () => {},
  trackPageView: () => {},
  trackError: () => {},
});

export const useTelemetry = () => useContext(TelemetryContext);

export const TelemetryProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  useEffect(() => {
    // Initialize telemetry (e.g., Application Insights, DataDog, etc.)
    console.log('[Telemetry] Initialized');
  }, []);

  const trackEvent = (eventName: string, properties?: Record<string, any>) => {
    console.log(`[Telemetry] Event: ${eventName}`, properties);
  };

  const trackPageView = (pageName: string) => {
    console.log(`[Telemetry] PageView: ${pageName}`);
  };

  const trackError = (error: Error, info?: any) => {
    console.error(`[Telemetry] Error: ${error.message}`, info);
  };

  return (
    <TelemetryContext.Provider value={{ trackEvent, trackPageView, trackError }}>
      {children}
    </TelemetryContext.Provider>
  );
};
