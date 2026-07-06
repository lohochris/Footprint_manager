import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetGraphSnapshotsQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';
import { routes } from '@/router/routes';

export const GraphActivityWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  // Heavy data: fetch on demand rather than poll frequently
  const { data, isLoading, isFetching, error, refetch } = useGetGraphSnapshotsQuery(
    { workspaceId }
  );

  if (error) {
    return (
      <WidgetCard title="Graph Activity" isLoading={false} isFetching={false}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Failed to load graph snapshots</p>
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

  const snapshots = data?.results ?? [];
  const isEmpty = !isLoading && snapshots.length === 0;

  const actionLink = (
    <Link to={routes.graph(workspaceId)} style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}>
      Open Graph View
    </Link>
  );

  return (
    <WidgetCard
      title="Graph Activity"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={isEmpty}
      emptyMessage="No graph snapshots available."
      action={actionLink}
    >
      {snapshots.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {snapshots.map((snapshot) => (
            <li key={snapshot.id} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', padding: '0.75rem', border: '1px solid var(--color-border-subtle, #f3f4f6)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{snapshot.name || 'Snapshot'}</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)' }}>
                  {new Date(snapshot.created_at).toLocaleDateString()}
                </span>
              </div>
              <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)' }}>
                <span>Nodes: <strong>{snapshot.node_count}</strong></span>
                <span>Edges: <strong>{snapshot.edge_count}</strong></span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </WidgetCard>
  );
};
