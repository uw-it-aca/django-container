import os
from .common import INSTALLED_APPS, MIDDLEWARE, DATABASES


INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE = ['django_prometheus.middleware.PrometheusBeforeMiddleware'] + \
    MIDDLEWARE + \
    ['django_prometheus.middleware.PrometheusAfterMiddleware']

if os.getenv('DB', 'sqlite3') == 'sqlite3':
    DATABASES['default']['ENGINE'] = 'django_prometheus.db.backends.sqlite3'
elif os.getenv('DB', 'sqlite3') == 'mysql':
    DATABASES['default']['ENGINE'] = 'django_prometheus.db.backends.mysql'
elif os.getenv('DB', 'sqlite3') == 'postgres':
    DATABASES['default']['ENGINE'] = 'django_prometheus.db.backends.postgresql'
