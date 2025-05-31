#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Backend Deployment
echo "Setting up backend..."
cd /home/steve/PARAMOUNT/PARAMOUNT_BANK_LOG_SYSTEM
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
redis-server &
daphne -b 0.0.0.0 -p 8000 PARAMOUNT.asgi:application &

# Prompt user for environment variables
read -p "Enter EMAIL_HOST: " EMAIL_HOST
read -p "Enter EMAIL_HOST_USER: " EMAIL_HOST_USER
read -p "Enter EMAIL_HOST_PASSWORD: " EMAIL_HOST_PASSWORD
read -p "Enter STAFF_EMAIL_DOMAIN: " STAFF_EMAIL_DOMAIN
read -p "Enter IT_SUPPORT_EMAIL: " IT_SUPPORT_EMAIL
read -p "Enter WEBSITE_LINK: " WEBSITE_LINK

# Export environment variables
export EMAIL_HOST
export EMAIL_HOST_USER
export EMAIL_HOST_PASSWORD
export STAFF_EMAIL_DOMAIN
export IT_SUPPORT_EMAIL
export WEBSITE_LINK

# Prompt user for API_BASE_URL
read -p "Enter API_BASE_URL: " API_BASE_URL

# Export API_BASE_URL
export API_BASE_URL

# Add API_BASE_URL to .env file in paramount-it-log-system
echo "VITE_API_BASE_URL=$API_BASE_URL" > /home/steve/PARAMOUNT/PARAMOUNT_BANK_LOG_SYSTEM/paramount-it-log-system/.env

# Ensure sensitive environment variables are not echoed or logged
set +x

# Validate environment variables before exporting
if [[ -z "$EMAIL_HOST" || -z "$EMAIL_HOST_USER" || -z "$EMAIL_HOST_PASSWORD" || -z "$STAFF_EMAIL_DOMAIN" || -z "$IT_SUPPORT_EMAIL" || -z "$WEBSITE_LINK" || -z "$API_BASE_URL" ]]; then
  echo "Error: Missing required environment variables." >&2
  exit 1
fi

# Secure permissions for .env file
chmod 600 /home/steve/PARAMOUNT/PARAMOUNT_BANK_LOG_SYSTEM/paramount-it-log-system/.env

# Frontend Deployment
echo "Setting up frontend..."
cd /home/steve/PARAMOUNT/PARAMOUNT_BANK_LOG_SYSTEM/paramount-it-log-system

# Ensure npm install and build commands are run with non-root user
if [[ "$EUID" -eq 0 ]]; then
  echo "Error: Do not run npm commands as root." >&2
  exit 1
fi

npm install
npm run build
npx serve -s dist -l 8080 &

# Print success message
echo "Deployment completed successfully!"
