from .general import *
import dj_database_url # Make sure to: pip install dj-database-url psycopg2-binary

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "send-4315.onrender.com"]

# Supabase (PostgreSQL) Configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = os.getenv("EMAIL")
EMAIL_HOST_PASSWORD = os.getenv("PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("EMAIL")