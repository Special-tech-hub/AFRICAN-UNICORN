# Design Document — TakeOFF Driver Onboarding Platform

## Overview

The TakeOFF Driver Onboarding Platform is a full-stack web application composed of a Django REST Framework backend, a React/TypeScript/Tailwind CSS frontend, a PostgreSQL database, and a Redis instance for caching and Celery task queuing. The system supports two user roles (DRIVER and ADMIN), enforces a strict application state machine, handles secure document uploads, and provides an in-app notification system.

This document describes the high-level and low-level design decisions, component architecture, data models, API contract, and key algorithms.

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client (Browser)                          │
│   React + Vite + TypeScript + Tailwind CSS                       │
│   Axios for API calls │ React Router for navigation              │
│   React Hook Form + Zod for validation                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / JSON REST
┌───────────────────────────▼─────────────────────────────────────┐
│                     Django Application                            │
│   Django REST Framework │ Simple JWT │ drf-spectacular (OpenAPI) │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│   │ accounts │ │onboarding│ │documents │ │   applications   │  │
│   │   app    │ │   app    │ │   app    │ │       app        │  │
│   └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  │
│   ┌──────────┐ ┌──────────┐                                      │
│   │ reviews  │ │  notifs  │                                      │
│   │   app    │ │   app    │                                      │
│   └──────────┘ └──────────┘                                      │
└─────────┬──────────────────────────────┬───────────────────────-┘
          │                              │
┌─────────▼──────────┐        ┌──────────▼────────────┐
│    PostgreSQL       │        │    Redis               │
│    (primary DB)     │        │    (cache + Celery)    │
└────────────────────┘        └───────────────────────-┘
          │
┌─────────▼──────────┐
│  Media Storage      │
│  Local (dev)        │
│  S3-compatible (prod│
└────────────────────┘
```

### Directory Structure

```
takeoff-driver-onboarding/
├── backend/
│   ├── config/                  # Django project settings
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── accounts/            # User model, auth, OTP
│   │   ├── onboarding/          # DriverProfile, Identity, Vehicle
│   │   ├── documents/           # Document upload/storage
│   │   ├── applications/        # DriverApplication, state machine
│   │   ├── reviews/             # Admin review actions
│   │   └── notifications/       # In-app notifications
│   ├── core/                    # Shared utilities, permissions, mixins
│   ├── manage.py
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # Axios client and API functions
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/
│   │   │   ├── auth/            # Register, Login, OTP Verify
│   │   │   ├── onboarding/      # 6-step onboarding flow
│   │   │   ├── status/          # Application status page
│   │   │   └── admin/           # Admin dashboard and review
│   │   ├── hooks/               # Custom React hooks
│   │   ├── store/               # Zustand global state
│   │   ├── types/               # TypeScript interfaces
│   │   └── utils/               # Helpers, validators
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATABASE.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── DECISIONS.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

---

## Backend Design

### Django Apps

#### `accounts` app
Responsibilities: custom User model, registration, login, OTP generation/verification, JWT management.

Models: `User`, `OTPVerification`

Key files:
- `models.py` — Custom AbstractBaseUser with phone_number as USERNAME_FIELD
- `serializers.py` — RegisterSerializer, LoginSerializer, OTPVerifySerializer
- `views.py` — RegisterView, LoginView, OTPVerifyView, OTPResendView, TokenRefreshView, LogoutView
- `services.py` — OTPService (generate, hash, verify, resend logic)
- `otp_providers.py` — ConsoleOTPProvider, SMSOTPProvider (pluggable via OTP_PROVIDER env var)
- `permissions.py` — IsDriver, IsAdmin, IsPhoneVerified

#### `onboarding` app
Responsibilities: DriverProfile, IdentityVerification, Vehicle creation and updates.

Models: `DriverProfile`, `IdentityVerification`, `Vehicle`

Key files:
- `models.py` — Profile, Identity, Vehicle models
- `serializers.py` — Per-model serializers with validation
- `views.py` — CRUD views for each model (driver-scoped)
- `services.py` — OnboardingService (profile completeness check)

#### `documents` app
Responsibilities: Secure file upload, MIME validation, safe filename generation, access control.

Models: `Document`

Key files:
- `models.py` — Document model
- `serializers.py` — DocumentUploadSerializer
- `views.py` — DocumentListCreateView, DocumentDeleteView, DocumentServeView
- `validators.py` — MIMEValidator, ExtensionValidator, SizeValidator
- `storage.py` — SafeFileStorage wrapper

#### `applications` app
Responsibilities: DriverApplication lifecycle, state machine, application reference generation.

Models: `DriverApplication`, `ApplicationStatusHistory`

Key files:
- `models.py` — DriverApplication, ApplicationStatusHistory
- `serializers.py` — ApplicationSerializer, StatusHistorySerializer
- `views.py` — ApplicationCreateView, ApplicationSubmitView, ApplicationStatusView
- `state_machine.py` — ApplicationStateMachine (transition logic + history recording)
- `services.py` — ApplicationService (completeness validation, reference generation)
- `reference.py` — Atomic reference number generator using DB sequence

#### `reviews` app
Responsibilities: Admin review actions (approve, reject, move to under_review).

Models: No new models; operates on DriverApplication and ApplicationStatusHistory.

Key files:
- `serializers.py` — ReviewSerializer, ApproveSerializer, RejectSerializer
- `views.py` — AdminApplicationListView, AdminApplicationDetailView, ApproveView, RejectView
- `services.py` — ReviewService

#### `notifications` app
Responsibilities: Create and serve in-app notifications.

Models: `Notification`

Key files:
- `models.py` — Notification model
- `serializers.py` — NotificationSerializer
- `views.py` — NotificationListView, NotificationMarkReadView
- `services.py` — NotificationService (create_notification helper)

#### `core` module
Responsibilities: Shared utilities used across apps.

Key files:
- `permissions.py` — IsDriverUser, IsAdminUser, IsOwnerOrAdmin
- `pagination.py` — StandardPagination (20/page default, max 100)
- `exceptions.py` — Custom DRF exception handler
- `mixins.py` — AuditMixin, TimestampMixin

---

## Data Models

### User
```
id                  UUID        PK
phone_number        VARCHAR(20) UNIQUE NOT NULL
email               VARCHAR(254) NULL
password            VARCHAR(128) NOT NULL (hashed)
role                VARCHAR(10) CHOICES: DRIVER, ADMIN
is_phone_verified   BOOLEAN     DEFAULT False
is_active           BOOLEAN     DEFAULT True
is_staff            BOOLEAN     DEFAULT False
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### OTPVerification
```
id                  UUID        PK
user                FK(User)    NOT NULL
otp_hash            VARCHAR(128) NOT NULL
expires_at          TIMESTAMP   NOT NULL
attempt_count       INTEGER     DEFAULT 0
is_active           BOOLEAN     DEFAULT True
verified_at         TIMESTAMP   NULL
created_at          TIMESTAMP
```
Index: (user, is_active)

### DriverProfile
```
id                  UUID        PK
user                OneToOne(User) NOT NULL
first_name          VARCHAR(100)
middle_name         VARCHAR(100) NULL
last_name           VARCHAR(100)
date_of_birth       DATE
gender              VARCHAR(20)
nationality         VARCHAR(100)
email               VARCHAR(254) NULL
street_address      TEXT
city                VARCHAR(100)
province            VARCHAR(100)
emergency_contact_name  VARCHAR(200)
emergency_contact_phone VARCHAR(20)
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### IdentityVerification
```
id                  UUID        PK
driver              OneToOne(User) NOT NULL
id_type             VARCHAR(20) CHOICES: NATIONAL_ID, PASSPORT
id_number           VARCHAR(100)
drivers_license_number  VARCHAR(100)
license_expiry_date DATE
is_license_expired  BOOLEAN     DEFAULT False (computed on save)
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### Vehicle
```
id                  UUID        PK
driver              OneToOne(User) NOT NULL
vehicle_type        VARCHAR(20) CHOICES: MOTORCYCLE, SEDAN, HATCHBACK, PICKUP, VAN, TRUCK
make                VARCHAR(100)
model               VARCHAR(100)
year                INTEGER
registration_number VARCHAR(50)
colour              VARCHAR(50)
created_at          TIMESTAMP
updated_at          TIMESTAMP
```

### Document
```
id                  UUID        PK
driver              FK(User)    NOT NULL
application         FK(DriverApplication) NULL
document_type       VARCHAR(30) CHOICES: NATIONAL_ID, DRIVERS_LICENSE, VEHICLE_REGISTRATION, INSURANCE, INSPECTION
file                FileField   (stored outside public root)
original_filename   VARCHAR(255)
safe_filename       VARCHAR(255)
file_size           INTEGER     (bytes)
mime_type           VARCHAR(100)
verification_status VARCHAR(20) DEFAULT: PENDING
uploaded_at         TIMESTAMP
```
Index: (driver, document_type)

### DriverApplication
```
id                  UUID        PK
application_reference  VARCHAR(20) UNIQUE (TO-YYYY-NNNNN)
driver              OneToOne(User) NOT NULL
status              VARCHAR(20) DEFAULT: DRAFT CHOICES: DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED
submitted_at        TIMESTAMP   NULL
reviewed_at         TIMESTAMP   NULL
reviewed_by         FK(User)    NULL (Admin who last acted)
review_note         TEXT        NULL
created_at          TIMESTAMP
updated_at          TIMESTAMP
```
Index: (status), (driver), (application_reference)

### ApplicationStatusHistory
```
id                  UUID        PK
application         FK(DriverApplication) NOT NULL
previous_status     VARCHAR(20)
new_status          VARCHAR(20)
changed_by          FK(User)    NOT NULL
note                TEXT        NULL
created_at          TIMESTAMP
```
Index: (application, created_at)

### ApplicationSequence (for reference generation)
```
id                  INTEGER     PK AUTO
year                INTEGER     UNIQUE NOT NULL
last_sequence       INTEGER     DEFAULT 0
```
Uses `SELECT FOR UPDATE` to generate atomic, unique sequence numbers per year.

### Notification
```
id                  UUID        PK
user                FK(User)    NOT NULL
notification_type   VARCHAR(50)
title               VARCHAR(200)
message             TEXT
is_read             BOOLEAN     DEFAULT False
created_at          TIMESTAMP
```
Index: (user, is_read), (user, created_at)

---

## Application State Machine

```
DRAFT
  │
  ▼ (Driver submits — all fields + docs validated)
SUBMITTED
  │
  ▼ (Admin opens application)
UNDER_REVIEW
  │         │
  ▼         ▼
APPROVED  REJECTED (requires reason)
```

### Transition Table

| From         | To           | Actor  | Trigger                        |
|--------------|--------------|--------|--------------------------------|
| DRAFT        | SUBMITTED    | Driver | POST /api/applications/{id}/submit/ |
| SUBMITTED    | UNDER_REVIEW | Admin  | GET /api/admin/applications/{id}/ (auto) |
| UNDER_REVIEW | APPROVED     | Admin  | POST /api/admin/applications/{id}/approve/ |
| UNDER_REVIEW | REJECTED     | Admin  | POST /api/admin/applications/{id}/reject/ |

### StateMachine Implementation

```python
VALID_TRANSITIONS = {
    'DRAFT': ['SUBMITTED'],
    'SUBMITTED': ['UNDER_REVIEW'],
    'UNDER_REVIEW': ['APPROVED', 'REJECTED'],
    'APPROVED': [],
    'REJECTED': [],
}

class ApplicationStateMachine:
    def transition(self, application, new_status, actor, note=None):
        if new_status not in VALID_TRANSITIONS[application.status]:
            raise InvalidTransitionError(...)
        
        with transaction.atomic():
            old_status = application.status
            application.status = new_status
            application.save()
            
            ApplicationStatusHistory.objects.create(
                application=application,
                previous_status=old_status,
                new_status=new_status,
                changed_by=actor,
                note=note,
            )
            
            NotificationService.notify_status_change(application, new_status)
```

---

## Authentication Flow

### Registration
```
POST /api/auth/register/
  → Validate phone uniqueness, password strength
  → Create User (role=DRIVER, is_phone_verified=False)
  → OTPService.generate_and_send(user)
  → Return 201 {message: "OTP sent"}
```

### OTP Verification
```
POST /api/auth/verify-otp/
  → Find active OTPVerification for phone_number
  → Check expiry, attempt count
  → Compare submitted OTP with otp_hash using constant-time compare
  → Mark User.is_phone_verified = True
  → Invalidate OTPVerification
  → Issue JWT access + refresh tokens
  → Return 200 {access, refresh}
```

### Login
```
POST /api/auth/login/
  → Authenticate phone + password
  → Check is_phone_verified
  → Issue JWT access + refresh tokens
  → Return 200 {access, refresh}
```

### JWT Configuration
- Access token: 15 minutes
- Refresh token: 7 days
- Algorithm: HS256
- Stored in: httpOnly cookies (optional) or response body (configurable)
- Library: `djangorestframework-simplejwt`

---

## OTP Service Design

```python
class OTPService:
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    RESEND_COOLDOWN_SECONDS = 60

    @classmethod
    def generate_and_send(cls, user):
        # 1. Check cooldown on most recent OTPVerification
        # 2. Invalidate previous active OTPs
        # 3. Generate cryptographically secure OTP (secrets.randbelow)
        # 4. Hash OTP with SHA-256 + per-record salt
        # 5. Save OTPVerification record
        # 6. Dispatch via configured provider
        pass

    @classmethod
    def verify(cls, phone_number, submitted_otp):
        # 1. Find active, non-expired OTPVerification
        # 2. Increment attempt_count atomically
        # 3. Compare hash(submitted_otp + salt) == stored_hash
        # 4. Handle failure/success cases
        pass
```

### OTP Provider Abstraction
```python
class BaseOTPProvider:
    def send(self, phone_number: str, otp: str) -> None:
        raise NotImplementedError

class ConsoleOTPProvider(BaseOTPProvider):
    def send(self, phone_number: str, otp: str) -> None:
        logger.info(f"[DEV OTP] Phone: {phone_number} | OTP: {otp}")

class TwilioOTPProvider(BaseOTPProvider):
    def send(self, phone_number: str, otp: str) -> None:
        # Uses TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER from env
        pass

def get_otp_provider() -> BaseOTPProvider:
    provider = settings.OTP_PROVIDER
    if provider == 'console':
        return ConsoleOTPProvider()
    elif provider == 'twilio':
        return TwilioOTPProvider()
    raise ValueError(f"Unknown OTP provider: {provider}")
```

---

## Document Storage Design

### File Validation Pipeline
```
Upload request received
  │
  ├─ Check Content-Type header (pre-validation)
  ├─ Read first 261 bytes of file content → python-magic MIME detection
  ├─ Validate MIME type in ALLOWED_MIME_TYPES
  ├─ Extract file extension from original filename
  ├─ Validate extension matches MIME type
  ├─ Check file size ≤ 10 MB
  └─ Accept → proceed to storage
```

### Safe Filename Generation
```python
import uuid
from pathlib import Path

def generate_safe_filename(original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4().hex}{extension}"

def document_upload_path(instance, filename: str) -> str:
    safe_name = generate_safe_filename(filename)
    return f"documents/{instance.driver.id}/{safe_name}"
```

### Access Control for Document Serving
- Documents are NOT served from `MEDIA_URL` directly in production
- A `DocumentServeView` validates JWT, checks ownership or ADMIN role, then streams the file using Django's `FileResponse` or S3 pre-signed URL

---

## Application Reference Generation

```python
from django.db import transaction

def generate_application_reference(year: int) -> str:
    with transaction.atomic():
        seq_obj, _ = ApplicationSequence.objects.select_for_update().get_or_create(year=year)
        seq_obj.last_sequence += 1
        seq_obj.save()
        return f"TO-{year}-{seq_obj.last_sequence:05d}"
```

This uses `SELECT FOR UPDATE` to prevent race conditions under concurrent requests.

---

## API Design

### Authentication Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/register/ | None | Register new driver |
| POST | /api/auth/verify-otp/ | None | Verify OTP |
| POST | /api/auth/resend-otp/ | None | Resend OTP (rate limited) |
| POST | /api/auth/login/ | None | Login |
| POST | /api/auth/refresh/ | None | Refresh JWT |
| POST | /api/auth/logout/ | JWT | Logout (blacklist refresh token) |

### Driver Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET/PUT | /api/driver/profile/ | JWT+Driver | Personal + contact details |
| GET/PUT | /api/driver/identity/ | JWT+Driver | Identity verification details |
| GET/PUT | /api/driver/vehicle/ | JWT+Driver | Vehicle details |
| GET | /api/driver/documents/ | JWT+Driver | List own documents |
| POST | /api/driver/documents/ | JWT+Driver | Upload document |
| DELETE | /api/driver/documents/{id}/ | JWT+Driver | Delete document (DRAFT only) |

### Application Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/applications/me/ | JWT+Driver | Get own application |
| POST | /api/applications/ | JWT+Driver | Create application (DRAFT) |
| POST | /api/applications/{id}/submit/ | JWT+Driver | Submit application |
| GET | /api/applications/{id}/status/ | JWT+Driver | Get status + history |

### Admin Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /api/admin/applications/ | JWT+Admin | List all applications |
| GET | /api/admin/applications/{id}/ | JWT+Admin | Get full application details |
| POST | /api/admin/applications/{id}/approve/ | JWT+Admin | Approve application |
| POST | /api/admin/applications/{id}/reject/ | JWT+Admin | Reject application (reason required) |
| GET | /api/admin/statistics/ | JWT+Admin | Dashboard statistics |

### System Endpoints
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health/ | None | Health check |
| GET | /api/schema/ | None (dev) | OpenAPI schema |
| GET | /api/docs/ | None (dev) | Swagger UI |

---

## Frontend Design

### Routing Structure
```
/                          → Redirect to /login or /dashboard
/register                  → DriverRegistrationPage
/verify-otp                → OTPVerificationPage
/login                     → LoginPage
/onboarding                → OnboardingLayout (protected, phone-verified)
  /onboarding/personal     → PersonalDetailsStep
  /onboarding/contact      → ContactDetailsStep
  /onboarding/identity     → IdentityVerificationStep
  /onboarding/vehicle      → VehicleDetailsStep
  /onboarding/documents    → DocumentUploadStep
  /onboarding/review       → ReviewAndSubmitStep
/application/status        → ApplicationStatusPage
/application/success       → SubmissionSuccessPage
/admin                     → AdminLayout (protected, ADMIN role)
  /admin/dashboard         → AdminDashboardPage
  /admin/applications      → ApplicationListPage
  /admin/applications/:id  → ApplicationReviewPage
```

### State Management (Zustand)
```typescript
interface AuthStore {
  user: User | null;
  accessToken: string | null;
  login: (tokens: Tokens) => void;
  logout: () => void;
}

interface OnboardingStore {
  currentStep: number;
  applicationId: string | null;
  personalDetails: PersonalDetails | null;
  contactDetails: ContactDetails | null;
  identityDetails: IdentityDetails | null;
  vehicleDetails: VehicleDetails | null;
  documents: Document[];
  setStep: (step: number) => void;
  updateSection: (section: string, data: any) => void;
}
```

### Onboarding Progress Component
```typescript
// Steps array drives both the progress bar and routing
const STEPS = [
  { id: 1, label: 'Personal',   path: '/onboarding/personal' },
  { id: 2, label: 'Contact',    path: '/onboarding/contact' },
  { id: 3, label: 'Identity',   path: '/onboarding/identity' },
  { id: 4, label: 'Vehicle',    path: '/onboarding/vehicle' },
  { id: 5, label: 'Documents',  path: '/onboarding/documents' },
  { id: 6, label: 'Review',     path: '/onboarding/review' },
];
```

### Form Validation Strategy
- Frontend: React Hook Form + Zod schemas for real-time validation
- Backend: DRF serializer validation (always enforced, cannot be bypassed)
- Both layers validate the same rules independently

### Axios Configuration
```typescript
// Automatic token refresh on 401
// Request interceptor: attach Authorization: Bearer {accessToken}
// Response interceptor: on 401, attempt refresh, retry original request
```

---

## Security Design

### Password Hashing
- Django's default PBKDF2-SHA256 with 720,000 iterations (Django 4.2+)
- Configurable to Argon2 via `PASSWORD_HASHERS` setting

### JWT Security
- Short-lived access tokens (15 min) reduce exposure window
- Refresh tokens stored in `OutstandingToken` table for blacklisting
- Logout blacklists the refresh token

### OTP Security
- OTP stored as `PBKDF2-HMAC-SHA256(otp + salt)` — never plaintext
- Constant-time comparison to prevent timing attacks
- Max 5 attempts, 60s cooldown, 10-minute expiry

### File Upload Security
- MIME detection from file bytes (python-magic)
- UUID-based filenames prevent path traversal and enumeration
- Files stored at `MEDIA_ROOT/documents/{user_id}/{uuid}.ext` outside web root
- Authenticated serve endpoint for access control

### CORS
```python
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True
```

### Rate Limiting
- `django-ratelimit` on OTP endpoints: 5 requests per phone per 10 minutes
- Returns 429 with `Retry-After` header

---

## Notifications Design

```python
class NotificationService:
    @staticmethod
    def create(user, notification_type, title, message):
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
        )

NOTIFICATION_TEMPLATES = {
    'OTP_SENT':        ('OTP Sent', 'Your OTP has been sent to {phone}.'),
    'PHONE_VERIFIED':  ('Phone Verified', 'Your phone number has been verified.'),
    'APP_SUBMITTED':   ('Application Submitted', 'Your application {ref} has been submitted.'),
    'APP_UNDER_REVIEW':('Application Under Review', 'Your application {ref} is under review.'),
    'APP_APPROVED':    ('Application Approved', 'Congratulations! Your application {ref} has been approved.'),
    'APP_REJECTED':    ('Application Rejected', 'Your application {ref} has been rejected. Reason: {reason}'),
}
```

---

## Seed Data Design

The `management/commands/seed_data.py` command creates:
- 1 Admin user: `admin / admin1234`
- 5 Driver accounts representing each status:
  - `tendai.moyo@example.com` / `Driver001!` → APPROVED
  - `amara.diallo@example.com` / `Driver002!` → REJECTED
  - `kofi.asante@example.com` / `Driver003!` → UNDER_REVIEW
  - `fatima.nkosi@example.com` / `Driver004!` → SUBMITTED
  - `chidi.okafor@example.com` / `Driver005!` → DRAFT
- Fictional vehicles, documents (placeholder files), and status histories

---

## Testing Strategy

### Backend (pytest-django)
- Unit tests: OTPService, ApplicationStateMachine, reference generator, validators
- Integration tests: full API flows via DRF test client
- Fixtures: factory_boy factories for all models

### Frontend (Vitest + React Testing Library)
- Component tests: form validation, step navigation, error states
- API mock tests: axios-mock-adapter for simulated responses

### Coverage Target
- Backend: ≥80% on business-critical modules (accounts, applications, documents)

---

## Deployment Design

### Environment Variables
All secrets and environment-specific config via `.env` loaded by `django-environ`.

### Docker
- `Dockerfile.backend` — Python 3.12 slim, gunicorn
- `Dockerfile.frontend` — Node 20 builder + nginx static serve
- `docker-compose.yml` — backend, frontend, postgres, redis services

### Production Checklist
- `DEBUG=False`
- `ALLOWED_HOSTS` from env
- `SECURE_SSL_REDIRECT=True`
- Static files: `whitenoise` for backend static; nginx for frontend
- Media files: S3-compatible storage via `django-storages`
- Database: PostgreSQL connection pool via `dj-database-url`

---

## Key Technical Decisions

1. **UUID primary keys** — Prevents ID enumeration attacks and is cloud-friendly.
2. **OneToOne for DriverProfile/Identity/Vehicle** — Each driver has exactly one profile; enforces data integrity at DB level.
3. **SELECT FOR UPDATE for reference generation** — Guarantees uniqueness without application-level locks.
4. **MIME detection from file bytes** — Prevents extension-spoofing attacks.
5. **Separate document serve endpoint** — Keeps files outside public URL space; enforces per-request authorization.
6. **State machine as a service class** — Centralises all transition logic; prevents scattered status changes.
7. **Pluggable OTP provider** — Development uses console; production swaps to SMS via env var with no code changes.
8. **React Hook Form + Zod** — Schema-driven validation reused between frontend form fields and TypeScript types.
9. **Zustand over Redux** — Simpler API for the moderate state complexity of this application.
10. **drf-spectacular** — Auto-generates OpenAPI 3.0 schema from DRF views; no manual schema maintenance.
