import React, { ReactNode } from 'react';
import { WidgetErrorBoundary } from './WidgetErrorBoundary';

interface WidgetCardProps {
  title: string;
  children: ReactNode;
  isLoading?: boolean;
  isFetching?: boolean;
  isEmpty?: boolean;
  emptyMessage?: string;
  action?: ReactNode; // e.g. a link to the full feature page
}

export const WidgetCard: React.FC<WidgetCardProps> = ({
  title,
  children,
  isLoading,
  isFetching,
  isEmpty,
  emptyMessage = 'No data available',
  action
}) => {
  return (
    <WidgetErrorBoundary widgetName={title}>
      <section 
        className="widget-card" 
        style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          background: 'var(--color-bg-surface, #ffffff)', 
          borderRadius: '8px', 
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
          height: '100%',
          overflow: 'hidden'
        }}
        aria-label={title}
      >
        <header style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          padding: '1rem', 
          borderBottom: '1px solid var(--color-border, #e5e7eb)' 
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <h2 style={{ margin: 0, fontSize: '1.125rem', fontWeight: 600 }}>{title}</h2>
            {isFetching && !isLoading && (
              <span aria-live="polite" aria-label={`Refreshing ${title} data`} style={{ fontSize: '0.75rem', color: 'var(--color-text-muted, #6b7280)' }}>
                (Refreshing...)
              </span>
            )}
          </div>
          {action && <div>{action}</div>}
        </header>
        
        <div className="widget-content" style={{ padding: '1rem', flex: 1, overflowY: 'auto' }}>
          {isLoading ? (
            <div className="widget-skeleton" aria-live="polite" aria-busy="true">
              {/* Basic skeleton loader */}
              <div style={{ height: '2rem', background: 'var(--color-border, #e5e7eb)', borderRadius: '4px', marginBottom: '0.5rem', animation: 'pulse 1.5s infinite' }} />
              <div style={{ height: '2rem', background: 'var(--color-border, #e5e7eb)', borderRadius: '4px', marginBottom: '0.5rem', animation: 'pulse 1.5s infinite' }} />
              <div style={{ height: '2rem', background: 'var(--color-border, #e5e7eb)', borderRadius: '4px', animation: 'pulse 1.5s infinite' }} />
            </div>
          ) : isEmpty ? (
            <div className="widget-empty" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'var(--color-text-muted, #6b7280)' }}>
              <p>{emptyMessage}</p>
            </div>
          ) : (
            children
          )}
        </div>
      </section>
    </WidgetErrorBoundary>
  );
};
