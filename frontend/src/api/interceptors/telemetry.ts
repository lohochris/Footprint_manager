import { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { TelemetryService } from '../../telemetry/TelemetryService';

export const telemetryRequestInterceptor = (config: InternalAxiosRequestConfig) => {
  // @ts-ignore
  config.metadata = { startTime: new Date() };
  TelemetryService.emit('ApiRequestStarted', { url: config.url, method: config.method });
  return config;
};

export const telemetryResponseInterceptor = (response: AxiosResponse) => {
  // @ts-ignore
  const duration = new Date().getTime() - response.config.metadata.startTime.getTime();
  TelemetryService.emit('ApiRequestCompleted', { 
    url: response.config.url, 
    status: response.status,
    duration 
  });
  return response;
};

export const telemetryErrorInterceptor = (error: AxiosError) => {
  TelemetryService.emit('ApiRequestFailed', { 
    url: error.config?.url,
    status: error.response?.status,
    message: error.message
  });
  return Promise.reject(error);
};
