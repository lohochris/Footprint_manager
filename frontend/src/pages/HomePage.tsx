import { Box, Card, CardContent, Chip, Grid, Typography } from '@mui/material';
import { motion } from 'framer-motion';

import { HealthStatus } from '@/components/HealthStatus';
import { APP_NAME, APP_VERSION } from '@/utils/constants';

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4 },
};

export function HomePage() {
  return (
    <Box>
      <motion.div {...fadeIn}>
        <Typography variant="h4" gutterBottom fontWeight={700}>
          Welcome to {APP_NAME}
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Enterprise Digital Footprint Intelligence Platform — Sprint 0 Infrastructure Bootstrap
        </Typography>
      </motion.div>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <motion.div {...fadeIn} transition={{ delay: 0.1 }}>
            <HealthStatus />
          </motion.div>
        </Grid>
        <Grid item xs={12} md={6}>
          <motion.div {...fadeIn} transition={{ delay: 0.2 }}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Platform Status
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                  <Chip label={`Version ${APP_VERSION}`} color="primary" size="small" />
                  <Chip label="Sprint 0" color="secondary" size="small" />
                  <Chip label="Infrastructure Ready" color="success" size="small" />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  Backend, frontend, and DevOps infrastructure are configured and ready for
                  Sprint 1 feature development.
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
}
