# django-container

[![Build Status](https://github.com/uw-it-aca/django-container/workflows/Build%2C%20Test/badge.svg)](https://github.com/uw-it-aca/django-container/actions)
[![GitHub release](https://img.shields.io/github/release/uw-it-aca/django-container.svg)](https://github.com/uw-it-aca/django-container/releases)
![Python versions](https://img.shields.io/badge/python-3.12-blue.svg)
A configurable container for deploying Django applications


## Serving HTTP: gunicorn + nginx sidecar

**Breaking change:** the image no longer contains nginx or supervisor and, outside
`ENV=localdev`, no longer serves HTTP on `$PORT`. It runs only gunicorn, bound
to the unix socket `/var/run/gunicorn/gunicorn.sock`. In Kubernetes, an nginx
sidecar added by [django-production-chart](https://github.com/uw-it-aca/django-production-chart)
(`proxyServer.enabled: true`) shares that socket directory and serves the app on
`proxyServer.servicePort` (default 8080). Release this as a new major version.

Things that used to rely on the image answering on port 8000 (CI smoke tests,
`docker run -p 8000:8000`, ad-hoc compose files) need either `ENV=localdev`
(Django `runserver`, TCP on `$PORT`) or the compose setup below.

CI that needs to talk to the app (smoke tests, health checks) should do so over
the unix socket, not HTTP on a port. For example, inside the container, connect
to `/var/run/gunicorn/gunicorn.sock` with a plain `GET`. The
`uw-it-aca/actions/django-container-smoke-test` action does this when given
`unix-socket: /var/run/gunicorn/gunicorn.sock` and a path as `health-check-url`.
The image has no curl.

### Migrating an app

- **Static files and extra locations:** the app's `docker/locations.conf` is no
  longer read by the image. Move its contents to `proxyServer.locations` in the
  app's chart values. Paths outside `/static` that come from the app image
  (for example `/app/<app>/templates/...`) go in `proxyServer.appImagePaths`;
  they are mounted into nginx from the app image, not copied.
- **`/media`:** set `proxyServer.media.enabled` (with `storageSize`) for a shared
  volume mounted in both containers.
- **Readiness:** the chart's nginx answers liveness itself and proxies readiness
  to the app (`proxyServer.readinessAppPath`). `/scripts/ready.sh` now only
  reports whether the gunicorn socket exists.
- **Shutdown:** `/scripts/prestop.sh` sends SIGTERM to the gunicorn master.
- **Custom `start.sh` hooks:** `app_start.sh` still runs before gunicorn; it no
  longer needs to (and cannot) configure nginx.

### Testing with docker compose

`docker-compose.yaml` reproduces the pod: gunicorn in the app container and the
same nginx in a second container, sharing the socket volume. The app's
`/static` is mounted into nginx as an image volume, and `compose/nginx.conf`
mirrors the chart's default config.

```
APP_IMAGE=myapp:latest APP_ENV_FILE=./app.env \
APP_LOCATIONS_CONF=./docker/locations.conf docker compose up
```

The app env must not set `ENV=localdev`, which starts `runserver` instead of
gunicorn. The app is then served at http://localhost:8080 (`PROXY_PORT` to change). Keep `compose/nginx.conf` in sync with the chart's
`templates/_proxy_server.tpl`.
