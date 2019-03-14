from .default import *  # noqa

# use postgresql so we test database transactions correctly
DATABASES["default"] = {
    "ENGINE": "django.db.backends.postgresql_psycopg2",
    "HOST": "localhost",
    "NAME": "oscar_docdata_sandbox",
    "USER": "postgres",
    "PASSWORD": "",
}
