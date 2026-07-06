import { createApi } from '@reduxjs/toolkit/query/react';

import { baseQueryWithReauth } from './baseQuery';

export const apiSlice = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['Health'],
  endpoints: (builder) => ({
    getHealth: builder.query<{ status: string; service: string }, void>({
      query: () => '/health/',
      providesTags: ['Health'],
    }),
  }),
});

export const { useGetHealthQuery } = apiSlice;
