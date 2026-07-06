import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetActiveInvestigationsQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';
import { routes } from '@/router/routes';

export const ActiveInvestigationsWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetActiveInvestigationsQuery(
    { workspaceId },
    { pollingInterval: 60000 } // 60s polling
  );

  const actionLink = (
    <Link to={routes.investigations(workspaceId)} style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}>
      View all
    </Link>
  );

  if (error) {
    return (
      <WidgetCard title="Active Investigations" isLoading={false} isFetching={false} action={actionLink}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Unable to load active investigations</p>
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

  const investigations = data?.results ?? [];
  const isEmpty = !isLoading && investigations.length === 0;

  return (
    <WidgetCard
      title="Active Investigations"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={isEmpty}
      emptyMessage="No active investigations found."
      action={actionLink}
    >
      {investigations.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {investigations.map((inv) => (
            <li key={inv.id} style={{ padding: '0.75rem', background: 'var(--color-bg-subtle, #f3f4f6)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                <span style={{ fontWeight: 600 }}>{inv.title}</span>
                <span style={{ fontSize: '0.75rem', padding: '0.125rem 0.375rem', background: 'var(--color-primary-subtle, #dbeafe)', color: 'var(--color-primary-dark, #1e40af)', borderRadius: '4px' }}>
                  {inv.priority}
                </span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)', display: 'flex', justifyContent: 'space-between' }}>
                <span>Status: {inv.status}</span>
                <span>Updated: {new Date(inv.updated_at).toLocaleDateString()}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </WidgetCard>
  );
};
