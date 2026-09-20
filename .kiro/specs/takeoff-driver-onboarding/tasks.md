# Tasks

## Task 1: Project Scaffolding and Configuration
Set up the complete project directory structure, Python virtual environment dependencies, Django project configuration, React/Vite frontend scaffold, environment variable templates, Docker files, and `.gitignore`.

- [x] 1.1 Create the top-level directory structure: `backend/`, `frontend/`, `docs/`, with placeholder `README.md`, `.env.example`, `.gitignore`, `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`.
- [x] 1.2 Initialise the Django project inside `backend/` with a `config/` package containing `settings/base.py`, `settings/development.py`, `settings/production.py`, `urls.py`, `wsgi.py`, `asgi.py`. Create `backend/manage.py` pointing at `config.settings.development` for `DJANGO_SETTINGS_MODULE`.
- [x] 1.3 Create `backend/requirements.txt` pinned with: Django==4.2.*, djangorestframework, djangorestframework-simplejwt, psycopg2-binary, django-environ, django-cors-headers, django-ratelimit, drf-spectacular, python-magic, Pillow, celery, redis, django-storages, boto3, factory-boy, pytest-django, coverage. Create `backend/requirements-dev.txt` with pytest, pytest-django, factory-boy, coverage, black, isort, flake8.
- [ ] 1.4 Create `backend/apps/` with empty `__init__.py` and stub Django apps: `accounts`, `onboarding`, `documents`, `applications`, `reviews`, `notifications`, each with `__init__.py`, `models.py`, `serializers.py`, `views.py`, `urls.py`, `admin.py`, `apps.py`, `tests/` directory.
- [ ] 1.5 Create `backend/core/` with `__init__.py`, `permissions.py`, `pagination.py`, `exceptions.py`, `mixins.py`.
- [ ] 1.6 Configure `backend/config/settings/base.py` with: INSTALLED_APPS (all six apps, rest_framework, simplejwt, corsheaders, drf_spectacular, django_ratelimit), DATABASES (dj-database-url from env), AUTH_USER_MODEL='accounts.User', REST_FRAMEWORK defaults (JWT auth, pagination), SIMPLE_JWT config (15 min access, 7 day refresh, rotate refresh tokens, blacklist), SPECTACULAR_SETTINGS, MEDIA_ROOT, MEDIA_URL, DEFAULT_FILE_STORAGE from env.
- [ ] 1.7 Scaffold the React + Vite + TypeScript + Tailwind CSS frontend inside `frontend/` using `npm create vite@latest . -- --template react-ts`. Install: axios, react-router-dom, zustand, react-hook-form, zod, @hookform/resolvers. Configure Tailwind. Create `src/` with subdirectories: `api/`, `components/`, `pages/`, `hooks/`, `store/`, `types/`, `utils/`.
- [ ] 1.8 Create `.env.example` with all required variables: DEBUG, SECRET_KEY, DATABASE_URL, JWT_SECRET_KEY, OTP_PROVIDER, SMS_PROVIDER, SMS_API_KEY, MEDIA_STORAGE_PROVIDER, CLOUD_STORAGE_BUCKET, CLOUD_STORAGE_ACCESS_KEY, CLOUD_STORAGE_SECRET_KEY, CORS_ALLOWED_ORIGINS, REDIS_URL, ALLOWED_HOSTS.
- [ ] 1.9 Create `docker-compose.yml` defining services: `backend` (Dockerfile.backend, env_file .env, depends_on postgres + redis), `frontend` (Dockerfile.frontend), `postgres` (postgres:15 image, volume), `redis` (redis:7 image). Create `Dockerfile.backend` (python:3.12-slim, install deps, gunicorn entrypoint) and `Dockerfile.frontend` (node:20-slim build + nginx serve).
- [ ] 1.10 Create a `backend/pytest.ini` (or `setup.cfg`) configuring pytest-django with `DJANGO_SETTINGS_MODULE=config.settings.development` and `python_files=tests/test_*.py`.

## Task 2: Database Models and Migrations
Implement all Django ORM models, run initial migrations, and configure Django Admin registrations.

_Depends on: Task 1_

- [ ] 2.1 Implement `accounts/models.py`: Custom `User` model extending `AbstractBaseUser` + `PermissionsMixin` with fields: `id` (UUIDField PK), `phone_number` (unique), `email` (nullable), `password` (hashed), `role` (CharField choices DRIVER/ADMIN), `is_phone_verified` (BooleanField default False), `is_active`, `is_staff`, `created_at`, `updated_at`. Implement `UserManager` with `create_user` and `create_superuser`. Set `USERNAME_FIELD = 'phone_number'`. Implement `OTPVerification` model with fields: `id` (UUID PK), `user` (FK User), `otp_hash`, `expires_at`, `attempt_count` (default 0), `is_active` (default True), `verified_at` (nullable), `created_at`. Add composite index on `(user, is_active)`.
- [~] 2.2 Implement `onboarding/models.py`: `DriverProfile` (OneToOne to User, personal + contact fields as per design doc), `IdentityVerification` (OneToOne to User, id_type choices, licence fields, `is_license_expired` BooleanField), `Vehicle` (OneToOne to User, vehicle_type choices, make/model/year/registration/colour). Override `save()` on `IdentityVerification` to auto-set `is_license_expired` based on `license_expiry_date`.
- [~] 2.3 Implement `documents/models.py`: `Document` model with all fields from design doc. Add index on `(driver, document_type)`.
- [~] 2.4 Implement `applications/models.py`: `DriverApplication` (OneToOne to User as driver, application_reference unique, status choices, all timestamp + reviewer fields), `ApplicationStatusHistory` (FK to DriverApplication, previous/new status, changed_by FK User, note, created_at). Add index on `(status)`, `(application, created_at)`. Implement `ApplicationSequence` model (year unique, last_sequence integer) for atomic reference generation.
- [~] 2.5 Implement `notifications/models.py`: `Notification` model with all fields from design doc. Add index on `(user, is_read)` and `(user, created_at)`.
- [~] 2.6 Run `python manage.py makemigrations` for all apps and verify the generated migration files are correct and complete. Run `python manage.py migrate` against a local PostgreSQL instance to confirm migrations apply without errors.
- [~] 2.7 Register all models in their respective `admin.py` files with appropriate `list_display`, `list_filter`, `search_fields`, and `ordering`. Register: User (list: phone, role, is_phone_verified, created_at; filter: role, is_phone_verified), DriverApplication (list: application_reference, driver phone, status, submitted_at; filter: status), Document (list: driver, document_type, uploaded_at; filter: document_type), Notification (list: user, notification_type, is_read; filter: is_read).

## Task 3: Authentication Backend — Registration, OTP, Login
Implement the complete authentication API: user registration, OTP service with pluggable providers, OTP verification, login, token refresh, and logout.

_Depends on: Task 2_

- [~] 3.1 Implement `core/permissions.py`: `IsDriverUser` (checks `request.user.role == 'DRIVER'`), `IsAdminUser` (checks `request.user.role == 'ADMIN'`), `IsPhoneVerified` (checks `request.user.is_phone_verified`), `IsOwnerOrAdmin` (checks object owner == request.user or user is ADMIN).
- [~] 3.2 Implement `accounts/otp_providers.py`: `BaseOTPProvider` abstract class with `send(phone_number, otp)` method. `ConsoleOTPProvider` that logs OTP to Django logger at INFO level (only when OTP_PROVIDER=console). `TwilioOTPProvider` stub that reads `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` from settings and calls Twilio API. `get_otp_provider()` factory function that reads `settings.OTP_PROVIDER` and returns the appropriate provider instance; raises `ValueError` for unknown providers.
- [~] 3.3 Implement `accounts/services.py` — `OTPService` class: `generate_and_send(user)` method (check resend cooldown 60s on latest active OTP, invalidate previous active OTPs, generate 6-digit OTP via `secrets.randbelow(10**6)`, zero-pad, hash with `hashlib.pbkdf2_hmac('sha256', otp.encode(), salt, 260000)`, store `OTPVerification`, dispatch via provider, create Notification). `verify(phone_number, submitted_otp)` method (find active non-expired record, increment attempt_count atomically, compare hashes using `hmac.compare_digest`, handle expired/exceeded cases, mark verified, return User). All methods should raise typed exceptions (`OTPExpiredError`, `OTPMaxAttemptsError`, `OTPCooldownError`, `OTPInvalidError`).
- [~] 3.4 Implement `accounts/serializers.py`: `RegisterSerializer` (phone_number, password, confirm_password — validate uniqueness, password match, min length 8, phone format via regex), `OTPVerifySerializer` (phone_number, otp), `OTPResendSerializer` (phone_number), `LoginSerializer` (phone_number, password — authenticate and check is_phone_verified), `LogoutSerializer` (refresh token field).
- [~] 3.5 Implement `accounts/views.py`: `RegisterView` (POST, calls `OTPService.generate_and_send`, returns 201), `OTPVerifyView` (POST, calls `OTPService.verify`, returns JWT pair on success), `OTPResendView` (POST with rate limiting via `django-ratelimit` 5/10min per phone, calls `OTPService.generate_and_send`), `LoginView` (POST, returns JWT pair), `TokenRefreshView` (delegates to SimpleJWT), `LogoutView` (POST, blacklists refresh token, requires JWT auth).
- [~] 3.6 Configure `accounts/urls.py` with all auth routes and wire into `config/urls.py` at `api/auth/`.
- [~] 3.7 Implement `accounts/tests/test_auth.py`: test registration success, duplicate phone 400, password mismatch 400, weak password 400, OTP verify success (tokens returned, phone marked verified), expired OTP 400, invalid OTP 400, max attempts 429, resend cooldown 429, login success, unverified phone login 403, wrong password 401, admin login success, driver cannot access admin endpoints 403.

## Task 4: Driver Onboarding API — Profile, Identity, Vehicle
Implement the driver onboarding step APIs for personal details, contact details, identity verification, and vehicle details.

_Depends on: Task 3_

- [~] 4.1 Implement `onboarding/serializers.py`: `DriverProfileSerializer` (all profile fields, validate date_of_birth is a valid date, validate email format), `IdentityVerificationSerializer` (validate id_type choices, validate licence_expiry_date is a valid date), `VehicleSerializer` (validate vehicle_type choices, validate year 1900 ≤ year ≤ current_year+1, validate registration_number non-empty).
- [~] 4.2 Implement `onboarding/views.py`: `DriverProfileView` (GET/PUT, permission: IsAuthenticated + IsDriverUser + IsPhoneVerified, get_or_create DriverProfile for request.user, on PUT create/update DRAFT application if not exists). `IdentityVerificationView` (GET/PUT, same permissions, get_or_create IdentityVerification for request.user). `VehicleView` (GET/PUT, same permissions, get_or_create Vehicle for request.user). All views use `select_related` appropriately.
- [~] 4.3 Wire `onboarding/urls.py` and register at `api/driver/` in `config/urls.py`.
- [~] 4.4 Implement `onboarding/tests/test_onboarding.py`: test profile create, profile update, identity create with expired licence sets flag, vehicle create success, vehicle year out of range 400, unauthenticated access 401, driver cannot access another driver's profile.

## Task 5: Document Upload API
Implement the secure document upload system with MIME validation, safe filename generation, authenticated file serving, and deletion controls.

_Depends on: Task 4_

- [~] 5.1 Implement `documents/validators.py`: `MIMEValidator` class that reads the first 261 bytes of the uploaded file using `python-magic` to detect MIME type and raises `ValidationError` if not in `['image/jpeg', 'image/png', 'application/pdf']`. `ExtensionValidator` class that checks the file extension matches the detected MIME type. `FileSizeValidator` class that checks file size ≤ 10 MB (10 * 1024 * 1024 bytes).
- [~] 5.2 Implement `documents/storage.py`: `document_upload_path(instance, filename)` function that generates `documents/{user_id}/{uuid4().hex}{.ext}` path. Apply to `Document.file` FileField.
- [~] 5.3 Implement `documents/serializers.py`: `DocumentUploadSerializer` (document_type required, file required — apply all three validators). `DocumentSerializer` (read-only representation with id, document_type, original_filename, file_size, mime_type, verification_status, uploaded_at, download_url computed field).
- [~] 5.4 Implement `documents/views.py`: `DocumentListCreateView` (GET lists driver's own documents; POST validates + saves document, stores original_filename from `request.FILES[...].name`). `DocumentDeleteView` (DELETE, checks document belongs to driver, checks application status is DRAFT before allowing delete, returns 403 if submitted). `DocumentServeView` (GET /{id}/download/, validates JWT, checks IsOwnerOrAdmin permission, returns `FileResponse` with appropriate Content-Type header, or redirect to S3 pre-signed URL in production).
- [~] 5.5 Wire `documents/urls.py` and register at `api/driver/documents/` in `config/urls.py`.
- [~] 5.6 Implement `documents/tests/test_documents.py`: test upload valid PDF success, upload valid JPEG success, upload invalid MIME type 400, upload oversized file 400, upload mismatched extension 400, list documents returns only own docs, delete document on DRAFT application success, delete document on SUBMITTED application 403, serve document unauthenticated 401, serve document wrong driver 403, serve document as admin success.

## Task 6: Application Submission and State Machine
Implement the DriverApplication creation, completeness validation, submission flow, state machine transitions, and application reference generation.

_Depends on: Task 5_

- [~] 6.1 Implement `applications/reference.py`: `generate_application_reference()` function using `ApplicationSequence` with `select_for_update()` inside `transaction.atomic()` to atomically increment per-year sequence and return `TO-{year}-{seq:05d}`.
- [~] 6.2 Implement `applications/state_machine.py`: `VALID_TRANSITIONS` dict. `ApplicationStateMachine` class with `transition(application, new_status, actor, note=None)` method that validates the transition, wraps the update + history creation in `transaction.atomic()`, creates `ApplicationStatusHistory`, and calls `NotificationService` after commit. Raises `InvalidTransitionError` on invalid transitions.
- [~] 6.3 Implement `applications/services.py`: `ApplicationService.validate_completeness(driver)` method that checks DriverProfile required fields, IdentityVerification required fields, Vehicle required fields, and presence of required Document types (NATIONAL_ID, DRIVERS_LICENSE, VEHICLE_REGISTRATION, INSURANCE). Returns a list of missing items. `ApplicationService.submit(application, driver)` method that calls `validate_completeness`, calls `generate_application_reference`, calls `state_machine.transition(DRAFT → SUBMITTED)`, sets `submitted_at`.
- [~] 6.4 Implement `applications/serializers.py`: `DriverApplicationSerializer` (read-only: id, application_reference, status, submitted_at, reviewed_at, review_note). `ApplicationStatusSerializer` (application_reference, status, submitted_at, status_history nested list). `ApplicationStatusHistorySerializer` (previous_status, new_status, changed_by role, note, created_at).
- [~] 6.5 Implement `applications/views.py`: `MyApplicationView` (GET, returns driver's own application or 404). `CreateApplicationView` (POST, creates DRAFT application if none exists, returns 400 if one already exists). `SubmitApplicationView` (POST /applications/{id}/submit/, permission: IsDriverUser, calls `ApplicationService.submit`, returns 200 with reference on success, 400 with missing items on failure). `ApplicationStatusView` (GET /applications/{id}/status/, returns full status + history).
- [~] 6.6 Wire `applications/urls.py` and register at `api/applications/` in `config/urls.py`.
- [~] 6.7 Implement `applications/tests/test_applications.py`: test DRAFT creation success, duplicate DRAFT creation 400, submission with all fields + docs success (reference generated, status=SUBMITTED), submission with missing profile fields returns 400 with field list, submission with missing required document 400, submit already-submitted application 400, state machine invalid transition raises error, reference uniqueness (concurrent requests produce unique references), driver cannot view another driver's application.

## Task 7: Admin Review API
Implement the admin-facing endpoints: application list with filtering/search/pagination, application detail, approve, reject, and statistics.

_Depends on: Task 6_

- [~] 7.1 Implement `core/pagination.py`: `StandardPagination` class (PageNumberPagination, page_size=20, page_size_query_param='page_size', max_page_size=100).
- [~] 7.2 Implement `reviews/serializers.py`: `AdminApplicationListSerializer` (application_reference, driver full name, phone, vehicle type/make/model, submitted_at, status, reviewer phone). `AdminApplicationDetailSerializer` (full nested data: profile, identity, vehicle, documents with download_url, status_history). `ApproveSerializer` (optional note field). `RejectSerializer` (reason field — required, `min_length=1` validation).
- [~] 7.3 Implement `reviews/views.py`: `AdminApplicationListView` (GET, permission: IsAdminUser, uses `StandardPagination`, supports `?status=`, `?search=` query params filtering on driver name/phone/reference, uses `select_related` + `prefetch_related`). `AdminApplicationDetailView` (GET, permission: IsAdminUser, returns full detail; auto-triggers SUBMITTED→UNDER_REVIEW transition via state machine if status is SUBMITTED). `ApproveApplicationView` (POST, permission: IsAdminUser, calls `state_machine.transition(UNDER_REVIEW→APPROVED)`, stores optional note). `RejectApplicationView` (POST, permission: IsAdminUser, validates reason required, calls `state_machine.transition(UNDER_REVIEW→REJECTED)`, stores reason as review_note). `AdminStatisticsView` (GET, permission: IsAdminUser, returns aggregate counts using `DriverApplication.objects.values('status').annotate(count=Count('id'))`).
- [~] 7.4 Wire `reviews/urls.py` and register at `api/admin/` in `config/urls.py`.
- [~] 7.5 Implement `reviews/tests/test_reviews.py`: test admin can list applications, status filter returns correct subset, search by name returns match, search by phone returns match, admin detail view triggers SUBMITTED→UNDER_REVIEW, approve success (status=APPROVED, history created, driver notified), approve non-UNDER_REVIEW application 400, reject with reason success (status=REJECTED, reason stored), reject without reason 400, reject non-UNDER_REVIEW application 400, statistics returns correct counts, driver cannot access admin list 403, driver cannot access approve endpoint 403.

## Task 8: Notifications System
Implement in-app notification creation, listing, and mark-as-read endpoints; integrate notification creation into all relevant event points.

_Depends on: Task 7_

- [~] 8.1 Implement `notifications/services.py`: `NotificationService` class with `create(user, notification_type, title, message)` static method that creates a `Notification` record. Define `NOTIFICATION_TEMPLATES` dict mapping event types to (title_template, message_template) tuples. Implement helper methods: `notify_otp_sent(user, phone)`, `notify_phone_verified(user)`, `notify_app_submitted(user, reference)`, `notify_app_under_review(user, reference)`, `notify_app_approved(user, reference, note)`, `notify_app_rejected(user, reference, reason)`.
- [~] 8.2 Integrate `NotificationService` calls into: `OTPService.generate_and_send` → `notify_otp_sent`, `OTPService.verify` → `notify_phone_verified`, `ApplicationService.submit` → `notify_app_submitted`, `ApplicationStateMachine.transition` for UNDER_REVIEW → `notify_app_under_review`, for APPROVED → `notify_app_approved`, for REJECTED → `notify_app_rejected`.
- [~] 8.3 Implement `notifications/serializers.py`: `NotificationSerializer` (all fields, read-only except `is_read`).
- [~] 8.4 Implement `notifications/views.py`: `NotificationListView` (GET, permission: IsAuthenticated, returns notifications for `request.user` ordered by `-created_at`). `MarkNotificationReadView` (PATCH /notifications/{id}/read/, validates notification belongs to request.user, sets `is_read=True`).
- [~] 8.5 Wire `notifications/urls.py` and register at `api/notifications/` in `config/urls.py`.
- [~] 8.6 Implement `notifications/tests/test_notifications.py`: test notification created on OTP send, on phone verify, on app submit, on under_review, on approve, on reject, driver sees own notifications only, mark read sets is_read=True, driver cannot mark another driver's notification.

## Task 9: Health Check and API Documentation
Implement the `/health/` endpoint and configure drf-spectacular for auto-generated OpenAPI documentation.

_Depends on: Task 3_

- [~] 9.1 Create `core/views.py` with `HealthCheckView` (GET, unauthenticated, checks DB connectivity via `connection.ensure_connection()`, returns `{"status": "ok"}` with 200 on success, `{"status": "degraded", "detail": "database unavailable"}` with 503 on failure).
- [~] 9.2 Register `GET /health/` in `config/urls.py` pointing to `HealthCheckView`.
- [~] 9.3 Configure `SPECTACULAR_SETTINGS` in `base.py`: TITLE='TakeOFF Driver Onboarding API', VERSION='1.0.0', SERVE_INCLUDE_SCHEMA=False. Add `SpectacularAPIView` at `/api/schema/` and `SpectacularSwaggerView` at `/api/docs/` to `config/urls.py`.
- [~] 9.4 Add `@extend_schema` decorators to all views to ensure request/response schemas, tags, and descriptions are accurate in the generated OpenAPI spec.

## Task 10: Seed Data Management Command
Create a Django management command that seeds the database with realistic fictional test data covering all application statuses.

_Depends on: Task 7_

- [~] 10.1 Create `backend/apps/accounts/management/commands/seed_data.py`. The command should be idempotent (safe to run multiple times). Create: 1 Admin user (phone: `0700000000`, password: `Admin1234!`), 5 Driver accounts with fictional Zimbabwean/African names, emails, addresses. For each driver: create DriverProfile (complete), IdentityVerification, Vehicle, and linked Documents (using small placeholder test PDF/image files generated programmatically). Create DriverApplication records in all 5 statuses: DRAFT, SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED. For APPROVED/REJECTED applications create full ApplicationStatusHistory chain. For REJECTED include a rejection reason. Print a summary table on completion.
- [~] 10.2 Create `backend/apps/accounts/management/commands/create_admin.py`: a utility command to create an admin user from command-line arguments (for production bootstrap without seed data).

## Task 11: Frontend — Authentication Pages
Build the React authentication pages: registration, OTP verification, and login, with full form validation and API integration.

_Depends on: Task 3_

- [~] 11.1 Implement `frontend/src/api/client.ts`: Axios instance with `baseURL` from `VITE_API_BASE_URL` env var. Request interceptor attaches `Authorization: Bearer {accessToken}` from Zustand store. Response interceptor handles 401 by attempting token refresh (POST /api/auth/refresh/) then retrying the original request; if refresh fails, clears auth state and redirects to `/login`.
- [~] 11.2 Implement `frontend/src/store/authStore.ts`: Zustand store with `user`, `accessToken`, `refreshToken` state. `login(tokens, user)` action, `logout()` action (clears state + calls logout API), `setTokens()` action. Persist tokens to `localStorage` with hydration on app init.
- [~] 11.3 Implement `frontend/src/api/auth.ts`: typed API functions: `register(data)`, `verifyOtp(data)`, `resendOtp(data)`, `login(data)`, `logout()`, `refreshToken(token)`.
- [~] 11.4 Build `frontend/src/pages/auth/RegisterPage.tsx`: Form with phone_number, password, confirm_password fields. Zod schema validation (phone regex, password min 8 chars, passwords match). Show loading state on submit. On success navigate to `/verify-otp` passing phone in state. Show field-level error messages. Link to `/login`.
- [~] 11.5 Build `frontend/src/pages/auth/OTPVerifyPage.tsx`: 6-digit OTP input (individual digit boxes or single input). Displays the phone number being verified. Shows countdown timer (60s) for resend cooldown. Resend button enabled after countdown. On success stores JWT tokens, navigates to `/onboarding/personal`. Show error messages for invalid/expired OTP.
- [~] 11.6 Build `frontend/src/pages/auth/LoginPage.tsx`: Form with phone_number, password. Show loading state. On success store tokens, redirect based on role (DRIVER → `/onboarding` or `/application/status`, ADMIN → `/admin/dashboard`). Link to `/register`.
- [~] 11.7 Implement `frontend/src/components/ProtectedRoute.tsx`: HOC that checks auth state; redirects to `/login` if unauthenticated. `AdminRoute.tsx`: additionally checks `user.role === 'ADMIN'`, redirects if Driver tries to access admin route.
- [~] 11.8 Wire all auth routes in `frontend/src/App.tsx` using React Router.

## Task 12: Frontend — Driver Onboarding Flow (Steps 1–4)
Build the 6-step onboarding layout with persistent progress indicator, and implement steps 1 (Personal Details), 2 (Contact Details), 3 (Identity Verification), and 4 (Vehicle Details).

_Depends on: Task 11_

- [~] 12.1 Build `frontend/src/components/onboarding/OnboardingLayout.tsx`: persistent sidebar/top-bar progress indicator showing 6 steps with ✓ (completed), ● (current), ○ (incomplete) states. Layout wraps all onboarding step pages. Derives current step from route path.
- [~] 12.2 Implement `frontend/src/store/onboardingStore.ts`: Zustand store tracking `currentStep`, `applicationId`, and form data for each step. Persist to `sessionStorage` to survive page refresh. Actions: `savePersonal(data)`, `saveContact(data)`, `saveIdentity(data)`, `saveVehicle(data)`, `setApplicationId(id)`.
- [~] 12.3 Implement `frontend/src/api/onboarding.ts`: typed API functions for `getProfile()`, `updateProfile(data)`, `getIdentity()`, `updateIdentity(data)`, `getVehicle()`, `updateVehicle(data)`. On component mount, fetch and pre-populate forms with existing data.
- [~] 12.4 Build `frontend/src/pages/onboarding/PersonalDetailsStep.tsx`: fields: first_name, middle_name (optional), last_name, date_of_birth (date picker), gender (select: Male/Female/Other/Prefer not to say), nationality. Zod validation: required fields, valid date, reasonable age (16–100). Next button calls `updateProfile`, saves to store, navigates to Contact step.
- [~] 12.5 Build `frontend/src/pages/onboarding/ContactDetailsStep.tsx`: fields: phone_number (read-only, pre-filled from auth), email, street_address, city, province, emergency_contact_name, emergency_contact_phone. Zod validation: email format, required fields. Back + Next navigation.
- [~] 12.6 Build `frontend/src/pages/onboarding/IdentityVerificationStep.tsx`: fields: id_type (select: National ID/Passport), id_number, drivers_license_number, license_expiry_date. Warn (yellow banner) if licence expiry is in the past. Back + Next navigation.
- [~] 12.7 Build `frontend/src/pages/onboarding/VehicleDetailsStep.tsx`: fields: vehicle_type (select with all 6 types), make, model, year (number input, validated 1900–current+1), registration_number, colour. Back + Next navigation.

## Task 13: Frontend — Documents Upload and Review/Submit Steps
Build step 5 (Document Uploads) and step 6 (Review & Submit), including document upload UI, file validation feedback, review summary with edit links, and submission confirmation.

_Depends on: Task 12_

- [~] 13.1 Implement `frontend/src/api/documents.ts`: `listDocuments()`, `uploadDocument(type, file)` (multipart form data), `deleteDocument(id)` functions.
- [~] 13.2 Build `frontend/src/components/DocumentUploader.tsx`: reusable component for a single document type. Shows current upload status (uploaded/pending). File input restricted to `.pdf,.jpg,.jpeg,.png`. Client-side validates size ≤ 10 MB. Shows file name and size after selection. Upload button triggers API call. Shows progress/loading state. Shows success tick or error message. Allows replacement of an existing upload.
- [~] 13.3 Build `frontend/src/pages/onboarding/DocumentUploadStep.tsx`: renders `DocumentUploader` for each required document type (National ID, Driver's Licence, Vehicle Registration, Insurance Certificate) and one optional (Vehicle Inspection Certificate). Shows which documents are required vs optional. Back + Next (to Review) disabled until all required docs are uploaded.
- [~] 13.4 Build `frontend/src/pages/onboarding/ReviewAndSubmitStep.tsx`: displays read-only summary sections: Personal Information, Contact Details, Identity, Vehicle, Documents. Each section has an "Edit" link routing back to the relevant step. Confirmation checkbox: "I confirm that the information provided is accurate and complete." Submit button enabled only when checkbox is checked. On click shows a confirmation modal: "Submit Application? You will not be able to edit your application after submission." with Cancel and Submit Application buttons.
- [~] 13.5 Build `frontend/src/pages/application/SubmissionSuccessPage.tsx`: shows Application Submitted Successfully message, application reference number (formatted as TO-YYYY-NNNNN), "Your application is now awaiting review" message, and "View Application Status" button linking to `/application/status`.
- [~] 13.6 Build `frontend/src/pages/application/ApplicationStatusPage.tsx`: fetches application status + history from API. Shows application reference, current status badge (colour-coded), submitted date. Shows timeline with check marks for completed stages. Shows reviewer note if APPROVED. Shows rejection reason prominently if REJECTED. Auto-refreshes every 30 seconds if status is SUBMITTED or UNDER_REVIEW.

## Task 14: Frontend — Admin Dashboard and Review Interface
Build the admin dashboard, application list with search/filter, and the application review page with approve/reject actions.

_Depends on: Task 13_

- [~] 14.1 Implement `frontend/src/api/admin.ts`: typed functions: `getStatistics()`, `listApplications(params)` (status, search, page, page_size), `getApplication(id)`, `approveApplication(id, note?)`, `rejectApplication(id, reason)`.
- [~] 14.2 Build `frontend/src/pages/admin/AdminDashboardPage.tsx`: stat cards showing Total, Pending Review, Approved, Rejected counts. Quick links to application list filtered by status. Recent applications table (5 rows).
- [~] 14.3 Build `frontend/src/pages/admin/ApplicationListPage.tsx`: table with columns: Application ID, Driver Name, Phone, Vehicle, Submitted Date, Status (badge), Actions (View button). Search input (debounced 300ms). Status filter dropdown. Pagination controls. Empty state message when no results.
- [~] 14.4 Build `frontend/src/pages/admin/ApplicationReviewPage.tsx`: full applicant detail view with sections: Driver Info, Identity (with expired licence warning badge), Vehicle, Documents (list with download links). Application History timeline. Action buttons: "Approve Application" (opens confirm modal with optional note field) and "Reject Application" (opens modal requiring reason text input, rejects disabled until reason non-empty). Show current status badge prominently.
- [~] 14.5 Build `frontend/src/components/admin/RejectModal.tsx` and `frontend/src/components/admin/ApproveModal.tsx`: modal dialogs with Cancel/Confirm buttons, loading states, error display.
- [~] 14.6 Wire admin routes in `App.tsx` under `AdminRoute` protection.

## Task 15: Documentation
Create all required documentation files.

_Depends on: Task 14_

- [~] 15.1 Write `README.md`: Project overview, features list, tech stack, architecture summary, prerequisites, local setup (clone, venv, .env setup, migrations, seed data, run backend, run frontend), OTP dev mode explanation, demo accounts table, test commands, Docker usage, deployment notes, security notes.
- [~] 15.2 Write `docs/ARCHITECTURE.md`: system diagram (ASCII), component breakdown, request lifecycle description, frontend architecture, state management rationale.
- [~] 15.3 Write `docs/DATABASE.md`: ER diagram (ASCII), table descriptions, relationship explanations, indexing rationale, migration strategy.
- [~] 15.4 Write `docs/API.md`: endpoint reference table (method, path, auth, description, request body, response), authentication flow diagrams, error response format.
- [~] 15.5 Write `docs/DEPLOYMENT.md`: environment variables reference table, Docker deployment steps, Render/Railway deployment steps, production checklist, static/media file handling.
- [~] 15.6 Write `docs/DECISIONS.md`: numbered list of key technical decisions with rationale: UUID PKs, OneToOne relations, SELECT FOR UPDATE for references, state machine as service, pluggable OTP provider, MIME detection from bytes, short-lived JWTs, Zustand vs Redux, drf-spectacular, django-ratelimit.

## Task 16: End-to-End Verification and Final Fixes
Run the full test suite, verify the acceptance test scenario manually, fix any failing tests or broken flows, and confirm the application starts cleanly from scratch.

_Depends on: Task 15_

- [~] 16.1 Run `pytest backend/` with `--cov=apps` and fix all failing tests. Target ≥80% coverage on accounts, applications, documents apps.
- [~] 16.2 Run `python manage.py seed_data` and verify all 5 driver accounts and 1 admin account are created successfully with correct statuses.
- [~] 16.3 Manually execute the full acceptance test scenario: register new driver → verify OTP (console log) → complete all 6 onboarding steps → upload test documents → submit application → view confirmation with reference → log in as admin → view application → approve with note → log back in as driver → verify status shows APPROVED with note.
- [~] 16.4 Run `npm run build` in `frontend/` and confirm no TypeScript or build errors.
- [~] 16.5 Verify `GET /health/` returns `{"status": "ok"}` with 200. Verify `GET /api/docs/` renders Swagger UI. Verify `GET /api/schema/` returns valid OpenAPI JSON.
- [~] 16.6 Verify Docker Compose: `docker compose up` starts all services, migrations run, application is accessible on configured ports.
- [~] 16.7 Review `.env.example` to confirm all required variables are present with placeholder values and no real secrets exist in any tracked file.
