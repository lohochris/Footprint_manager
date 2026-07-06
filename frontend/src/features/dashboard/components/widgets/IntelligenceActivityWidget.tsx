import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetIntelligenceRecommendationsQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';
import { routes } from '@/router/routes';

export const IntelligenceActivityWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetIntelligenceRecommendationsQuery(
    { workspaceId },
    { pollingInterval: 60000 }
  );

  const actionLink = (
    <Link to={routes.intelligence(workspaceId)} style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}>
      View all
    </Link>
  );

  if (error) {
    return (
      <WidgetCard title="Intelligence Activity" isLoading={false} isFetching={false} action={actionLink}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Unable to load intelligence recommendations</p>
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

  const recommendations = data?.results ?? [];
  const isEmpty = !isLoading && recommendations.length === 0;

  return (
    <WidgetCard
      title="Intelligence Activity"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={isEmpty}
      emptyMessage="No new intelligence recommendations."
      action={actionLink}
    >
      {recommendations.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {recommendations.map((rec) => (
            <li key={rec.id} style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', padding: '0.75rem', background: 'var(--color-bg-subtle, #f3f4f6)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 500, lineHeight: 1.4 }}>{rec.description}</span>
                <span style={{ fontSize: '0.65rem', padding: '0.125rem 0.375rem', background: 'var(--color-warning-subtle, #fef3c7)', color: 'var(--color-warning-dark, #b45309)', borderRadius: '4px', whiteSpace: 'nowrap', marginLeft: '0.5rem' }}>
                  {rec.priority}
                </span>
              </div>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)' }}>{new Date(rec.created_at).toLocaleDateString()}</span>
            </li>
          ))}
        </ul>
      )}
    </WidgetCard>
  );
};
