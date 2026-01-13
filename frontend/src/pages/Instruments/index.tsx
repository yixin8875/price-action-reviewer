import { useState } from 'react';
import {
  Typography,
  Button,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  CircularProgress,
  Snackbar,
  Alert,
} from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';
import { Add, Sync } from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';
import apiClient from '../../services/api';
import type { Instrument } from '../../types';

export default function Instruments() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [marketType, setMarketType] = useState('all');
  const [syncDays, setSyncDays] = useState(30);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [validationError, setValidationError] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  const { data: instruments = [], isLoading } = useQuery<Instrument[]>({
    queryKey: ['instruments'],
    queryFn: async () => {
      const response = await apiClient.get('/instruments/');
      return response.data;
    },
  });

  const syncMutation = useMutation({
    mutationFn: async (data: { instrument_ids?: number[]; market_type?: string; days: number }) => {
      return apiClient.post('/klines/batch-import/', data);
    },
    onSuccess: () => {
      setSnackbar({ open: true, message: '数据同步成功', severity: 'success' });
      setDialogOpen(false);
      setSelectedRows([]);
    },
    onError: () => {
      setSnackbar({ open: true, message: '数据同步失败', severity: 'error' });
    },
  });

  const handleBatchSync = () => {
    setValidationError('');

    if (syncDays < 1 || syncDays > 365) {
      setValidationError('同步天数必须在1到365之间');
      return;
    }

    if (selectedRows.length > 0) {
      syncMutation.mutate({
        instrument_ids: selectedRows,
        days: syncDays,
      });
    } else {
      syncMutation.mutate({
        market_type: marketType === 'all' ? undefined : marketType,
        days: syncDays,
      });
    }
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'symbol', headerName: '代码', width: 130 },
    { field: 'name', headerName: '名称', width: 200 },
    { field: 'exchange', headerName: '交易所', width: 130 },
    { field: 'instrument_type', headerName: '类型', width: 130 },
    {
      field: 'is_active',
      headerName: '状态',
      width: 100,
      valueGetter: (value) => (value ? '活跃' : '停用'),
    },
  ];

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">标的管理</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<Sync />}
            onClick={() => setDialogOpen(true)}
          >
            批量同步
          </Button>
          <Button variant="contained" startIcon={<Add />}>
            添加标的
          </Button>
        </Box>
      </Box>
      <Box sx={{ height: 600, width: '100%' }}>
        <DataGrid
          rows={instruments}
          columns={columns}
          loading={isLoading}
          checkboxSelection
          onRowSelectionModelChange={(newSelection) => {
            const ids = newSelection.type === 'include'
              ? Array.from(newSelection.ids) as number[]
              : [];
            setSelectedRows(ids);
          }}
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: { paginationModel: { pageSize: 10 } },
          }}
        />
      </Box>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>批量同步K线数据</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
            {validationError && (
              <Alert severity="error" onClose={() => setValidationError('')}>
                {validationError}
              </Alert>
            )}
            {selectedRows.length > 0 ? (
              <Alert severity="info">
                已选择 {selectedRows.length} 个标的进行同步
              </Alert>
            ) : (
              <TextField
                select
                label="市场类型"
                value={marketType}
                onChange={(e) => setMarketType(e.target.value)}
                fullWidth
              >
                <MenuItem value="all">全部</MenuItem>
                <MenuItem value="stock">股票</MenuItem>
                <MenuItem value="futures">期货</MenuItem>
                <MenuItem value="forex">外汇</MenuItem>
                <MenuItem value="crypto">加密货币</MenuItem>
              </TextField>
            )}
            <TextField
              type="number"
              label="同步天数"
              value={syncDays}
              onChange={(e) => setSyncDays(Number(e.target.value))}
              fullWidth
              inputProps={{ min: 1, max: 365 }}
              error={syncDays < 1 || syncDays > 365}
              helperText={
                syncDays < 1 || syncDays > 365
                  ? '同步天数必须在1到365之间'
                  : '请输入需要同步的天数'
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>取消</Button>
          <Button
            onClick={handleBatchSync}
            variant="contained"
            disabled={syncMutation.isPending}
          >
            {syncMutation.isPending ? <CircularProgress size={24} /> : '开始同步'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}
