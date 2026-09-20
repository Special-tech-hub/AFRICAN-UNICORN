# Architecture

## System Overview

```
┌─────────────┐     HTTPS/JSON      ┌─────────────────────────────┐
│   Browser   │ ──────────────────► │     Django (port 8000)      │
│  React/Vite │ ◄────────────────── │  DRF + SimpleJWT + Swagger  │
└─────────────┘                     └──────────┬──────────────────┘
                                               │
                                    ┌──────────▼──────────┐
                                    │  SQLite / PostgreSQL │
                                    └─────────────────────┘
```

## Backend Django Apps

| App             | Responsibility                                    |
|-----------------|---------------------------------------------------|
| `accounts`      | User model, registration, OTP, login, JWT         |
| `onboarding`    | DriverProfile, IdentityVerification, Vehicle      |
| `documents`     | File upload, MIME validation, secure serving      |
| `applications`  | DriverApplication, state machine, references      |
| `reviews`       | Admin list/detail/approve/reject, statistics      |
| `notifications` | In-app notification records                       |

## Core Module

`backend/core/` contains shared utilities:
- `permissions.py` — IsDriverUser, IsAdminUser, IsPhoneVerified, IsOwnerOrAdmin
- `pagination.py` — StandardPagination (20/page, max 100)
- `exceptions.py` — Consistent JSON error format
- `views.py` — HealthCheckView

## Authentication Flow

```
Register → OTP sent to console/SMS
         → POST /api/auth/verify-otp/
         → JWT access (15min) + refresh (7 days) issued
         → Auto-refresh on 401 via Axios interceptor
```

## Application State Machine

```
DRAFT → SUBMITTED → UNDER_REVIEW → APPROVED
                                 → REJECTED
```

All transitions are recorded in `ApplicationStatusHistory`.

## Frontend Architecture

- **React Router v6** — client-side routing
- **Zustand** — lightweight global state (auth + onboarding)
- **React Hook Form + Zod** — schema-driven form validation
- **Axios** — API client with JWT interceptors and auto-refresh

## Request Lifecycle

1. Browser sends JWT in `Authorization: Bearer` header
2. Django `JWTAuthentication` validates token
3. View checks permissions (IsDriverUser / IsAdminUser)
4. Service layer executes business logic
5. Serializer formats JSON response
