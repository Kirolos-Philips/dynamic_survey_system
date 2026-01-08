from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Load environment variables from the .envs/.local/ directory
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".django"))
environ.Env.read_env(str(BASE_DIR / ".envs" / ".local" / ".postgres"))

from .base import *  # noqa
from .base import env  # noqa: E402

DEBUG = True

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-6j!&txba*c+rj82_cbj+-du5^68)_xrl*&v-w048$s8vf$h#lp",
)

ALLOWED_HOSTS = ["localhost", "0.0.0.0", "127.0.0.1"]
