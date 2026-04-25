# NAGEBABA VIP DRY CLEANERS - Dashboard

## Quick Start

```bash
# 1. Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install django pillow

# For PostgreSQL support (optional, SQLite works by default):
# pip install psycopg2-binary

# 3. Apply migrations
python manage.py migrate

# 4. Seed sample data & create admin user
python manage.py seed_data

# 5. Start server
python manage.py runserver

# 6. Open browser: http://127.0.0.1:8000
# Login: admin / admin123
```

## Features
- Dashboard with today's stats
- Order management (create, track, update status)
- Customer management with full history
- Multi-item orders with auto-pricing
- Payment tracking (Cash, UPI, PhonePe, Google Pay)
- Thermal-style printable receipts
- Expense tracking (daily/monthly/yearly)
- Analytics with Chart.js charts
- Dark/Light theme toggle
- Mobile responsive

## Default Login
- Username: `admin`
- Password: `admin123`

## Production Setup
1. Set `DEBUG = False` in settings.py
2. Change `SECRET_KEY` to a secure random key
3. Configure PostgreSQL in DATABASES
4. Run `python manage.py collectstatic`
5. Use gunicorn + nginx for deployment
