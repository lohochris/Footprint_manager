import { apiSlice } from '@/store/api/apiSlice';

export interface WorkspaceOverview {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  status: string;
}

export interface ActiveInvestigation {
  id: string;
  title: string;
  status: string;
  priority: string;
  updated_at: string;
}

export interface PaginatedInvestigations {
  count: number;
  results: ActiveInvestigation[];
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  created_at: string;
  is_read: boolean;
}

export interface PaginatedNotifications {
  count: number;
  results: Notification[];
}

export interface ObservabilityHealth {
  status: string;
  components?: Record<string, string>;
  last_checked?: string;
}

// Phase 3C Interfaces
export interface EvidenceItem {
  id: string;
  type: string;
  status: string;
  created_at: string;
}

export interface PaginatedEvidence {
  count: number;
  results: EvidenceItem[];
}

export interface IdentityMatch {
  id: string;
  status: string;
  confidence_score: number;
  created_at: string;
}

export interface PaginatedIdentityMatches {
  count: number;
  results: IdentityMatch[];
}

export interface IntelligenceRecommendation {
  id: string;
  description: string;
  priority: string;
  created_at: string;
}

export interface PaginatedRecommendations {
  count: number;
  results: IntelligenceRecommendation[];
}

export interface GraphSnapshot {
  id: string;
  name: string;
  node_count: number;
  edge_count: number;
  created_at: string;
}

export interface PaginatedGraphSnapshots {
  count: number;
  results: GraphSnapshot[];
}

export interface ObservabilityAlert {
  id: string;
  severity: string;
  message: string;
  created_at: string;
  acknowledged: boolean;
}

export interface PaginatedAlerts {
  count: number;
  results: ObservabilityAlert[];
}

export interface AiSession {
  id: string;
  title: string;
  status: string;
  updated_at: string;
}

export interface PaginatedAiSessions {
  count: number;
  results: AiSession[];
}

export const dashboardApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getWorkspaceOverview: builder.query<WorkspaceOverview, string>({
      query: (workspaceId) => `/api/v1/workspaces/${workspaceId}/`,
    }),
    getActiveInvestigations: builder.query<PaginatedInvestigations, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/investigations/`,
        params: { workspace: workspaceId, limit: 5, ordering: '-updated_at' },
      }),
    }),
    getObservabilityHealth: builder.query<ObservabilityHealth, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/observability/health/`,
        params: { workspace: workspaceId },
      }),
    }),
    getCollaborationNotifications: builder.query<PaginatedNotifications, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/collaboration/notifications/`,
        params: { workspace: workspaceId, limit: 10, ordering: '-created_at' },
      }),
    }),
    getEvidenceSummary: builder.query<PaginatedEvidence, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/evidence/`,
        params: { workspace: workspaceId, limit: 5, ordering: '-created_at' },
      }),
    }),
    getIdentityMatches: builder.query<PaginatedIdentityMatches, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/identity/matches/`,
        params: { workspace: workspaceId, limit: 5, status: 'PENDING', ordering: '-created_at' },
      }),
    }),
    getIntelligenceRecommendations: builder.query<PaginatedRecommendations, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/intelligence/recommendations/`,
        params: { workspace: workspaceId, limit: 5, ordering: '-created_at' },
      }),
    }),
    getGraphSnapshots: builder.query<PaginatedGraphSnapshots, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/graph/snapshots/`,
        params: { workspace: workspaceId, limit: 5, ordering: '-created_at' },
      }),
    }),
    getObservabilityAlerts: builder.query<PaginatedAlerts, void>({
      query: () => ({
        url: `/api/v1/observability/alerts/`,
        params: { limit: 5, acknowledged: false, ordering: '-created_at' },
      }),
    }),
    getAiSessions: builder.query<PaginatedAiSessions, { workspaceId: string }>({
      query: ({ workspaceId }) => ({
        url: `/api/v1/ai/sessions/`,
        params: { workspace: workspaceId, limit: 3, ordering: '-updated_at' },
      }),
    }),
  }),
  overrideExisting: false,
});

export const {
  useGetWorkspaceOverviewQuery,
  useGetActiveInvestigationsQuery,
  useGetObservabilityHealthQuery,
  useGetCollaborationNotificationsQuery,
  useGetEvidenceSummaryQuery,
  useGetIdentityMatchesQuery,
  useGetIntelligenceRecommendationsQuery,
  useGetGraphSnapshotsQuery,
  useGetObservabilityAlertsQuery,
  useGetAiSessionsQuery,
} = dashboardApi;
