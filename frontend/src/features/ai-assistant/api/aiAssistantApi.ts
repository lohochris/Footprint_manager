import { apiSlice } from '@/store/api/apiSlice';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AiSession {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedAiSessions {
  count: number;
  results: AiSession[];
}

export interface AiMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface PaginatedAiMessages {
  count: number;
  results: AiMessage[];
}

export interface CreateSessionResponse {
  id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
}

// ─── API Slice Injection ───────────────────────────────────────────────────────

export const aiAssistantApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    /** List sessions for a workspace */
    listAiSessions: builder.query<PaginatedAiSessions, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: '/api/v1/ai/sessions/',
        params: { workspace: workspaceId, ordering: '-updated_at' },
      }),
      providesTags: ['AiSessions'],
    }),

    /** Fetch messages in a session */
    listAiMessages: builder.query<PaginatedAiMessages, { sessionId: string }>({
      query: ({ sessionId }) => ({
        url: `/api/v1/ai/sessions/${sessionId}/messages/`,
        params: { ordering: 'created_at' },
      }),
      providesTags: (_result, _error, { sessionId }) => [{ type: 'AiMessages', id: sessionId }],
    }),

    /** Create a new session */
    createAiSession: builder.mutation<CreateSessionResponse, { workspaceId: string; title?: string }>({
      query: ({ workspaceId, title }) => ({
        url: '/api/v1/ai/sessions/',
        method: 'POST',
        body: { workspace: workspaceId, title: title ?? 'New Session' },
      }),
      invalidatesTags: ['AiSessions'],
    }),

    /** Send a message to a session */
    sendAiMessage: builder.mutation<AiMessage, { sessionId: string; content: string }>({
      query: ({ sessionId, content }) => ({
        url: `/api/v1/ai/sessions/${sessionId}/messages/`,
        method: 'POST',
        body: { content, role: 'user' },
      }),
      invalidatesTags: (_result, _error, { sessionId }) => [{ type: 'AiMessages', id: sessionId }],
    }),
  }),
  overrideExisting: false,
});

export const {
  useListAiSessionsQuery,
  useListAiMessagesQuery,
  useCreateAiSessionMutation,
  useSendAiMessageMutation,
} = aiAssistantApi;
