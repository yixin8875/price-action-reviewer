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
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [marketType, setMarketType] = useState('all');
  const [syncDays, setSyncDays] = useState(30);
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const [validationError, setValidationError] = useState('');
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  // 新标的表单数据
  const [newInstrument, setNewInstrument] = useState({
    symbol: '',
    name: '',
    market_type: 'STOCK',
    exchange: 'SSE',
  });

  // 编辑标的表单数据
  const [editInstrument, setEditInstrument] = useState<Instrument | null>(null);

  const { data: instruments = [], isLoading, refetch } = useQuery<Instrument[]>({
    queryKey: ['instruments'],
    queryFn: async () => {
      const response = await apiClient.get('/instruments/');
      return response.data.results || response.data;
    },
  });

  const addMutation = useMutation({
    mutationFn: async (data: typeof newInstrument) => {
      return apiClient.post('/instruments/', data);
    },
    onSuccess: () => {
      setSnackbar({ open: true, message: '标的添加成功', severity: 'success' });
      setAddDialogOpen(false);
      setNewInstrument({ symbol: '', name: '', market_type: 'STOCK', exchange: 'SSE' });
      refetch();
    },
    onError: () => {
      setSnackbar({ open: true, message: '标的添加失败', severity: 'error' });
    },
  });

  const editMutation = useMutation({
    mutationFn: async (data: Instrument) => {
      return apiClient.put(`/instruments/${data.id}/`, data);
    },
    onSuccess: () => {
      setSnackbar({ open: true, message: '标的更新成功', severity: 'success' });
      setEditDialogOpen(false);
      setEditInstrument(null);
      refetch();
    },
    onError: () => {
      setSnackbar({ open: true, message: '标的更新失败', severity: 'error' });
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

  const handleAddInstrument = () => {
    setValidationError('');

    if (!newInstrument.symbol || !newInstrument.name) {
      setValidationError('代码和名称不能为空');
      return;
    }

    addMutation.mutate(newInstrument);
  };

  const handleEditInstrument = () => {
    setValidationError('');

    if (!editInstrument || !editInstrument.symbol || !editInstrument.name) {
      setValidationError('代码和名称不能为空');
      return;
    }

    editMutation.mutate(editInstrument);
  };

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'symbol', headerName: '代码', width: 130 },
    { field: 'name', headerName: '名称', width: 200 },
    { field: 'exchange', headerName: '交易所', width: 130 },
    { field: 'market_type', headerName: '类型', width: 130 },
    {
      field: 'is_active',
      headerName: '状态',
      width: 100,
      valueGetter: (value) => (value ? '活跃' : '停用'),
    },
    {
      field: 'actions',
      headerName: '操作',
      width: 100,
      renderCell: (params) => (
        <Button
          size="small"
          onClick={() => {
            setEditInstrument(params.row);
            setEditDialogOpen(true);
          }}
        >
          编辑
        </Button>
      ),
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
          <Button variant="contained" startIcon={<Add />} onClick={() => setAddDialogOpen(true)}>
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

      <Dialog open={addDialogOpen} onClose={() => setAddDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>添加标的</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
            {validationError && (
              <Alert severity="error" onClose={() => setValidationError('')}>
                {validationError}
              </Alert>
            )}
            <TextField
              label="代码"
              value={newInstrument.symbol}
              onChange={(e) => setNewInstrument({ ...newInstrument, symbol: e.target.value })}
              fullWidth
              required
              placeholder="例如: 000001"
            />
            <TextField
              label="名称"
              value={newInstrument.name}
              onChange={(e) => setNewInstrument({ ...newInstrument, name: e.target.value })}
              fullWidth
              required
              placeholder="例如: 平安银行"
            />
            <TextField
              select
              label="市场类型"
              value={newInstrument.market_type}
              onChange={(e) => setNewInstrument({ ...newInstrument, market_type: e.target.value })}
              fullWidth
            >
              <MenuItem value="STOCK">股票</MenuItem>
              <MenuItem value="FUTURES">期货</MenuItem>
            </TextField>
            <TextField
              select
              label="交易所"
              value={newInstrument.exchange}
              onChange={(e) => setNewInstrument({ ...newInstrument, exchange: e.target.value })}
              fullWidth
            >
              <MenuItem value="SSE">上海证券交易所</MenuItem>
              <MenuItem value="SZSE">深圳证券交易所</MenuItem>
              <MenuItem value="CFFEX">中国金融期货交易所</MenuItem>
              <MenuItem value="SHFE">上海期货交易所</MenuItem>
              <MenuItem value="DCE">大连商品交易所</MenuItem>
              <MenuItem value="CZCE">郑州商品交易所</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialogOpen(false)}>取消</Button>
          <Button
            onClick={handleAddInstrument}
            variant="contained"
            disabled={addMutation.isPending}
          >
            {addMutation.isPending ? <CircularProgress size={24} /> : '添加'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>编辑标的</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 2 }}>
            {validationError && (
              <Alert severity="error" onClose={() => setValidationError('')}>
                {validationError}
              </Alert>
            )}
            <TextField
              label="代码"
              value={editInstrument?.symbol || ''}
              onChange={(e) => setEditInstrument(editInstrument ? { ...editInstrument, symbol: e.target.value } : null)}
              fullWidth
              required
            />
            <TextField
              label="名称"
              value={editInstrument?.name || ''}
              onChange={(e) => setEditInstrument(editInstrument ? { ...editInstrument, name: e.target.value } : null)}
              fullWidth
              required
            />
            <TextField
              select
              label="市场类型"
              value={editInstrument?.market_type || 'STOCK'}
              onChange={(e) => setEditInstrument(editInstrument ? { ...editInstrument, market_type: e.target.value } : null)}
              fullWidth
            >
              <MenuItem value="STOCK">股票</MenuItem>
              <MenuItem value="FUTURES">期货</MenuItem>
            </TextField>
            <TextField
              select
              label="交易所"
              value={editInstrument?.exchange || 'SSE'}
              onChange={(e) => setEditInstrument(editInstrument ? { ...editInstrument, exchange: e.target.value } : null)}
              fullWidth
            >
              <MenuItem value="SSE">上海证券交易所</MenuItem>
              <MenuItem value="SZSE">深圳证券交易所</MenuItem>
              <MenuItem value="CFFEX">中国金融期货交易所</MenuItem>
              <MenuItem value="SHFE">上海期货交易所</MenuItem>
              <MenuItem value="DCE">大连商品交易所</MenuItem>
              <MenuItem value="CZCE">郑州商品交易所</MenuItem>
            </TextField>
            <TextField
              select
              label="状态"
              value={editInstrument?.is_active ? 'true' : 'false'}
              onChange={(e) => setEditInstrument(editInstrument ? { ...editInstrument, is_active: e.target.value === 'true' } : null)}
              fullWidth
            >
              <MenuItem value="true">活跃</MenuItem>
              <MenuItem value="false">停用</MenuItem>
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>取消</Button>
          <Button
            onClick={handleEditInstrument}
            variant="contained"
            disabled={editMutation.isPending}
          >
            {editMutation.isPending ? <CircularProgress size={24} /> : '保存'}
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
