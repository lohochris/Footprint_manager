import { fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import type { BaseQueryFn, FetchArgs, FetchBaseQueryError } from '@reduxjs/toolkit/query';
import { RootState } from '../index';
import { logout, setCredentials } from '../slices/authSlice';

const baseQuery = fetchBaseQuery({
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  prepareHeaders: (headers, { getState }) => {
    headers.set('Accept', 'application/json');
    // We can only access the RootState if it's properly typed and avoids circular dependencies.
    // Ensure `store.ts` imports authSlice correctly.
    const token = (getState() as RootState).auth?.accessToken;
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

export const baseQueryWithReauth: BaseQueryFn<
  string | FetchArgs,
  unknown,
  FetchBaseQueryError
> = async (args, api, extraOptions) => {
  // Wait until the mutex is available without locking it
  let result = await baseQuery(args, api, extraOptions);
  
  if (result.error && result.error.status === 401) {
    const refreshToken = (api.getState() as RootState).auth?.refreshToken;
    if (refreshToken) {
      // try to get a new token
      const refreshResult = await baseQuery(
        { url: '/api/v1/auth/jwt/refresh/', method: 'POST', body: { refresh: refreshToken } },
        api,
        extraOptions
      );
      if (refreshResult.data) {
        // store the new token
        api.dispatch(setCredentials({ 
          accessToken: (refreshResult.data as any).access, 
          refreshToken: (refreshResult.data as any).refresh || refreshToken 
        }));
        // retry the initial query
        result = await baseQuery(args, api, extraOptions);
      } else {
        api.dispatch(logout());
      }
    } else {
      api.dispatch(logout());
    }
  }
  return result;
};
