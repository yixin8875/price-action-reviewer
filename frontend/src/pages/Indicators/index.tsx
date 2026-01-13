import { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Stack,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';
import { Calculate } from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../services/api';
import type { Instrument } from '../../types';

interface IndicatorRecord {
  id: number;
  instrument: number;
  instrument_name?: string;
  indicator_type: string;
  trade_date: string;
  calculated_at: string;
}

const INDICATOR_TYPES = [
  { value: 'MA', label: '移动平均线' },
  { value: 'MACD', label: 'MACD' },
  { value: 'RSI', label: 'RSI' },
  { value: 'KDJ', label: 'KDJ' },
  { value: 'BOLL', label: '布林带' },
];

const TIMEFRAMES = [
  { value: '1d', label: '日线' },
  { value: '1w', label: '周线' },
  { value: '1M', label: '月线' },
];

export default function Indicators() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedInstruments, setSelectedInstruments] = useState<number[]>([]);
  const [selectedIndicators, setSelectedIndicators] = useState<string[]>([]);
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [timeframe, setTimeframe] = useState('1d');
  const [validationError, setValidationError] = useState('');
  const queryClient = useQueryClient();

  const { data: indicators = [], isLoading } = useQuery<IndicatorRecord[]>({
    queryKey: ['indicators'],
    queryFn: async () => {
      const response = await apiClient.get('/indicators/');
      return response.data;
    },
  });

  const { data: instruments = [] } = useQuery<Instrument[]>({
    queryKey: ['instruments'],
    queryFn: async () => {
      const response = await apiClient.get('/instruments/');
      return response.data;
    },
  });

  const calculateMutation = useMutation({
    mutationFn: async (data: {
      instrument_ids: number[];
      indicator_types: string[];
      start_date: string;
      end_date: string;
      timeframe: string;
    }) => {
      return apiClient.post('/indicators/batch-calculate/', data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['indicators'] });
      setDialogOpen(false);
      setSelectedInstruments([]);
      setSelectedIndicators([]);
      setStartDate(null);
      setEndDate(null);
    },
  });

  const handleCalculate = () => {
    setValidationError('');

    if (selectedInstruments.length === 0) {
      setValidationError('请至少选择一个标的');
      return;
    }
    if (selectedIndicators.length === 0) {
      setValidationError('请至少选择一个指标');
      return;
    }
    if (!startDate) {
      setValidationError('请选择开始日期');
      return;
    }
    if (!endDate) {
      setValidationError('请选择结束日期');
      return;
    }
    if (startDate > endDate) {
      setValidationError('开始日期不能晚于结束日期');
      return;
    }

    calculateMutation.mutate({
      instrument_ids: selectedInstruments,
      indicator_types: selectedIndicators,
      start_date: startDate.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      timeframe,
    });
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    {
      field: 'instrument_name',
      headerName: '标的',
      width: 150,
      valueGetter: (value, row) =>
        value || instruments.find((i) => i.id === row.instrument)?.name || `#${row.instrument}`,
    },
    { field: 'indicator_type', headerName: '指标类型', width: 130 },
    { field: 'trade_date', headerName: '交易日期', width: 130 },
    {
      field: 'calculated_at',
      headerName: '计算时间',
      width: 180,
      valueGetter: (value) => new Date(value).toLocaleString(),
    },
  ];

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4">技术指标</Typography>
          <Button
            variant="contained"
            startIcon={<Calculate />}
            onClick={() => setDialogOpen(true)}
          >
            批量计算
          </Button>
        </Box>

        <Box sx={{ height: 600, width: '100%' }}>
          <DataGrid
            rows={indicators}
            columns={columns}
            loading={isLoading}
            pageSizeOptions={[10, 25, 50]}
            initialState={{
              pagination: { paginationModel: { pageSize: 10 } },
            }}
          />
        </Box>

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>批量计算技术指标</DialogTitle>
          <DialogContent>
            <Stack spacing={3} sx={{ mt: 2 }}>
              {validationError && (
                <Alert severity="error" onClose={() => setValidationError('')}>
                  {validationError}
                </Alert>
              )}

              <TextField
                select
                label="选择标的"
                SelectProps={{ multiple: true }}
                value={selectedInstruments}
                onChange={(e) => setSelectedInstruments(e.target.value as unknown as number[])}
                fullWidth
                error={selectedInstruments.length === 0 && validationError !== ''}
                helperText={selectedInstruments.length === 0 ? '请至少选择一个标的' : ''}
              >
                {instruments.map((inst) => (
                  <MenuItem key={inst.id} value={inst.id}>
                    {inst.name} ({inst.symbol})
                  </MenuItem>
                ))}
              </TextField>

              <TextField
                select
                label="选择指标"
                SelectProps={{ multiple: true }}
                value={selectedIndicators}
                onChange={(e) => setSelectedIndicators(e.target.value as unknown as string[])}
                fullWidth
                error={selectedIndicators.length === 0 && validationError !== ''}
                helperText={selectedIndicators.length === 0 ? '请至少选择一个指标' : ''}
              >
                {INDICATOR_TYPES.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </TextField>

              <DatePicker
                label="开始日期"
                value={startDate}
                onChange={setStartDate}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    error: !startDate && validationError !== '',
                    helperText: !startDate ? '请选择开始日期' : '',
                  },
                }}
              />

              <DatePicker
                label="结束日期"
                value={endDate}
                onChange={setEndDate}
                slotProps={{
                  textField: {
                    fullWidth: true,
                    error: !endDate && validationError !== '',
                    helperText: !endDate ? '请选择结束日期' : '',
                  },
                }}
              />

              <TextField
                select
                label="周期"
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                fullWidth
              >
                {TIMEFRAMES.map((tf) => (
                  <MenuItem key={tf.value} value={tf.value}>
                    {tf.label}
                  </MenuItem>
                ))}
              </TextField>

              {selectedInstruments.length > 0 && (
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    已选择 {selectedInstruments.length} 个标的
                  </Typography>
                </Box>
              )}

              {selectedIndicators.length > 0 && (
                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                  {selectedIndicators.map((ind) => (
                    <Chip
                      key={ind}
                      label={INDICATOR_TYPES.find((t) => t.value === ind)?.label}
                      size="small"
                    />
                  ))}
                </Box>
              )}
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>取消</Button>
            <Button
              onClick={handleCalculate}
              variant="contained"
              disabled={calculateMutation.isPending}
            >
              {calculateMutation.isPending ? <CircularProgress size={24} /> : '开始计算'}
            </Button>
          </DialogActions>
        </Dialog>
      </>
    </LocalizationProvider>
  );
}
