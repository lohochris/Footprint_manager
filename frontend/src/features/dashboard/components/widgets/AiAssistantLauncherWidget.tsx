import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetAiSessionsQuery } from '../../api/dashboardApi';
import { Link } from 'react-router-dom';
import { routes } from '@/router/routes';

export const AiAssistantLauncherWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetAiSessionsQuery(
    { workspaceId },
    { pollingInterval: 60000 }
  );

  if (error) {
    return (
      <WidgetCard title="AI Assistant" isLoading={false} isFetching={false}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Failed to load AI sessions</p>
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

  const actionLink = (
    <Link
      to={routes.ai(workspaceId)}
      style={{ fontSize: '0.875rem', color: 'var(--color-primary, #3b82f6)', textDecoration: 'none', fontWeight: 500 }}
    >
      Open Assistant
    </Link>
  );

  const recentSessions = data?.results ?? [];

  return (
    <WidgetCard
      title="AI Assistant"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={false} // Launcher is always available
      action={actionLink}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
        <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--color-text, #111827)' }}>
          How can I assist with your investigation today?
        </p>

        <Link
          to={routes.aiNewSession(workspaceId)}
          style={{
            display: 'block',
            padding: '0.75rem',
            textAlign: 'center',
            background: 'var(--color-primary, #3b82f6)',
            color: 'white',
            borderRadius: '6px',
            textDecoration: 'none',
            fontWeight: 500,
            fontSize: '0.875rem'
          }}
        >
          Start New Session
        </Link>

        {recentSessions.length > 0 && (
          <div style={{ marginTop: 'auto' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.75rem', textTransform: 'uppercase', color: 'var(--color-text-muted, #6b7280)' }}>Recent Sessions</h4>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {recentSessions.map((session) => (
                <li key={session.id}>
                  <Link
                    to={routes.aiSession(workspaceId, session.id)}
                    style={{ fontSize: '0.875rem', color: 'var(--color-text, #111827)', textDecoration: 'none', display: 'flex', justifyContent: 'space-between' }}
                  >
                    <span style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap', maxWidth: '70%' }}>{session.title}</span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--color-text-light, #9ca3af)' }}>{new Date(session.updated_at).toLocaleDateString()}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </WidgetCard>
  );
};
