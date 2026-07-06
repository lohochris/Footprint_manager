import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetWorkspaceOverviewQuery } from '../../api/dashboardApi';

export const WorkspaceOverviewWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetWorkspaceOverviewQuery(workspaceId);

  if (error) {
    return (
      <WidgetCard title="Workspace Overview" isLoading={false} isFetching={false}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Failed to load workspace overview</p>
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

  return (
    <WidgetCard
      title="Workspace Overview"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={!isLoading && !data}
    >
      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h3 style={{ margin: 0 }}>{data.name}</h3>
          <p style={{ margin: 0, color: 'var(--color-text-muted, #6b7280)' }}>{data.description || 'No description available'}</p>
          <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
            <span style={{ fontWeight: 600 }}>Status:</span> {data.status}
          </div>
          <div style={{ fontSize: '0.875rem' }}>
            <span style={{ fontWeight: 600 }}>Created:</span> {new Date(data.created_at).toLocaleDateString()}
          </div>
        </div>
      )}
    </WidgetCard>
  );
};
