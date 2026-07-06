export type TelemetryEventName = 
  | 'RouteVisited'
  | 'ApiRequestStarted'
  | 'ApiRequestCompleted'
  | 'ApiRequestFailed'
  | 'ComponentError'
  | 'PerformanceMetric'
  | 'UserInteraction';

export interface TelemetryEvent {
  name: TelemetryEventName;
  payload: any;
  timestamp: string;
}
