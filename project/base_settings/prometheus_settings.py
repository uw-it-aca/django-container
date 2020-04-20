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

if os.getenv('CACHE', '') == 'filebased':
    CACHES['default']['ENGINE'] = 'django_prometheus.cache.backends.filebased.FileBasedCache'
elif os.getenv('CACHE', '') == 'memcached':
    CACHES['default']['ENGINE'] = 'django_prometheus.cache.backends.memcached.MemcachedCache'
elif os.getenv('CACHE', '') == 'redis':
    CACHES['default']['ENGINE'] = 'django_prometheus.cache.backends.memcached.RedisCache'
elif os.getenv('CACHE', '') == 'locmem':
    CACHES['default']['ENGINE'] = 'django_prometheus.cache.backends.memcached.LocMemCache'
