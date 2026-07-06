import React from 'react';
import { WidgetCard } from '../WidgetCard';
import { DashboardWidgetProps } from '../../types';
import { useGetCollaborationNotificationsQuery } from '../../api/dashboardApi';

export const NotificationsWidget: React.FC<DashboardWidgetProps> = ({ workspaceId }) => {
  const { data, isLoading, isFetching, error, refetch } = useGetCollaborationNotificationsQuery(
    { workspaceId },
    { pollingInterval: 15000 } // 15s polling for fast-changing data
  );

  if (error) {
    return (
      <WidgetCard title="Notifications" isLoading={false} isFetching={false}>
        <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--color-danger, #ef4444)' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontWeight: 500 }}>Failed to load notifications</p>
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

  const notifications = data?.results ?? [];
  const isEmpty = !isLoading && notifications.length === 0;

  return (
    <WidgetCard
      title="Notifications"
      isLoading={isLoading}
      isFetching={isFetching}
      isEmpty={isEmpty}
      emptyMessage="You have no new notifications."
    >
      {notifications.length > 0 && (
        <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {notifications.map((notification) => (
            <li
              key={notification.id}
              style={{
                padding: '0.75rem',
                background: notification.is_read ? 'transparent' : 'var(--color-primary-subtle, #eff6ff)',
                borderLeft: notification.is_read ? '2px solid transparent' : '2px solid var(--color-primary, #3b82f6)',
                borderRadius: '0 4px 4px 0',
                borderBottom: '1px solid var(--color-border-subtle, #f3f4f6)'
              }}
            >
              <h4 style={{ margin: '0 0 0.25rem 0', fontSize: '0.875rem', fontWeight: notification.is_read ? 500 : 600 }}>
                {notification.title}
              </h4>
              <p style={{ margin: '0 0 0.25rem 0', fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)' }}>
                {notification.message}
              </p>
              <span style={{ fontSize: '0.65rem', color: 'var(--color-text-light, #9ca3af)' }}>
                {new Date(notification.created_at).toLocaleString()}
              </span>
            </li>
          ))}
        </ul>
      )}
    </WidgetCard>
  );
};
