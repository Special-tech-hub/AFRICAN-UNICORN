# Deployment Guide

## Environment Variables

| Variable                  | Required | Description                                      |
|---------------------------|----------|--------------------------------------------------|
| `DEBUG`                   | Yes      | Set to `False` in production                     |
| `SECRET_KEY`              | Yes      | Django secret key — generate a random 50+ char string |
| `DATABASE_URL`            | Yes      | PostgreSQL: `postgres://user:pass@host:5432/db`  |
| `JWT_SECRET_KEY`          | Yes      | JWT signing key — separate from SECRET_KEY       |
| `OTP_PROVIDER`            | Yes      | `console` (dev) or `twilio` (prod)               |
| `ALLOWED_HOSTS`           | Yes      | Comma-separated: `yourdomain.com,www.yourdomain.com` |
| `CORS_ALLOWED_ORIGINS`    | Yes      | Frontend URL: `https://app.yourdomain.com`       |
| `TWILIO_ACCOUNT_SID`      | Prod     | Twilio account SID                               |
| `TWILIO_AUTH_TOKEN`       | Prod     | Twilio auth token                                |
| `TWILIO_FROM_NUMBER`      | Prod     | Twilio phone number                              |
| `MEDIA_STORAGE_PROVIDER`  | No       | `local` (default) or `s3`                        |
| `CLOUD_STORAGE_BUCKET`    | S3 only  | S3 bucket name                                   |
| `CLOUD_STORAGE_ACCESS_KEY`| S3 only  | AWS access key ID                                |
| `CLOUD_STORAGE_SECRET_KEY`| S3 only  | AWS secret access key                            |
| `REDIS_URL`               | No       | Redis for Celery: `redis://host:6379/0`          |

## Docker Deployment

```bash
# Copy and fill in your environment variables
cp .env.example .env

# Start all services
docker compose up -d

# Run migrations
docker compose exec backend python manage.py migrate

# Create admin user
docker compose exec backend python manage.py create_admin --phone 0700000000 --password YourSecurePass!

# (Optional) Load demo data
docker compose exec backend python manage.py seed_data
```

Services:
- **Backend** → http://localhost:8000
- **Frontend** → http://localhost:80
- **PostgreSQL** → localhost:5432
- **Redis** → localhost:6379

## Render Deployment

1. Create a new **Web Service** from your GitHub repo
2. Set **Build Command**: `pip install -r backend/requirements.txt`
3. Set **Start Command**: `cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Add all environment variables in the Render dashboard
5. Create a **PostgreSQL** add-on and link the `DATABASE_URL`

## Railway Deployment

1. Connect your GitHub repository
2. Add a **PostgreSQL** plugin — Railway auto-sets `DATABASE_URL`
3. Add a **Redis** plugin if using Celery
4. Set all required environment variables
5. Railway auto-deploys on push

## Production Checklist

- [ ] `DEBUG=False`
- [ ] Strong unique `SECRET_KEY` (50+ characters)
- [ ] Strong unique `JWT_SECRET_KEY`
- [ ] PostgreSQL `DATABASE_URL` configured
- [ ] `ALLOWED_HOSTS` set to your domain
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend URL
- [ ] `OTP_PROVIDER=twilio` with real credentials
- [ ] `python manage.py collectstatic` run
- [ ] Migrations applied: `python manage.py migrate`
- [ ] Media files configured (local or S3)
- [ ] HTTPS enabled (via reverse proxy or platform)
- [ ] `GET /health/` returns `{"status": "ok"}`
