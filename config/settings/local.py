import os
import sys
from pathlib import Path

import environ

# Debugpy for remote debugging (optional)
try:
    if "runserver" in sys.argv and os.environ.get("RUN_MAIN") == "true":
        import debugpy

        debugpy.listen(("0.0.0.0", 5679))
        print("✅ Debugger is listening on port 5679...")
except RuntimeError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Load environment variables from the .envs/.local/ directory
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".django"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".postgres"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".celery"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".redis"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".flower"))

from .base import *  # noqa
from .base import env  # noqa: E402

DEBUG = True

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-6j!&txba*c+rj82_cbj+-du5^68)_xrl*&v-w048$s8vf$h#lp",
)

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mailpit"
EMAIL_PORT = 1025
