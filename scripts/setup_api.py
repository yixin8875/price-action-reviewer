#!/usr/bin/env python3
"""
Test script for Price Action Reviewer API
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/boohee/Documents/trae_projects/price-action-reviewer')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth.models import User
from apps.market_data.models import Instrument, KLine
from datetime import date
from decimal import Decimal

def create_test_user():
    """Create a test user for API authentication"""
    username = 'testuser'
    password = 'testpass123'

    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': 'test@example.com'}
    )

    if created:
        user.set_password(password)
        user.save()
        print(f"✓ Created test user: {username}")
    else:
        print(f"✓ Test user already exists: {username}")

    return username, password

def create_test_data():
    """Create some test data"""
    # Create test instrument
    instrument, created = Instrument.objects.get_or_create(
        symbol='000001',
        defaults={
            'name': '平安银行',
            'market_type': 'STOCK',
            'exchange': 'SZSE',
            'is_active': True
        }
    )

    if created:
        print(f"✓ Created test instrument: {instrument.symbol}")
    else:
        print(f"✓ Test instrument already exists: {instrument.symbol}")

    # Create test K-line
    kline, created = KLine.objects.get_or_create(
        instrument=instrument,
        period='1d',
        trade_date=date.today(),
        defaults={
            'open_price': Decimal('10.00'),
            'high_price': Decimal('10.50'),
            'low_price': Decimal('9.80'),
            'close_price': Decimal('10.20'),
            'volume': 1000000,
            'amount': Decimal('10200000.00')
        }
    )

    if created:
        print(f"✓ Created test K-line for {instrument.symbol}")
    else:
        print(f"✓ Test K-line already exists for {instrument.symbol}")

def print_api_info():
    """Print API information"""
    print("\n" + "="*60)
    print("Price Action Reviewer API - Setup Complete")
    print("="*60)
    print("\nAPI Endpoints:")
    print("  Base URL: http://localhost:8000/api/v1/")
    print("\nAuthentication:")
    print("  Login: POST /api/v1/auth/login/")
    print("  Refresh: POST /api/v1/auth/refresh/")
    print("  Verify: POST /api/v1/auth/verify/")
    print("\nAPI Documentation:")
    print("  Swagger UI: http://localhost:8000/api/v1/docs/")
    print("  Schema: http://localhost:8000/api/v1/schema/")
    print("\nResource Endpoints:")
    print("  Instruments: /api/v1/instruments/")
    print("  K-Lines: /api/v1/klines/")
    print("  Indicators: /api/v1/indicators/")
    print("  Patterns: /api/v1/patterns/")
    print("  Support/Resistance: /api/v1/support-resistance/")
    print("  Reviews: /api/v1/reviews/")
    print("  Trades: /api/v1/trades/")
    print("\nTest Credentials:")
    print("  Username: testuser")
    print("  Password: testpass123")
    print("\nTo start the server:")
    print("  python3 manage.py runserver")
    print("="*60)

if __name__ == '__main__':
    print("Setting up Price Action Reviewer API...\n")

    try:
        create_test_user()
        create_test_data()
        print_api_info()
        print("\n✓ Setup completed successfully!")
    except Exception as e:
        print(f"\n✗ Error during setup: {e}")
        import traceback
        traceback.print_exc()
