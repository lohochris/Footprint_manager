import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? '';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl,
    prepareHeaders: (headers) => {
      headers.set('Accept', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Health'],
  endpoints: (builder) => ({
    getHealth: builder.query<{ status: string; service: string }, void>({
      query: () => '/health/',
      providesTags: ['Health'],
    }),
  }),
});

export const { useGetHealthQuery } = apiSlice;
