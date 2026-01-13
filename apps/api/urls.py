from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.market_data.viewsets import InstrumentViewSet, KLineViewSet
from apps.technical_analysis.viewsets import IndicatorViewSet, PatternViewSet, SupportResistanceViewSet
from apps.review.viewsets import ReviewRecordViewSet, TradeLogViewSet

router = DefaultRouter()

# Market Data
router.register(r'instruments', InstrumentViewSet, basename='instrument')
router.register(r'klines', KLineViewSet, basename='kline')

# Technical Analysis
router.register(r'indicators', IndicatorViewSet, basename='indicator')
router.register(r'patterns', PatternViewSet, basename='pattern')
router.register(r'support-resistance', SupportResistanceViewSet, basename='support-resistance')

# Review
router.register(r'reviews', ReviewRecordViewSet, basename='review')
router.register(r'trades', TradeLogViewSet, basename='trade')

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),

    # JWT Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
