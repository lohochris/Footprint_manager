import React from 'react';
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText } from '@mui/material';
import { Dashboard, Assessment, Source, Person, Timeline, Settings, SmartToy } from '@mui/icons-material';
import { useNavigate, useParams } from 'react-router-dom';
import { routes } from '@/router/routes';

export const LeftNav: React.FC = () => {
  const navigate = useNavigate();
  const { workspaceId } = useParams();
  const wid = workspaceId ?? 'default';

  const navItems = [
    { label: 'Dashboard',       icon: <Dashboard />,  path: routes.dashboard(wid) },
    { label: 'Investigations',  icon: <Assessment />, path: routes.investigations(wid) },
    { label: 'Evidence',        icon: <Source />,     path: routes.evidence(wid) },
    { label: 'Identity',        icon: <Person />,     path: routes.identity(wid) },
    { label: 'Timeline',        icon: <Timeline />,   path: routes.timeline(wid) },
    { label: 'AI Assistant',    icon: <SmartToy />,   path: routes.ai(wid) },
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
          <ListItemButton onClick={() => navigate(routes.adminSettings())}>
            <ListItemIcon><Settings /></ListItemIcon>
            <ListItemText primary="Admin Settings" />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  );
};
