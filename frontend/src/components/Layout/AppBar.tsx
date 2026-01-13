import { AppBar as MuiAppBar, Toolbar, IconButton, Typography } from '@mui/material';
import { Menu as MenuIcon, Brightness4, Brightness7 } from '@mui/icons-material';
import { useAuthStore } from '../../stores/authStore';

interface AppBarProps {
  onMenuClick: () => void;
  darkMode: boolean;
  onThemeToggle: () => void;
}

export default function AppBar({ onMenuClick, darkMode, onThemeToggle }: AppBarProps) {
  const { user } = useAuthStore();

  return (
    <MuiAppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <IconButton color="inherit" edge="start" onClick={onMenuClick} sx={{ mr: 2 }}>
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          价格行为复盘系统
        </Typography>
        <IconButton color="inherit" onClick={onThemeToggle}>
          {darkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
        <Typography variant="body2" sx={{ ml: 2 }}>
          {user?.username}
        </Typography>
      </Toolbar>
    </MuiAppBar>
  );
}
