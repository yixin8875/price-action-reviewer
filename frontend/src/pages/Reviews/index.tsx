import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  Chip,
  IconButton,
  Rating,
  Skeleton,
} from '@mui/material';
import { Add, Edit } from '@mui/icons-material';
import apiClient from '../../services/api';
import type { ReviewRecord } from '../../types';

export default function Reviews() {
  const [reviews, setReviews] = useState<ReviewRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await apiClient.get('/reviews/');
      setReviews(response.data);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">复盘记录</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => navigate('/reviews/new')}>
          创建复盘
        </Button>
      </Box>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }, gap: 3 }}>
        {isLoading ? (
          [1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardContent>
                <Skeleton variant="text" width="70%" height={32} />
                <Skeleton variant="text" width="40%" />
                <Skeleton variant="rectangular" height={20} sx={{ mt: 1, width: 100 }} />
                <Skeleton variant="text" sx={{ mt: 2 }} />
                <Skeleton variant="text" />
              </CardContent>
            </Card>
          ))
        ) : (
          reviews.map((review) => (
            <Card key={review.id}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <Typography variant="h6" gutterBottom>
                    {review.instrument_name || `标的 #${review.instrument}`}
                  </Typography>
                  <IconButton size="small" onClick={() => navigate(`/reviews/${review.id}/edit`)}>
                    <Edit fontSize="small" />
                  </IconButton>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {review.review_date}
                </Typography>
                {review.rating && (
                  <Rating value={review.rating} readOnly size="small" sx={{ mt: 1 }} />
                )}
                {review.outcome && (
                  <Chip
                    label={review.outcome}
                    color={review.outcome === 'win' ? 'success' : review.outcome === 'loss' ? 'error' : 'default'}
                    size="small"
                    sx={{ mt: 1 }}
                  />
                )}
                {review.analysis_notes && (
                  <Typography variant="body2" sx={{ mt: 2 }}>
                    {review.analysis_notes.substring(0, 100)}
                    {review.analysis_notes.length > 100 && '...'}
                  </Typography>
                )}
                {review.tags && review.tags.length > 0 && (
                  <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {review.tags.map((tag, idx) => (
                      <Chip key={idx} label={tag} size="small" variant="outlined" />
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </Box>
    </>
  );
}
