import { AxiosError } from 'axios';
import { useAuthStore } from '../../store/authStore';

export const errorResponseInterceptor = (error: AxiosError) => {
  if (error.response?.status === 401) {
    useAuthStore.getState().logout();
    window.location.href = '/login';
  }
  return Promise.reject(error);
};
