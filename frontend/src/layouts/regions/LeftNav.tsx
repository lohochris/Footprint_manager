import React from 'react';
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { Dashboard, Assessment, Source, Person, Timeline, Settings } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';

export const LeftNav: React.FC = () => {
  const navigate = useNavigate();
  const { workspaceId } = useParams();
  const basePath = `/workspace/${workspaceId || 'default'}`;

  const navItems = [
    { label: 'Dashboard', icon: <Dashboard />, path: `${basePath}/dashboard` },
    { label: 'Investigations', icon: <Assessment />, path: `${basePath}/investigations` },
    { label: 'Evidence', icon: <Source />, path: `${basePath}/evidence` },
    { label: 'Identity', icon: <Person />, path: `${basePath}/identity` },
    { label: 'Timeline', icon: <Timeline />, path: `${basePath}/timeline` },
  ];

  return (
    <Box sx={{ 
      width: 240, 
      borderRight: '1px solid', 
      borderColor: 'divider',
      backgroundColor: 'background.paper',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <List sx={{ flexGrow: 1 }}>
        {navItems.map((item) => (
          <ListItem key={item.label} disablePadding>
            <ListItemButton onClick={() => navigate(item.path)}>
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
      <List>
        <ListItem disablePadding>
          <ListItemButton onClick={() => navigate('/admin/settings')}>
            <ListItemIcon><Settings /></ListItemIcon>
            <ListItemText primary="Admin Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );
};
