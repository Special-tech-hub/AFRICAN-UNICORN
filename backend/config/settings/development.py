"""Development settings for TakeOFF Driver Onboarding Platform."""
from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# Use SQLite for local dev if DATABASE_URL not set
# (base.py reads DATABASE_URL from env, falls back to sqlite)

# Show OTP in console logs during development
OTP_PROVIDER = 'console'

# Disable rate limiting in tests
RATELIMIT_ENABLE = False

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
