# Footprint Manager Frontend Architecture

This is the flagship Intelligence Dashboard for the Footprint Manager platform.

## Architecture Guidelines

1. **Framework**: React 18, Vite, TypeScript. No server-side rendering (SSR).
2. **State Management**:
   - **React Query** for Server State (fetching, caching, deduping).
   - **Zustand** for Client UI State (themes, layout).
3. **Design Tokens**: All styling is driven by CSS Variables defined in `src/styles/variables.css`. Do not hardcode hex colors or pixel spacings. Use CSS Modules.
4. **Shell Architecture**: All pages use the `Shell` layout with named regions (Header, Sidebar, Workspace, Inspector, Activity) to support a modular workspace.
5. **Route Guards**: Use modular wrapper components (`RequireAuth`, `RequirePermission`) to mirror the backend authorization model.
6. **Telemetry**: Utilize `TelemetryService` to publish observability events uniformly.

## Directory Structure
- `/src/api`: Typed Axios clients, modular interceptors (Auth, Error, Telemetry), and DTOs.
- `/src/components`: Atomic design components (`atoms`, `molecules`, `organisms`, `templates`, including Error Boundaries).
- `/src/features`: Business logic domains (Graph, Timeline, Investigations, AI Assistant).
- `/src/layouts`: Shell infrastructure.
- `/src/routes`: Route Guards and App Router.
- `/src/telemetry`: The centralized observability emission layer.

## Future Integration Points
- **Graph Intelligence**: Cytoscape instances render inside `GraphCanvas`.
- **Timeline Intelligence**: Vis Timeline instances render inside `TimelineViewport`.
- **AI Assistant**: Will be a persistent dockable panel residing in an isolated feature folder.
