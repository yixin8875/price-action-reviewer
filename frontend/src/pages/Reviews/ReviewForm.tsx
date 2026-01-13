import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Typography,
  Paper,
  Rating,
  Stack,
  CircularProgress,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '../../services/api';
import type { Instrument } from '../../types';

const reviewSchema = z.object({
  instrument: z.number().min(1, '请选择标的'),
  review_date: z.date(),
  review_type: z.enum(['daily', 'weekly', 'monthly']),
  market_stage: z.enum(['uptrend', 'downtrend', 'consolidation', 'reversal']),
  support_levels: z.string().optional(),
  resistance_levels: z.string().optional(),
  analysis_notes: z.string().min(10, '分析笔记至少需要10个字符').max(5000, '分析笔记不能超过5000个字符'),
  rating: z.number().min(1, '评分至少为1星').max(5, '评分最多为5星').optional(),
  tags: z.string().optional(),
});

type ReviewFormData = z.infer<typeof reviewSchema>;

export default function ReviewForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = Boolean(id);

  const { data: instruments = [] } = useQuery<Instrument[]>({
    queryKey: ['instruments'],
    queryFn: async () => {
      const response = await apiClient.get('/instruments/');
      return response.data;
    },
  });

  const { data: review, isLoading: reviewLoading } = useQuery({
    queryKey: ['review', id],
    queryFn: async () => {
      const response = await apiClient.get(`/reviews/${id}/`);
      return response.data;
    },
    enabled: isEdit,
  });

  const {
    control,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ReviewFormData>({
    resolver: zodResolver(reviewSchema),
    mode: 'onChange',
    defaultValues: {
      review_type: 'daily',
      market_stage: 'consolidation',
      rating: 3,
    },
  });

  useEffect(() => {
    if (review) {
      reset({
        instrument: review.instrument,
        review_date: new Date(review.review_date),
        review_type: review.review_type || 'daily',
        market_stage: review.market_stage || 'consolidation',
        support_levels: review.support_levels || '',
        resistance_levels: review.resistance_levels || '',
        analysis_notes: review.analysis_notes || '',
        rating: review.rating || 3,
        tags: review.tags?.join(', ') || '',
      });
    }
  }, [review, reset]);

  const mutation = useMutation({
    mutationFn: async (data: ReviewFormData) => {
      const payload = {
        ...data,
        review_date: data.review_date.toISOString().split('T')[0],
        tags: data.tags?.split(',').map((t) => t.trim()).filter(Boolean) || [],
      };
      if (isEdit) {
        return apiClient.put(`/reviews/${id}/`, payload);
      }
      return apiClient.post('/reviews/', payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      navigate('/reviews');
    },
  });

  const onSubmit = (data: ReviewFormData) => {
    mutation.mutate(data);
  };

  if (reviewLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box sx={{ maxWidth: 800, mx: 'auto' }}>
        <Typography variant="h4" gutterBottom>
          {isEdit ? '编辑复盘记录' : '创建复盘记录'}
        </Typography>
        <Paper sx={{ p: 3, mt: 3 }}>
          <form onSubmit={handleSubmit(onSubmit)}>
            <Stack spacing={3}>
              <Controller
                name="instrument"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    select
                    label="标的"
                    error={!!errors.instrument}
                    helperText={errors.instrument?.message}
                    fullWidth
                  >
                    {instruments.map((inst) => (
                      <MenuItem key={inst.id} value={inst.id}>
                        {inst.name} ({inst.symbol})
                      </MenuItem>
                    ))}
                  </TextField>
                )}
              />

              <Controller
                name="review_date"
                control={control}
                render={({ field }) => (
                  <DatePicker
                    {...field}
                    label="交易日期"
                    slotProps={{
                      textField: {
                        error: !!errors.review_date,
                        helperText: errors.review_date?.message,
                        fullWidth: true,
                      },
                    }}
                  />
                )}
              />

              <Controller
                name="review_type"
                control={control}
                render={({ field }) => (
                  <TextField {...field} select label="复盘类型" fullWidth>
                    <MenuItem value="daily">日复盘</MenuItem>
                    <MenuItem value="weekly">周复盘</MenuItem>
                    <MenuItem value="monthly">月复盘</MenuItem>
                  </TextField>
                )}
              />

              <Controller
                name="market_stage"
                control={control}
                render={({ field }) => (
                  <TextField {...field} select label="市场阶段" fullWidth>
                    <MenuItem value="uptrend">上升趋势</MenuItem>
                    <MenuItem value="downtrend">下降趋势</MenuItem>
                    <MenuItem value="consolidation">盘整</MenuItem>
                    <MenuItem value="reversal">反转</MenuItem>
                  </TextField>
                )}
              />

              <Controller
                name="support_levels"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="支撑位"
                    placeholder="多个价位用逗号分隔，如: 100.5, 98.2"
                    fullWidth
                  />
                )}
              />

              <Controller
                name="resistance_levels"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="阻力位"
                    placeholder="多个价位用逗号分隔，如: 105.8, 108.3"
                    fullWidth
                  />
                )}
              />

              <Controller
                name="analysis_notes"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="分析笔记"
                    multiline
                    rows={6}
                    error={!!errors.analysis_notes}
                    helperText={errors.analysis_notes?.message}
                    fullWidth
                  />
                )}
              />

              <Box>
                <Typography component="legend" gutterBottom>
                  评分
                </Typography>
                <Controller
                  name="rating"
                  control={control}
                  render={({ field }) => <Rating {...field} />}
                />
              </Box>

              <Controller
                name="tags"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    label="标签"
                    placeholder="多个标签用逗号分隔，如: 突破, 回调"
                    fullWidth
                  />
                )}
              />

              <Stack direction="row" spacing={2} justifyContent="flex-end">
                <Button onClick={() => navigate('/reviews')}>取消</Button>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={mutation.isPending || isSubmitting}
                >
                  {mutation.isPending ? '提交中...' : isEdit ? '更新' : '创建'}
                </Button>
              </Stack>
            </Stack>
          </form>
        </Paper>
      </Box>
    </LocalizationProvider>
  );
}
