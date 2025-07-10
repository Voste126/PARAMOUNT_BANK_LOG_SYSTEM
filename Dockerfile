# Dockerfile for PARAMOUNT Django Project
#
# This Dockerfile builds a production-ready image for the Django backend.
# It installs system dependencies, Python packages, and sets up the app user and entrypoint.

# Use official Python slim image as base
FROM python:3.11-slim

# Set environment variables
# - PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# - PYTHONUNBUFFERED: Ensures output is sent straight to terminal (no buffering)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies required for building Python packages and running the app
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
 # Fix for girepository pkg-config naming
 && ln -s /usr/lib/x86_64-linux-gnu/pkgconfig/girepository-1.0.pc \
         /usr/lib/x86_64-linux-gnu/pkgconfig/girepository-2.0.pc \
 # Clean up apt cache to reduce image size
 && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies file
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip \
 && python -m pip install -r requirements.txt

# Copy project files into the container
COPY . .

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos "" appuser \
 && chown -R appuser /app
USER appuser

# Expose port 8000 for the Django app
EXPOSE 8000

# Run migrations and start Gunicorn server
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 PARAMOUNT.wsgi"]
