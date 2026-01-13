from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Load environment variables from the .envs/.production/ directory
environ.Env.read_env(str(BASE_DIR / ".envs" / ".production" / ".django"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".production" / ".postgres"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".production" / ".celery"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".production" / ".redis"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".production" / ".flower"))

from .base import *  # noqa
from .base import env  # noqa: E402

DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

# Security settings
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
    "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
)
