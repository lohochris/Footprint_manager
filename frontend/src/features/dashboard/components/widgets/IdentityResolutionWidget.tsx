import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetIdentityMatchesQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';
import { routes } from '@/router/routes';

export const IdentityResolutionWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetIdentityMatchesQuery(
    { workspaceId },
    { pollingInterval: 60000 }
  );

  if (error) {
    return (
      <WidgetCard title="Identity Resolution" isLoading={false} isFetching={false}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Failed to load identity matches</p>
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

  const matches = data?.results ?? [];
  const isEmpty = !isLoading && matches.length === 0;

  const actionLink = (
    <Link to={routes.identity(workspaceId)} style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}>
      Resolve Identities
    </Link>
  );

  return (
    <WidgetCard
      title="Identity Resolution"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={isEmpty}
      emptyMessage="No pending matches to resolve."
      action={actionLink}
    >
      {matches.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {matches.map((match) => (
            <li key={match.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.5rem', background: 'var(--color-bg-subtle, #f3f4f6)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Pending Match</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)' }}>{new Date(match.created_at).toLocaleDateString()}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: match.confidence_score > 0.8 ? 'var(--color-success, #10b981)' : 'var(--color-warning, #f59e0b)' }}>
                  {(match.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </WidgetCard>
  );
};
