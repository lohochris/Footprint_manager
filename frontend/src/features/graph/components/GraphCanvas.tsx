import React, { useRef, useEffect } from 'react';
import cytoscape from 'cytoscape';

interface GraphCanvasProps {
  elements: cytoscape.ElementDefinition[];
  onNodeClick?: (node: cytoscape.NodeSingular) => void;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ elements, onNodeClick }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);

  useEffect(() => {
    if (containerRef.current) {
      cyRef.current = cytoscape({
        container: containerRef.current,
        elements,
        style: [
          {
            selector: 'node',
            style: {
              'background-color': '#2563eb',
              'label': 'data(id)',
              'color': '#fff',
              'text-outline-color': '#2563eb',
              'text-outline-width': 2,
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 2,
              'line-color': '#94a3b8',
              'target-arrow-color': '#94a3b8',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier'
            }
          }
        ],
        layout: { name: 'cose' }
      });

      if (onNodeClick) {
        cyRef.current.on('tap', 'node', (evt) => {
          onNodeClick(evt.target);
        });
      }
    }

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [elements, onNodeClick]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};
