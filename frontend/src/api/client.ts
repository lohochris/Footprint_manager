import axios from 'axios';
import { authRequestInterceptor } from './interceptors/auth';
import { errorResponseInterceptor } from './interceptors/errors';
import { 
  telemetryRequestInterceptor, 
  telemetryResponseInterceptor, 
  telemetryErrorInterceptor 
} from './interceptors/telemetry';

export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptors
apiClient.interceptors.request.use(authRequestInterceptor);
apiClient.interceptors.request.use(telemetryRequestInterceptor);

// Response Interceptors
apiClient.interceptors.response.use(
  telemetryResponseInterceptor,
  (error) => {
    telemetryErrorInterceptor(error);
    return errorResponseInterceptor(error);
  }
);
