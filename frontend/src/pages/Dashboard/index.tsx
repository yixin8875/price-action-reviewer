import { useEffect, useState } from 'react';
import { Box, Typography, Stack, Card, CardContent, Skeleton } from '@mui/material';
import { TrendingUp, Assessment, ShowChart } from '@mui/icons-material';
import StatCard from '../../components/Common/StatCard';
import apiClient from '../../services/api';
import type { DashboardStats } from '../../types';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats>({
    total_instruments: 0,
    total_reviews: 0,
    total_trades: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [instruments, reviews, trades] = await Promise.all([
          apiClient.get('/instruments/'),
          apiClient.get('/reviews/'),
          apiClient.get('/trades/'),
        ]);
        setStats({
          total_instruments: (instruments.data.results || instruments.data).length,
          total_reviews: (reviews.data.results || reviews.data).length,
          total_trades: (trades.data.results || trades.data).length,
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <>
      <Typography variant="h4" gutterBottom>
        仪表盘
      </Typography>
      {isLoading ? (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3}>
          {[1, 2, 3].map((i) => (
            <Box key={i} sx={{ flex: 1 }}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" width="60%" height={24} />
                  <Skeleton variant="rectangular" height={48} sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Box>
          ))}
        </Stack>
      ) : (
        <Stack direction={{ xs: 'column', sm: 'row' }} spacing={3}>
          <Box sx={{ flex: 1 }}>
            <StatCard title="标的总数" value={stats.total_instruments} icon={<TrendingUp />} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <StatCard title="复盘记录" value={stats.total_reviews} icon={<Assessment />} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <StatCard title="交易日志" value={stats.total_trades} icon={<ShowChart />} />
          </Box>
        </Stack>
      )}
    </>
  );
}
