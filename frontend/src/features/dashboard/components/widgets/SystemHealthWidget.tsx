import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetObservabilityHealthQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';

export const SystemHealthWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetObservabilityHealthQuery(
    { workspaceId }, 
    { pollingInterval: 300000 } // Poll every 5 minutes (static/cached)
  );

  const actionLink = (
    <Link to="/admin/observability" style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}>
      View details
    </Link>
  );

  const getStatusColor = (status: string) => {
    switch (status?.toUpperCase()) {
      case 'HEALTHY':
      case 'OK':
      case 'PASS':
        return 'var(--color-success, #10b981)';
      case 'WARNING':
      case 'DEGRADED':
        return 'var(--color-warning, #f59e0b)';
      default:
        return 'var(--color-danger, #ef4444)';
    }
  };

  return (
    <WidgetCard
      title="System Health"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={!isLoading && !data && !error}
      action={actionLink}
    >
      {error ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0' }}>Unable to load system health</p>
          <button 
            onClick={() => refetch()}
            style={{ padding: '0.25rem 0.75rem', background: 'transparent', border: '1px solid currentColor', borderRadius: '4px', color: 'inherit', cursor: 'pointer', fontSize: '0.875rem' }}
          >
            Retry
          </button>
        </div>
      ) : data ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', height: '100%' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ 
              display: 'inline-block', 
              width: '12px', 
              height: '12px', 
              borderRadius: '50%', 
              backgroundColor: getStatusColor(data.status) 
            }} />
            <h3 style={{ margin: 0, fontSize: '1.25rem' }}>{data.status || 'UNKNOWN'}</h3>
          </div>
          
          {data.components && Object.keys(data.components).length > 0 && (
            <div style={{ marginTop: '0.5rem' }}>
              <h4 style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem' }}>Components:</h4>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem' }}>
                {Object.entries(data.components).map(([key, status]) => (
                  <li key={key}>{key}: {status}</li>
                ))}
              </ul>
            </div>
          )}

          {data.last_checked && (
             <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)', marginTop: '1rem' }}>
               Last checked: {new Date(data.last_checked).toLocaleTimeString()}
             </div>
          )}
        </div>
      ) : null}
    </WidgetCard>
  );
};
