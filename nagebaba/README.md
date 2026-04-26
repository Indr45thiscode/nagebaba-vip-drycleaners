# NAGEBABA VIP DRY CLEANERS - Dashboard

## Quick Start

```bash
# 1. Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Seed sample data
python manage.py seed_data

# 5. Start server
python manage.py runserver

# 6. Open browser: http://127.0.0.1:8000
# Login: use ADMIN_USERNAME / ADMIN_PASSWORD from your environment
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

## Admin Login
- Username: value from `ADMIN_USERNAME`
- Password: value from `ADMIN_PASSWORD`

## Production Setup
1. Set `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`
2. Configure PostgreSQL using `DATABASE_URL`
3. Run `python manage.py migrate`
4. Run `python manage.py collectstatic --noinput`
5. Start with `gunicorn config.wsgi:application`

## Render Deployment
This repository includes a root-level `render.yaml` blueprint for Render.

### Recommended Steps
1. Push your latest code to GitHub.
2. In Render, open `Blueprints` and create a new blueprint from this repository.
3. Render will create:
   - one web service
   - one PostgreSQL database
4. After the first deploy finishes, open the web service shell and run:
   - `python manage.py seed_data`

### Important Notes
- The Django app lives inside the `nagebaba/` directory.
- Render is configured to use `nagebaba` as the app root.
- This app now requires PostgreSQL through `DATABASE_URL`. SQLite is not supported.
- Uploaded media files will also not persist unless you later add external storage.
