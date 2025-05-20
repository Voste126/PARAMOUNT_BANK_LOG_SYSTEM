# PARAMOUNT_BANK_LOG_SYSTEM

A Django-based system for Paramount Bank staff to log IT issues, track their status, and receive real-time feedback via email and WebSocket notifications. The system supports OTP-based authentication for staff and provides a RESTful API for integration with frontend dashboards.

---

## Features

- **Staff Registration & OTP Authentication**: Staff register with their corporate email and verify via OTP sent to their email. Login is also OTP-based.
- **IT Issue Logging**: Staff can log IT issues, attach files, and specify priority, category, and method of logging.
- **Real-Time Notifications**: Both staff and IT support receive email notifications and real-time WebSocket updates when issues are logged or resolved.
- **RESTful API**: All operations are exposed via a documented REST API (Swagger/Redoc available).
- **Admin Dashboard**: Django admin for managing staff and issues.
- **Prometheus Metrics**: Integrated for monitoring.

---

## Requirements

- Python 3.10+
- Django 5.1+
- Redis (for Channels/WebSocket support)
- See `requirements.txt` for all Python dependencies

---

## Installation & Setup

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd PARAMOUNT_BANK_LOG_SYSTEM
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env` and set your SMTP credentials, Redis host, etc.

   Example variables:

   ```env
   EMAIL_HOST=smtp.yourprovider.com
   EMAIL_HOST_USER=youruser
   EMAIL_HOST_PASSWORD=yourpassword
   STAFF_EMAIL_DOMAIN=@paramount.co.ke
   IT_SUPPORT_EMAIL=it-support@paramount.co.ke
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (for admin access)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run Redis server**

   ```bash
   redis-server
   ```

8. **Run the Django development server (with Channels)**

   ```bash
   daphne PARAMOUNT.asgi:application
   # or for development:
   python manage.py runserver
   ```

---

## API Endpoints

### Staff Authentication

- `POST /api/staff/register/` — Register staff (email, first_name, last_name)
- `POST /api/staff/verify-otp/` — Verify OTP (email, otp)
- `POST /api/staff/login/request/` — Request login OTP (email)
- `POST /api/staff/login/verify/` — Verify login OTP and get JWT

### IT Issue Reporting

- `GET /api/reportlog/issues/` — List all issues for the logged-in staff
- `POST /api/reportlog/issues/` — Log a new IT issue
- `GET /api/reportlog/issues/<id>/` — Retrieve a specific issue
- `PUT/PATCH /api/reportlog/issues/<id>/` — Update/resolve an issue
- `DELETE /api/reportlog/issues/<id>/` — Delete an issue

### API Documentation

- Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- Redoc: [http://localhost:8000/](http://localhost:8000/)

---

## Real-Time Notifications

- **WebSocket URL**: `ws://localhost:8000/ws/notifications/`
- Connect with any WebSocket client to receive real-time updates when issues are logged or resolved.

---

## Testing

- Run all tests:

  ```bash
  python manage.py test
  ```

- For WebSocket/manual testing, use a WebSocket client to connect to `ws://localhost:8000/ws/notifications/` and observe real-time events.

---

## Project Structure

- `Staff/` — Staff registration, authentication, and models
- `ReportLog/` — IT issue models, serializers, views, and URLs
- `Dashboard/` — WebSocket consumers and routing
- `PARAMOUNT/` — Project settings, URLs, ASGI/WSGI config

---

## Notes

- Make sure Redis is running for WebSocket support.
- Email settings must be configured for OTP and notifications.
- Only emails ending with the configured domain (default: `@paramount.co.ke`) can register.
- For production, set `DEBUG = False` and configure allowed hosts and secure credentials.

---

## License

See [LICENSE](LICENSE).
