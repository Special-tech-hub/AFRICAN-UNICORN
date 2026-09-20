# Technical Decisions

1. **UUID Primary Keys** — Prevents ID enumeration attacks and is cloud-storage friendly. All models use `UUIDField(primary_key=True, default=uuid.uuid4)`.

2. **Phone Number as Username** — Drivers register with phone numbers, not email. `USERNAME_FIELD = 'phone_number'` on the custom User model.

3. **PBKDF2 OTP Hashing** — OTPs are hashed with `hashlib.pbkdf2_hmac('sha256', otp, salt, 260000)` + a per-record random salt. Plaintext OTPs are never persisted.

4. **Pluggable OTP Provider** — `OTP_PROVIDER=console` logs the OTP for dev; `OTP_PROVIDER=twilio` sends SMS. No code changes required — just an env var.

5. **OneToOne for Profile/Identity/Vehicle** — Each driver has exactly one profile, one identity record, and one vehicle. Enforced at DB level with `OneToOneField`.

6. **SELECT FOR UPDATE for Reference Generation** — `ApplicationSequence.objects.select_for_update().get_or_create(year=year)` inside `transaction.atomic()` guarantees unique TO-YYYY-NNNNN references under concurrent requests.

7. **State Machine as a Service Class** — All status transition logic lives in `ApplicationStateMachine.transition()`. Views never set `application.status` directly. This prevents scattered, inconsistent transitions.

8. **MIME Detection from File Bytes** — `python-magic` reads the first 261 bytes of every uploaded file to detect the real MIME type, preventing extension-spoofing attacks (e.g. a `.pdf` that is actually an executable).

9. **Short-Lived JWTs** — 15-minute access tokens reduce the window of exposure if a token is intercepted. The 7-day refresh token is rotated and blacklisted on use.

10. **Zustand over Redux** — The application has moderate state complexity. Zustand requires far less boilerplate than Redux and integrates cleanly with `localStorage`/`sessionStorage` via the `persist` middleware.

11. **drf-spectacular** — Auto-generates OpenAPI 3.0 schema directly from DRF views and serializers. No manual schema maintenance required.

12. **SQLite for Development** — Zero-configuration local setup. `DATABASE_URL` in `.env` switches to PostgreSQL for production with no code changes.

13. **Separate Document Serve Endpoint** — Documents are stored outside the web root. `DocumentServeView` validates JWT and ownership before streaming the file, preventing direct URL access.

14. **Notifications as DB Records** — In-app notifications are stored in the `Notification` table for simplicity. The `NotificationService` abstraction makes it straightforward to add email/SMS delivery later.
