# TakeOFF Driver Onboarding Platform

A full-stack web application for courier/logistics driver registration, onboarding, and application review.

---

## What It Does

Drivers can register with a phone number, verify via OTP, complete a 6-step onboarding form, upload required documents, and submit their application for review. Administrators can log in, inspect submitted applications and documents, and approve or reject applications with notes.

---

## Features

- Phone-based registration with OTP verification
- 6-step onboarding: Personal → Contact → Identity → Vehicle → Documents → Review
- Secure document uploads (PDF, JPG, PNG; max 10 MB; MIME validation)
- Application state machine: DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED / REJECTED
- Admin dashboard with statistics, search, filter, approve/reject
- In-app notifications for all key events
- JWT authentication with auto-refresh
- Role-based access control (DRIVER / ADMIN)
- Unique application references (TO-YYYY-NNNNN)

---

## Technology Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Python 3.13, Django 4.2, Django REST Framework  |
| Auth       | JWT (djangorestframework-simplejwt)             |
| API Docs   | drf-spectacular (OpenAPI 3 / Swagger UI)        |
| Frontend   | React 18, Vite, TypeScript, Tailwind CSS        |
| State      | Zustand                                         |
| Forms      | React Hook Form + Zod                           |
| Database   | SQLite (dev) / PostgreSQL (prod)                |
| Storage    | Local media (dev) / S3-compatible (prod)        |

---

## Local Setup

### Prerequisites

- Python 3.10+ (Python 3.13 tested)
- Node.js 18+ and npm (for frontend)

### 1. Clone the repository

```
git clone <repo-url>
cd "AFRICA UNIRCORN"
```

### 2. Backend setup

```
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell:**
```
.\.venv\Scripts\Activate.ps1
```

**Windows CMD:**
```
.venv\Scripts\activate.bat
```

**macOS / Linux:**
```
source .venv/bin/activate
```

Install dependencies:
```
pip install -r requirements-core.txt
```

### 3. Environment variables

Copy the example file:
```
copy .env.example .env       # Windows
cp .env.example .env         # macOS/Linux
```

The default `.env` works for local development with SQLite. Edit as needed.

### 4. Run migrations

```
python manage.py migrate
```

### 5. Seed demo data

```
python manage.py seed_data
```

This creates 1 admin and 5 driver accounts in all statuses.

### 6. Start the backend

```
python manage.py runserver
```

Backend runs at: **http://127.0.0.1:8000**

### 7. Frontend setup (optional)

```
cd ../frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## Demo Accounts

| Role   | Phone       | Password    | App Status   |
|--------|-------------|-------------|--------------|
| Admin  | 0700000000  | Admin1234!  | N/A          |
| Driver | 0771100001  | Driver001!  | APPROVED     |
| Driver | 0771100002  | Driver002!  | REJECTED     |
| Driver | 0771100003  | Driver003!  | UNDER_REVIEW |
| Driver | 0771100004  | Driver004!  | SUBMITTED    |
| Driver | 0771100005  | Driver005!  | DRAFT        |

---

## OTP Development Mode

When `OTP_PROVIDER=console` (the default for development), OTPs are **printed to the Django server console** instead of being sent via SMS. Look for lines like:

```
[DEV OTP] Phone: 0771234567
[DEV OTP] OTP Code: 123456
```

To use a real SMS provider, set `OTP_PROVIDER=twilio` and provide your Twilio credentials in `.env`.

---

## API Documentation

With the server running, visit:

- **Swagger UI**: http://127.0.0.1:8000/api/docs/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/
- **Health Check**: http://127.0.0.1:8000/health/

---

## Running Tests

```
cd backend
.venv\Scripts\pip.exe install pytest pytest-django pytest-cov
.venv\Scripts\python.exe -m pytest apps/ -v
```

---

## Key API Endpoints

| Method | Endpoint                                   | Description                    |
|--------|--------------------------------------------|--------------------------------|
| POST   | /api/auth/register/                        | Register new driver            |
| POST   | /api/auth/verify-otp/                      | Verify OTP                     |
| POST   | /api/auth/login/                           | Login                          |
| GET    | /api/driver/profile/                       | Get/update profile             |
| POST   | /api/driver/documents/                     | Upload document                |
| POST   | /api/applications/{id}/submit/             | Submit application             |
| GET    | /api/admin/applications/                   | List all applications (admin)  |
| POST   | /api/admin/applications/{id}/approve/      | Approve application (admin)    |
| POST   | /api/admin/applications/{id}/reject/       | Reject application (admin)     |
| GET    | /api/admin/statistics/                     | Dashboard statistics (admin)   |

---

## Docker

```
docker compose up
```

Services: backend (port 8000), frontend (port 80), postgres, redis.

---

## Security Notes

- Passwords are hashed with Django's PBKDF2-SHA256
- OTPs are stored as PBKDF2-HMAC-SHA256 hashes — never plaintext
- JWT tokens: 15-minute access, 7-day refresh with rotation
- Documents served only through authenticated endpoints — never directly accessible
- All secrets must be in `.env` — never committed to source control

---

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY` and `JWT_SECRET_KEY`
3. Set `DATABASE_URL` to a PostgreSQL connection string
4. Set `ALLOWED_HOSTS` to your domain
5. Set `OTP_PROVIDER=twilio` with Twilio credentials
6. Run `python manage.py collectstatic`
7. Use gunicorn: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

See `docs/DEPLOYMENT.md` for full deployment instructions.
