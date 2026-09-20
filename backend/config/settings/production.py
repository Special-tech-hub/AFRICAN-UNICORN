"""Production settings for TakeOFF Driver Onboarding Platform."""
import os
from .base import *  # noqa
import environ

env = environ.Env()

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Media storage — configurable via env
MEDIA_STORAGE_PROVIDER = env('MEDIA_STORAGE_PROVIDER', default='local')

if MEDIA_STORAGE_PROVIDER == 's3':
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = env('CLOUD_STORAGE_BUCKET')
    AWS_ACCESS_KEY_ID = env('CLOUD_STORAGE_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = env('CLOUD_STORAGE_SECRET_KEY')
    AWS_S3_REGION_NAME = env('CLOUD_STORAGE_REGION', default='us-east-1')
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600  # 1 hour presigned URL expiry
