import { useState } from 'react';
import { Box, Toolbar, useMediaQuery, useTheme } from '@mui/material';
import AppBar from './AppBar';
import Sidebar from './Sidebar';
import MobileBottomNav from './MobileBottomNav';

interface MainLayoutProps {
  children: React.ReactNode;
  darkMode: boolean;
  onThemeToggle: () => void;
}

export default function MainLayout({ children, darkMode, onThemeToggle }: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        onMenuClick={() => setSidebarOpen(true)}
        darkMode={darkMode}
        onThemeToggle={onThemeToggle}
      />
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, sm: 3 },
          pb: isMobile ? 10 : 3,
        }}
      >
        <Toolbar />
        {children}
      </Box>
      {isMobile && <MobileBottomNav />}
    </Box>
  );
}
