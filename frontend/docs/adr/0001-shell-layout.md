# 0001: Shell Layout Architecture

## Status
Accepted

## Context
Footprint Manager is a highly interactive intelligence dashboard that requires multiple concurrent panels (e.g. workspace, graph, evidence inspector, timeline). We need a flexible layout system.

## Decision
We will use a Region-based Shell layout pattern rather than static layout files.
The `Shell` component will provide named slots (regions):
- Header
- Sidebar
- Workspace
- Inspector
- Activity

## Consequences
- **Positive:** Adding new dockable panels or dynamically resizing them is much easier because the Shell doesn't know about their contents.
- **Positive:** Consistent visual hierarchy.
- **Negative:** Slightly more verbose when wrapping routes, but outweighed by the maintainability benefits.
