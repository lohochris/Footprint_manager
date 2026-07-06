import React from 'react';
import { useParams } from 'react-router-dom';
import { WorkspaceOverviewWidget } from '../components/widgets/WorkspaceOverviewWidget';
import { ActiveInvestigationsWidget } from '../components/widgets/ActiveInvestigationsWidget';
import { SystemHealthWidget } from '../components/widgets/SystemHealthWidget';
import { NotificationsWidget } from '../components/widgets/NotificationsWidget';
import { EvidenceSummaryWidget } from '../components/widgets/EvidenceSummaryWidget';
import { IdentityResolutionWidget } from '../components/widgets/IdentityResolutionWidget';
import { IntelligenceActivityWidget } from '../components/widgets/IntelligenceActivityWidget';
import { GraphActivityWidget } from '../components/widgets/GraphActivityWidget';
import { RecentAlertsWidget } from '../components/widgets/RecentAlertsWidget';
import { AiAssistantLauncherWidget } from '../components/widgets/AiAssistantLauncherWidget';

export const DashboardView: React.FC = () => {
  const { workspaceId } = useParams<{ workspaceId: string }>();

  if (!workspaceId) {
    return <div>Error: No workspace selected</div>;
  }

  return (
    <div className="dashboard-container" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', padding: '1.5rem', height: '100%', overflowY: 'auto', background: 'var(--color-bg-canvas, #f9fafb)' }}>
      <header>
        <h1 style={{ fontSize: '1.5rem', margin: '0 0 1rem 0', fontWeight: 600 }}>Intelligence Dashboard</h1>
      </header>

      <div 
        className="dashboard-grid"
        style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(12, 1fr)', 
          gap: '1.5rem',
          gridAutoRows: 'minmax(300px, auto)'
        }}
      >
        {/* Top Row: High-level Summaries */}
        <div style={{ gridColumn: 'span 4' }}>
          <WorkspaceOverviewWidget workspaceId={workspaceId} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <ActiveInvestigationsWidget workspaceId={workspaceId} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <SystemHealthWidget workspaceId={workspaceId} />
        </div>

        {/* Middle Row: Operational Entities */}
        <div style={{ gridColumn: 'span 4' }}>
          <EvidenceSummaryWidget workspaceId={workspaceId} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <IdentityResolutionWidget workspaceId={workspaceId} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <IntelligenceActivityWidget workspaceId={workspaceId} />
        </div>

        {/* Bottom Row: Analytics & Tools */}
        <div style={{ gridColumn: 'span 6' }}>
          <GraphActivityWidget workspaceId={workspaceId} />
        </div>
        <div style={{ gridColumn: 'span 6' }}>
          <RecentAlertsWidget workspaceId={workspaceId} />
        </div>

        {/* Right Sidebar replacement/addition for Ai Assistant */}
        {/* We can place AiAssistant in the grid wherever makes sense, e.g. spanning 4 cols at the bottom or top.
            Since Notifications is in the first row spanning 4, let's put AI Assistant under Notifications or in the bottom row.
            Actually, the original plan had Top Row (4+4+4), Middle (4+4+4), Bottom (6+6), and Sidebar? 
            Let's keep the layout simple: Top (Overview, Investigations, Health), Middle (Evidence, Identity, Intelligence), Bottom (Graph, Alerts, AiAssistant) - wait, that's 9 widgets.
            Let's arrange them gracefully. 
        */}
        <div style={{ gridColumn: 'span 4' }}>
          <AiAssistantLauncherWidget workspaceId={workspaceId} />
        </div>
        <div style={{ gridColumn: 'span 4' }}>
          <NotificationsWidget workspaceId={workspaceId} />
        </div>
      </div>
    </div>
  );
};
