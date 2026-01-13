from pathlib import Path
import os
from dotenv import load_dotenv
from django.urls import reverse_lazy

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party apps
    'django_celery_beat',
    'django_celery_results',

    # Local apps
    'apps.core',
    'apps.market_data',
    'apps.technical_analysis',
    'apps.review',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_EXPIRES = 3600
CELERY_TASK_TIME_LIMIT = 600

# Django Unfold Configuration
UNFOLD = {
    "SITE_TITLE": "价格行为复盘系统",
    "SITE_HEADER": "价格行为复盘专家系统",
    "SITE_URL": "/",
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "市场数据",
                "separator": True,
                "items": [
                    {
                        "title": "标的管理",
                        "icon": "trending_up",
                        "link": lambda request: reverse_lazy("admin:market_data_instrument_changelist"),
                    },
                    {
                        "title": "K线数据",
                        "icon": "candlestick_chart",
                        "link": lambda request: reverse_lazy("admin:market_data_kline_changelist"),
                    },
                ],
            },
            {
                "title": "技术分析",
                "separator": True,
                "items": [
                    {
                        "title": "技术指标",
                        "icon": "analytics",
                        "link": lambda request: reverse_lazy("admin:technical_analysis_indicator_changelist"),
                    },
                    {
                        "title": "形态识别",
                        "icon": "pattern",
                        "link": lambda request: reverse_lazy("admin:technical_analysis_pattern_changelist"),
                    },
                    {
                        "title": "支撑阻力位",
                        "icon": "show_chart",
                        "link": lambda request: reverse_lazy("admin:technical_analysis_supportresistance_changelist"),
                    },
                ],
            },
            {
                "title": "复盘记录",
                "separator": True,
                "items": [
                    {
                        "title": "复盘记录",
                        "icon": "rate_review",
                        "link": lambda request: reverse_lazy("admin:review_reviewrecord_changelist"),
                    },
                    {
                        "title": "交易日志",
                        "icon": "receipt_long",
                        "link": lambda request: reverse_lazy("admin:review_tradelog_changelist"),
                    },
                ],
            },
        ],
    },
}


