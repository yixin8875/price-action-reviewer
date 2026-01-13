import { useNavigate, useLocation } from 'react-router-dom';
import { BottomNavigation, BottomNavigationAction, Paper } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  ShowChart,
  CandlestickChart,
  Assignment,
} from '@mui/icons-material';

export default function MobileBottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  const getActiveTab = () => {
    if (location.pathname === '/') return 0;
    if (location.pathname.startsWith('/instruments')) return 1;
    if (location.pathname.startsWith('/charts')) return 2;
    if (location.pathname.startsWith('/reviews')) return 3;
    return 0;
  };

  const handleChange = (_: React.SyntheticEvent, newValue: number) => {
    const routes = ['/', '/instruments', '/charts', '/reviews'];
    navigate(routes[newValue]);
  };

  return (
    <Paper
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
      }}
      elevation={3}
    >
      <BottomNavigation value={getActiveTab()} onChange={handleChange}>
        <BottomNavigationAction label="首页" icon={<DashboardIcon />} />
        <BottomNavigationAction label="标的" icon={<ShowChart />} />
        <BottomNavigationAction label="图表" icon={<CandlestickChart />} />
        <BottomNavigationAction label="复盘" icon={<Assignment />} />
      </BottomNavigation>
    </Paper>
  );
}
