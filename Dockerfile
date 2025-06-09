FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      python3-dev \
      python3-gi \
      pkg-config \
      libcairo2-dev \
      libdbus-1-dev \
      libdbus-glib-1-dev \
      gettext \
      meson \
      ninja-build \
      gobject-introspection \
      libgirepository1.0-dev \
      libglib2.0-dev \
      libffi-dev \
 && ln -s /usr/lib/x86_64-linux-gnu/pkgconfig/girepository-1.0.pc \
         /usr/lib/x86_64-linux-gnu/pkgconfig/girepository-2.0.pc \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip \
 && python -m pip install -r requirements.txt

COPY . .
RUN adduser --disabled-password --gecos "" appuser \
 && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 PARAMOUNT.wsgi"]
