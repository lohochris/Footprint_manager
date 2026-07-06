import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  widgetName: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class WidgetErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`Error in widget ${this.props.widgetName}:`, error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div 
          className="widget-error" 
          role="alert"
          style={{ 
            padding: '1rem', 
            border: '1px solid var(--color-danger, #ef4444)', 
            borderRadius: '8px', 
            background: 'var(--color-bg-danger-subtle, #fee2e2)', 
            color: 'var(--color-danger, #dc2626)',
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
          }}
        >
          <h3 style={{ fontSize: '1rem', margin: '0 0 0.5rem 0' }}>{this.props.widgetName} failed to load</h3>
          <p style={{ margin: 0, fontSize: '0.875rem' }}>{this.state.error?.message || 'An unexpected error occurred.'}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
