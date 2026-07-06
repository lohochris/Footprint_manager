import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetObservabilityAlertsQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';

export const RecentAlertsWidget: React.FC<DashboardWidgetProps> = () => {
  // Alerts are often cross-workspace or system level
  const { data, isLoading, isFetching, error, refetch } = useGetObservabilityAlertsQuery(undefined, {
    pollingInterval: 30000 // Poll every 30s
  });

  if (error) {
    return (
      <WidgetCard title="Recent Alerts" isLoading={false} isFetching={false}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Failed to load recent alerts</p>
          <button
            onClick={() => refetch()}
            style={{
              background: 'transparent',
              border: '1px solid currentColor',
              color: 'inherit',
              padding: '0.25rem 0.75rem',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.75rem'
            }}
          >
            Retry
          </button>
        </div>
      </WidgetCard>
    );
  }

  // Safely extract the results array – the backend may return a paginated response
  // (with a `results` key) or a plain array; guard both shapes.
  const alerts = data?.results ?? [];
  const isEmpty = !isLoading && alerts.length === 0;

  const actionLink = (
    <Link to="/admin/observability/alerts" style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}>
      View all
    </Link>
  );

  const getSeverityColor = (severity: string) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL': return 'var(--color-danger-dark, #991b1b)';
      case 'HIGH': return 'var(--color-danger, #ef4444)';
      case 'MEDIUM': return 'var(--color-warning, #f59e0b)';
      default: return 'var(--color-info, #3b82f6)';
    }
  };

  return (
    <WidgetCard
      title="Recent Alerts"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={isEmpty}
      emptyMessage="No recent unacknowledged alerts."
      action={actionLink}
    >
      {alerts.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {alerts.map((alert) => (
            <li key={alert.id} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', padding: '0.5rem 0', borderBottom: '1px solid var(--color-border-subtle, #f3f4f6)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 500, color: getSeverityColor(alert.severity) }}>
                  {alert.severity}
                </span>
                <span style={{ fontSize: '0.65rem', color: 'var(--color-text-light, #9ca3af)' }}>
                  {new Date(alert.created_at).toLocaleString()}
                </span>
              </div>
              <span style={{ fontSize: '0.875rem', color: 'var(--color-text, #111827)' }}>{alert.message}</span>
            </li>
          ))}
        </ul>
      )}
    </WidgetCard>
  );
};
