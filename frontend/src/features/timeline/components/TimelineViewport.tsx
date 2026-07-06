import React, { useRef, useEffect } from 'react';
import { Timeline, DataSet } from 'vis-timeline/standalone';
import 'vis-timeline/styles/vis-timeline-graph2d.min.css';

interface TimelineViewportProps {
  items: any[];
  groups?: any[];
  options?: any;
}

export const TimelineViewport: React.FC<TimelineViewportProps> = ({ items, groups, options }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const timelineRef = useRef<Timeline | null>(null);

  useEffect(() => {
    if (containerRef.current && !timelineRef.current) {
      const itemsDataset = new DataSet(items);
      
      const defaultOptions = {
        height: '100%',
        margin: { item: 10 },
      };

      if (groups) {
        const groupsDataset = new DataSet(groups);
        timelineRef.current = new Timeline(containerRef.current, itemsDataset, groupsDataset, { ...defaultOptions, ...options });
      } else {
        timelineRef.current = new Timeline(containerRef.current, itemsDataset, { ...defaultOptions, ...options });
      }
    }

    return () => {
      if (timelineRef.current) {
        timelineRef.current.destroy();
        timelineRef.current = null;
      }
    };
  }, [items, groups, options]);

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />;
};
