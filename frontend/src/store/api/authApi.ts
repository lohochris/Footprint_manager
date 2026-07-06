import { apiSlice } from './apiSlice';

export const authApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    login: builder.mutation<any, { email: string; password: string }>({
      query: (credentials) => ({
        url: '/api/v1/auth/jwt/create/',
        method: 'POST',
        body: credentials,
      }),
    }),
    bootstrap: builder.query<any, void>({
      query: () => '/api/v1/auth/bootstrap/',
    }),
  }),
});

export const { useLoginMutation, useBootstrapQuery, useLazyBootstrapQuery } = authApi;
