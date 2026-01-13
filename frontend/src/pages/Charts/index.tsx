import { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  List,
  ListItemButton,
  ListItemText,
  Typography,
  Stack,
  Button,
  Popover,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Skeleton,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import { ShowChart } from '@mui/icons-material';
import apiClient from '../../services/api';
import type { Instrument, KLine } from '../../types';
import KLineChart from '../../components/Charts/KLineChart';

export default function Charts() {
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [selectedInstrument, setSelectedInstrument] = useState<number | null>(null);
  const [klines, setKlines] = useState<KLine[]>([]);
  const [loading, setLoading] = useState(false);
  const [instrumentsLoading, setInstrumentsLoading] = useState(true);
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([]);
  const [indicatorData, setIndicatorData] = useState<Record<string, any>>({});
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  useEffect(() => {
    fetchInstruments();
  }, []);

  const fetchInstruments = async () => {
    try {
      const response = await apiClient.get('/instruments/');
      const data = response.data.results || response.data;
      setInstruments(data);
      if (data.length > 0) {
        setSelectedInstrument(data[0].id);
      }
    } catch (error) {
      console.error('Failed to fetch instruments:', error);
    } finally {
      setInstrumentsLoading(false);
    }
  };

  useEffect(() => {
    if (selectedInstrument) {
      fetchKlines(selectedInstrument);
    }
  }, [selectedInstrument]);

  useEffect(() => {
    if (selectedInstrument && selectedIndicators.length > 0) {
      fetchIndicators(selectedInstrument, selectedIndicators);
    }
  }, [selectedInstrument, selectedIndicators]);

  const fetchKlines = async (instrumentId: number) => {
    setLoading(true);
    try {
      const response = await apiClient.get(`/klines/?instrument=${instrumentId}&page_size=100`);
      setKlines(response.data.results || response.data);
    } catch (error) {
      console.error('Failed to fetch klines:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIndicators = async (instrumentId: number, indicators: string[]) => {
    try {
      const data: Record<string, any> = {};
      for (const indicator of indicators) {
        const response = await apiClient.get(
          `/indicators/?instrument=${instrumentId}&indicator_type=${indicator}`
        );
        data[indicator] = response.data;
      }
      setIndicatorData(data);
    } catch (error) {
      console.error('Failed to fetch indicators:', error);
    }
  };

  const handleIndicatorToggle = (indicator: string) => {
    setSelectedIndicators((prev) =>
      prev.includes(indicator) ? prev.filter((i) => i !== indicator) : [...prev, indicator]
    );
  };

  const AVAILABLE_INDICATORS = [
    { value: 'MA5', label: 'MA5' },
    { value: 'MA10', label: 'MA10' },
    { value: 'MA20', label: 'MA20' },
    { value: 'MACD', label: 'MACD' },
    { value: 'RSI', label: 'RSI' },
    { value: 'KDJ', label: 'KDJ' },
    { value: 'BOLL', label: 'BOLL' },
  ];

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">K线图表</Typography>
        <Button
          variant="outlined"
          startIcon={<ShowChart />}
          onClick={(e) => setAnchorEl(e.currentTarget)}
        >
          指标
        </Button>
      </Box>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={2}>
        {!isMobile && (
          <Paper sx={{ width: 300, height: 600, overflow: 'auto' }}>
            {instrumentsLoading ? (
              <List>
                {[1, 2, 3, 4, 5].map((i) => (
                  <ListItemButton key={i}>
                    <ListItemText
                      primary={<Skeleton width="60%" />}
                      secondary={<Skeleton width="40%" />}
                    />
                  </ListItemButton>
                ))}
              </List>
            ) : (
              <List>
                {instruments.map((instrument) => (
                  <ListItemButton
                    key={instrument.id}
                    selected={selectedInstrument === instrument.id}
                    onClick={() => setSelectedInstrument(instrument.id)}
                  >
                    <ListItemText primary={instrument.name} secondary={instrument.symbol} />
                  </ListItemButton>
                ))}
              </List>
            )}
          </Paper>
        )}
        <Paper sx={{ flex: 1, p: 2 }}>
          {loading ? (
            <Box sx={{ height: 600 }}>
              <Skeleton variant="rectangular" height="100%" />
            </Box>
          ) : klines.length > 0 ? (
            <KLineChart data={klines} indicators={indicatorData} />
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 600 }}>
              <Typography>暂无数据</Typography>
            </Box>
          )}
        </Paper>
      </Stack>

      <Popover
        open={Boolean(anchorEl)}
        anchorEl={anchorEl}
        onClose={() => setAnchorEl(null)}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ p: 2, minWidth: 200 }}>
          <Typography variant="subtitle2" gutterBottom>
            选择技术指标
          </Typography>
          <FormGroup>
            {AVAILABLE_INDICATORS.map((indicator) => (
              <FormControlLabel
                key={indicator.value}
                control={
                  <Checkbox
                    checked={selectedIndicators.includes(indicator.value)}
                    onChange={() => handleIndicatorToggle(indicator.value)}
                  />
                }
                label={indicator.label}
              />
            ))}
          </FormGroup>
        </Box>
      </Popover>
    </>
  );
}
