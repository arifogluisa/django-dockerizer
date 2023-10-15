from .utils import PROJECT_NAME, generate_or_retrieve_passwords

# Retrieve or generate passwords
DB_PASS, REDIS_PASS = generate_or_retrieve_passwords()

ENV_TYPES = ("dev", "prod")

DOCKERFILE_DEV = """FROM python:3.10
ENV PYTHONUNBUFFERED 1
ENV DEBUG True
COPY requirements.txt /code/requirements.txt
WORKDIR /code
RUN pip install -r requirements.txt
ADD . .
"""

DOCKERFILE_PROD = """FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV DEBUG False
ENV APP_ROOT /code

WORKDIR ${APP_ROOT}

COPY ./requirements.txt requirements.txt

RUN apt-get update && \\
  apt-get install -y \\
  locales \\
  locales-all \\
  build-essential \\
  libpcre3 \\
  libpcre3-dev \\
  curl \\
  libzbar-dev \\
  && pip install --upgrade pip \\
  && pip install --no-cache-dir -r requirements.txt \\
  && apt-get clean --dry-run

COPY ./mime.types /etc/mime.types
COPY ./uwsgi.ini /conf/uwsgi.ini
COPY ../.. /code

# Start uWSGI
CMD [ "uwsgi", "--ini", "/conf/uwsgi.ini"]
"""

UWSGI = f"""[uwsgi]
env = DJANGO_SETTINGS_MODULE={PROJECT_NAME}.settings
env = UWSGI_VIRTUALENV=/venv
env = IS_WSGI=True
env = LANG=en_US.UTF-8
workdir = /code
chdir = /code
logformat=%(ltime) "%(method) %(uri) %(proto)" status=%(status) res-time=%(msecs)ms
module = {PROJECT_NAME}.wsgi:application
enable-threads = true
master = True
pidfile = /tmp/app-master.pid
vacuum = True
max-requests = 5000
processes = 5
cheaper = 2
cheaper-initial = 5
gid = root
uid = root
http-socket = 0.0.0.0:$(HTTP_PORT)
stats = 0.0.0.0:$(STATS_PORT)
harakiri = $(TIMEOUT)
print = Your timeout is %(harakiri)
static-map = /static=%(workdir)/static
static-map = /media=%(workdir)/media
"""

MIME_TYPES = """# mime type definition extracted from nginx
# https://github.com/nginx/nginx/blob/master/conf/mime.types

text/html                             html htm shtml
text/css                              css
text/xml                              xml
image/gif                             gif
image/jpeg                            jpeg jpg
application/javascript                js
application/atom+xml                  atom
application/rss+xml                   rss

text/mathml                           mml
text/plain                            txt
text/vnd.sun.j2me.app-descriptor      jad
text/vnd.wap.wml                      wml
text/x-component                      htc

image/png                             png
image/tiff                            tif tiff
image/vnd.wap.wbmp                    wbmp
image/x-icon                          ico
image/x-jng                           jng
image/x-ms-bmp                        bmp
image/svg+xml                         svg svgz
image/webp                            webp

application/font-woff                 woff
application/java-archive              jar war ear
application/json                      json
application/mac-binhex40              hqx
application/msword                    doc
application/pdf                       pdf
application/postscript                ps eps ai
application/rtf                       rtf
application/vnd.apple.mpegurl         m3u8
application/vnd.ms-excel              xls
application/vnd.ms-fontobject         eot
application/vnd.ms-powerpoint         ppt
application/vnd.wap.wmlc              wmlc
application/vnd.google-earth.kml+xml  kml
application/vnd.google-earth.kmz      kmz
application/x-7z-compressed           7z
application/x-cocoa                   cco
application/x-java-archive-diff       jardiff
application/x-java-jnlp-file          jnlp
application/x-makeself                run
application/x-perl                    pl pm
application/x-pilot                   prc pdb
application/x-rar-compressed          rar
application/x-redhat-package-manager  rpm
application/x-sea                     sea
application/x-shockwave-flash         swf
application/x-stuffit                 sit
application/x-tcl                     tcl tk
application/x-x509-ca-cert            der pem crt
application/x-xpinstall               xpi
application/xhtml+xml                 xhtml
application/xspf+xml                  xspf
application/zip                       zip

application/octet-stream              bin exe dll
application/octet-stream              deb
application/octet-stream              dmg
application/octet-stream              iso img
application/octet-stream              msi msp msm

application/vnd.openxmlformats-officedocument.wordprocessingml.document    docx
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet          xlsx
application/vnd.openxmlformats-officedocument.presentationml.presentation  pptx

audio/midi                            mid midi kar
audio/mpeg                            mp3
audio/ogg                             ogg
audio/x-m4a                           m4a
audio/x-realaudio                     ra

video/3gpp                            3gpp 3gp
video/mp2t                            ts
video/mp4                             mp4
video/mpeg                            mpeg mpg
video/quicktime                       mov
video/webm                            webm
video/x-flv                           flv
video/x-m4v                           m4v
video/x-mng                           mng
video/x-ms-asf                        asx asf
video/x-ms-wmv                        wmv
video/x-msvideo                       avi
"""

DOCKER_COMPOSE_DEV = f"""version: '3'

services:
  postgres:
    container_name: postgres-db-{PROJECT_NAME}
    image: postgres:13.0-alpine
    ports:
      - 5432:5432
    volumes:
      - {PROJECT_NAME}_postgres-data:/var/lib/postgresql/data
    env_file: .env

  web:
    container_name: {PROJECT_NAME}
    build: .
    restart: "always"
    env_file: ./.env
    volumes:
      - ../../:/code
    ports:
      - "8000:8000"
    depends_on:
      - "postgres"
    command: bash -c " python /code/manage.py makemigrations --noinput && python /code/manage.py migrate && python /code/manage.py runserver 0.0.0.0:8000"

volumes:
  {PROJECT_NAME}_postgres-data:
"""

DOCKER_COMPOSE_WITH_CELERY_DEV = f"""version: '3'

services:
  postgres:
    container_name: postgres-db-{PROJECT_NAME}
    image: postgres:13.0-alpine
    ports:
      - 5432:5432
    volumes:
      - {PROJECT_NAME}_postgres-data:/var/lib/postgresql/data
    env_file: .env

  redis:
    container_name: redis
    image: redis:5
    restart: "on-failure"
    expose:
      - '6379'
    ports:
      - '6379:6379'
    volumes:
      - {PROJECT_NAME}_redis-data:/data

  celery: &celery
    container_name: celery
    build: .
    env_file: .env
    volumes:
      - ../..:/code
    command: bash -c "cd /code/ && celery --app={PROJECT_NAME}.celery:app worker -B --loglevel=INFO"
    depends_on:
      - web
      - redis
    links:
      - postgres
      - redis

  web:
    container_name: {PROJECT_NAME}
    build: .
    restart: "always"
    env_file: ./.env
    volumes:
      - ../../:/code
    ports:
      - "8000:8000"
    depends_on:
      - "postgres"
    command: bash -c " python /code/manage.py makemigrations --noinput && python /code/manage.py migrate && python /code/manage.py runserver 0.0.0.0:8000"

volumes:
  {PROJECT_NAME}_redis-data:
  {PROJECT_NAME}_postgres-data:
"""

DOCKER_COMPOSE_PROD = """version: '3'

services:

  nginx-proxy:
    image: jwilder/nginx-proxy
    container_name: nginx-proxy
    restart: "always"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - ../nginx.conf:/etc/nginx/nginx.conf
      - ../../static:/app/static
      - ../../media:/app/media
    depends_on:
      - "app"

  app:
    container_name: app
    build: .
    restart: "always"
    env_file: .env
    environment:
      - VIRTUAL_HOST=66.666.666.666 # this is example, replace this with your server IP
      - VIRTUAL_PORT=8000
      - HTTP_PORT=8000
      - STATS_PORT=8001
    volumes:
      - ../..:/code
    ports:
      - "8015:8000"
    links:
      - postgres
    depends_on:
      - "postgres"

  postgres:
    container_name: postgres-db
    image: postgres:13
    ports:
      - "5432:5432"
    volumes:
      - ./pgdb:/var/lib/postgresql/data
    env_file: .env

networks:
  default:
    external:
      name: nginx-proxy
"""

DOCKER_COMPOSE_WITH_CELERY_PROD = f"""version: '3'

services:

  nginx-proxy:
    image: jwilder/nginx-proxy
    container_name: nginx-proxy
    restart: "always"
    ports:
      - "80:80"
    volumes:
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - ../nginx.conf:/etc/nginx/nginx.conf
      - ../../static:/app/static
      - ../../media:/app/media
    depends_on:
      - "app"

  app:
    container_name: app
    build: .
    restart: "always"
    env_file: .env
    environment:
      - VIRTUAL_HOST=66.666.666.666 # this is example, replace this with your server IP
      - VIRTUAL_PORT=8000
      - HTTP_PORT=8000
      - STATS_PORT=8001
    volumes:
      - ../..:/code
    ports:
      - "8015:8000"
    links:
      - postgres
    depends_on:
      - "postgres"

  postgres:
    container_name: postgres-db
    image: postgres:13
    ports:
      - "5432:5432"
    volumes:
      - ./pgdb:/var/lib/postgresql/data
    env_file: .env

  redis:
    build:
      context: .
      dockerfile: redis.dockerfile
    image: redis:4.0.11
    restart: "on-failure"
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - ./redisdb:/var/lib/redis
    env_file: .env

  celery:
    restart: "always"
    build: .
    container_name: celery
    env_file: .env
    command: celery --app={PROJECT_NAME}.celery:app worker -B --loglevel=INFO
    volumes:
      - ../..:/code
    links:
      - redis
      - postgres
    depends_on:
      - "redis"
      - "postgres"

networks:
  default:
    external:
      name: nginx-proxy
"""

REDIS_DOCKERFILE = """FROM redis:4.0.11

CMD ["sh", "-c", "exec redis-server --requirepass \"$REDIS_PASSWORD\""]
"""

NGINX_CONF = """user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;
events {
    worker_connections 1024;
}
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for"';
    access_log /var/log/nginx/access.log main;
    sendfile on;
    keepalive_timeout 65;
    include /etc/nginx/conf.d/*.conf;
    # aditional
    client_max_body_size 200M;
}
"""

DEV_ENV = f"""# PostgreSQL
POSTGRES_DB={PROJECT_NAME}_db
POSTGRES_USER={PROJECT_NAME}_user
POSTGRES_PASSWORD={DB_PASS}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
LC_ALL=C.UTF-8

DEBUG=True
"""

DEV_ENV_WITH_CELERY = f"""# PostgreSQL
POSTGRES_DB={PROJECT_NAME}_db
POSTGRES_USER={PROJECT_NAME}_user
POSTGRES_PASSWORD={DB_PASS}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
LC_ALL=C.UTF-8

DEBUG=True

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD={REDIS_PASS}

CELERY_BROKER=redis://redis:6379/0
CELERY_BACKEND=redis://redis:6379/0
"""

PROD_ENV = f"""# PostgreSQL
POSTGRES_DB={PROJECT_NAME}_db
POSTGRES_USER={PROJECT_NAME}_user
POSTGRES_PASSWORD={DB_PASS}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
LC_ALL=C.UTF-8

DEBUG=False
"""

PROD_ENV_WITH_CELERY = f"""# PostgreSQL
POSTGRES_DB={PROJECT_NAME}_db
POSTGRES_USER={PROJECT_NAME}_user
POSTGRES_PASSWORD={DB_PASS}
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
LC_ALL=C.UTF-8

DEBUG=False

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD={REDIS_PASS}

CELERY_BROKER=redis://:{REDIS_PASS}@redis:6379/0
CELERY_BROKER_URL=redis://:{REDIS_PASS}@redis:6379/0
CELERY_BACKEND=redis://:{REDIS_PASS}@redis:6379/0
"""

CELERY = f"""from __future__ import absolute_import, unicode_literals

import logging
import os

from django.conf import settings
from celery import Celery

logger = logging.getLogger("Celery")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{PROJECT_NAME}.settings")

app = Celery("{PROJECT_NAME}")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print("Request: {{self.request}}")

if settings.DEBUG:
    app.conf.update(
        BROKER_URL='redis://localhost:6379/0',
        CELERYBEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
        CELERY_RESULT_BACKEND='redis://localhost:6379/1',
        CELERY_DISABLE_RATE_LIMITS=True,
        CELERY_ACCEPT_CONTENT=['json', ],
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        # CELERY_TIMEZONE='Asia/Baku',
    )
else:
    app.conf.update(
        BROKER_URL='redis://:{REDIS_PASS}@redis:6379/0',
        CELERYBEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler',
        CELERY_RESULT_BACKEND='redis://:{REDIS_PASS}@redis:6379/1',
        CELERY_DISABLE_RATE_LIMITS=True,
        CELERY_ACCEPT_CONTENT=['json', ],
        CELERY_TASK_SERIALIZER='json',
        CELERY_RESULT_SERIALIZER='json',
        # CELERY_TIMEZONE='Asia/Baku',
    )
"""

SINGLE_FILES = (
    ("uwsgi.ini", UWSGI),
    ("mime.types", MIME_TYPES),
)
