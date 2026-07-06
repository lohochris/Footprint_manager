import { InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '../../store/authStore';

export const authRequestInterceptor = (config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};
