"""
Python SECRET_KEY generator.
"""

from pathlib import Path
import random

chars = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!?@#$%^&*()"
size = 50
secret_key = "".join(random.choices(chars, k=size))

password_file = Path(__file__).resolve().parent / "veralign" / "password"
try:
    with open(password_file, "r") as f:
        password = f.read().rstrip()
except (FileNotFoundError, PermissionError, OSError) as e:
    raise RuntimeError(f"Could not read password file '{password_file}': {e}")

CONFIG_STRING = (
    """
DEBUG=True
SECRET_KEY=%s
ALLOWED_HOSTS=127.0.0.1,.localhost,0.0.0.0

DATABASE_URL=postgres://veralignadmin:%s@localhost:5432/veraligndb
POSTGRES_DB=veraligndb
POSTGRES_USER=veralignadmin
POSTGRES_PASSWORD=%s
DB_HOST=localhost

# DEFAULT_FROM_EMAIL=
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = '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'
EMAIL_CONNECTION_CLASS = 'django.core.mail.backends.smtp.EmailBackend'
""".strip()
    % (secret_key, password, password)
)

# Writing our configuration file to '.env'
with open(Path(__file__).resolve().parent / "veralign" / ".env", "w") as configfile:
    configfile.write(CONFIG_STRING)

print("Success!")
print("Type: cat ./veralign/.env")
