export interface HealthResponse {
  status: string;
  service: string;
}

export interface ReadinessResponse {
  status: string;
  checks: Record<string, string>;
}

export interface ApiError {
  detail: string;
  code?: string;
}
