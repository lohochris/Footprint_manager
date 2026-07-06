/**
 * Central route definitions for Footprint Manager.
 *
 * Every widget, sidebar item, and navigation action must import from here.
 * Changing a path in one place propagates everywhere automatically.
 */

export const routes = {
  /** Root → redirects to default workspace dashboard */
  root: () => '/',

  /** Login page */
  login: () => '/login',

  /** Workspace-scoped routes */
  dashboard: (workspaceId: string) => `/workspace/${workspaceId}/dashboard`,
  investigations: (workspaceId: string) => `/workspace/${workspaceId}/investigations`,
  investigation: (workspaceId: string, id: string) => `/workspace/${workspaceId}/investigations/${id}`,
  evidence: (workspaceId: string) => `/workspace/${workspaceId}/evidence`,
  identity: (workspaceId: string) => `/workspace/${workspaceId}/identity`,
  graph: (workspaceId: string) => `/workspace/${workspaceId}/graph`,
  timeline: (workspaceId: string) => `/workspace/${workspaceId}/timeline`,
  intelligence: (workspaceId: string) => `/workspace/${workspaceId}/intelligence`,
  integrations: (workspaceId: string) => `/workspace/${workspaceId}/integrations`,

  /** AI Assistant */
  ai: (workspaceId: string) => `/workspace/${workspaceId}/ai`,
  aiSession: (workspaceId: string, sessionId: string) =>
    `/workspace/${workspaceId}/ai/${sessionId}`,
  aiNewSession: (workspaceId: string) => `/workspace/${workspaceId}/ai?new=true`,

  /** Admin routes */
  adminObservability: () => '/admin/observability',
  adminAlerts: () => '/admin/observability/alerts',
  adminSettings: () => '/admin/settings',
} as const;
