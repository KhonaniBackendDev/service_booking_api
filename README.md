# Service Booking API

A professional backend API built with FastAPI for managing service bookings, authentication, and Stripe payments.

This project allows service owners to create and manage services while clients can browse services, create bookings, and securely complete payments through Stripe Checkout.

---

# Features

* User authentication with JWT
* Password hashing and verification
* Role-based access control
* Service management system
* Booking system
* Stripe Checkout integration
* Stripe webhook handling
* PostgreSQL database integration
* SQLAlchemy ORM
* Alembic database migrations
* Protected routes using OAuth2
* Login security with failed-attempt lockout
* Environment variable configuration
* RESTful API architecture

---

# Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Stripe API
* JWT Authentication
* Pydantic
* Uvicorn

---

# User Roles

## Owner

Owners can:

* Create services
* Update services
* Delete services

## Client

Clients can:

* View services
* Create bookings
* Pay for bookings using Stripe

---

# Authentication

Authentication is handled using JWT access tokens.

Passwords are securely hashed before storage and verified during login.

Protected endpoints use OAuth2 and bearer token authentication.

---

# Stripe Payment Flow

1. Client creates a booking
2. Backend creates a Stripe Checkout Session
3. Client completes payment through Stripe Checkout
4. Stripe sends a webhook event
5. Backend verifies the webhook signature
6. Booking payment status is updated to `paid`

---

# Project Structure

```bash
app/
│
├── routers/
├── models.py
├── schemas.py
├── database.py
├── oauth2.py
├── utils.py
├── config.py
├── main.py
│
alembic/
```

---

# Environment Variables

Create a `.env` file and configure:

```env
database_hostname=
database_port=
database_password=
database_name=
database_username=

secret_key=
algorithm=
access_token_expire_minutes=

stripe_secret_key=
stripe_webhook_secret=
```

---

# Installation

Clone the repository:

```
git clone <https://github.com/KhonaniBackendDev/service_booking_api.git>
```

Install dependencies:

```
pip install -r requirements.txt
```

Run database migrations:

```
alembic upgrade head
```

Start the server:

```
uvicorn app.main:app --reload
```

---

# API Documentation

FastAPI automatically generates interactive API documentation.

Swagger UI:

```
http://127.0.0.1:8000/docs
```

ReDoc:

```
http://127.0.0.1:8000/redoc
```

---

# Future Improvements

* Docker support
* Email notifications
* Admin dashboard
* Pagination and filtering
* Booking history
* Service categories
* Production deployment
* CI/CD pipeline
* Refresh tokens

---

# Author

Developed as a portfolio backend project focused on real-world API architecture, authentication, database design, and payment integration.
