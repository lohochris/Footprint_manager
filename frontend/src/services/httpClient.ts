import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL ?? '';

export const httpClient = axios.create({
  baseURL,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

httpClient.interceptors.request.use((config) => {
  const requestId = crypto.randomUUID();
  config.headers['X-Request-ID'] = requestId;
  config.headers['X-Correlation-ID'] = requestId;
  return config;
});
