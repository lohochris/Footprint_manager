import { TelemetryEvent, TelemetryEventName } from './events';

export class TelemetryService {
  private static buffer: TelemetryEvent[] = [];
  
  static emit(name: TelemetryEventName, payload: any) {
    const event: TelemetryEvent = {
      name,
      payload,
      timestamp: new Date().toISOString()
    };
    
    this.buffer.push(event);
    
    // In a real implementation, we would flush this buffer periodically or on page unload
    // console.log('[Telemetry]', event);
  }
  
  static flush() {
    // Send to backend observabliity endpoint
    // apiClient.post('/observability/telemetry', { events: this.buffer })
    this.buffer = [];
  }
}
