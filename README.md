# Coderr Backend

This is the backend REST API for the Coderr project, built with Django and Django REST Framework.
Coderr is a service marketplace platform where customers can register, browse business offers, place orders, and leave reviews. 

## Features

- User registration and authentication (Customer & Business)
- Business profiles & customer profiles
- Offers with multiple package tiers (basic, standard, premium)
- Orders with status management
- Customer reviews for business users
- Token-based authentication
- Seed script for demo/testing data with Faker

## Tech Stack

- Python 3.12+
- Django 5.1.6
- Django REST Framework 3.15.2
- SQLite3 (default, easy to switch to PostgreSQL)
- Faker for demo/seed data

## Getting Started

### Prerequisites

- Python 3.12+ installed
- pip
- (Recommended) virtual environment

### Installation

```bash
# 1. Clone the repository  
git clone git@github.com:PhilippKlinger/coderr_backend.git
cd coderr_backend

# 2. Make a copy of the .env.template
cp .env.dev.template .env -> local development
cp .env.prod.template .env -> production server

# 3. Enter your secrets, db settings etc. Be sure to set the right port for CORS.
http://127.0.0.1:5500/ -> Live Server
http://127.0.0.1:4200/ -> Angular

# 4. Build and start all services (backend, postgres)  
docker compose --profile dev up -d --build -> local development
docker compose --profile prod up -d --build -> production server

🟢 The backend, database, will be set up automatically.  
🟢 All migrations, static/media setup, and superuser creation are handled by the entrypoint script.

```

### API Overview

## All endpoints are prefixed with /api/

- Registration: /api/registration/
- Login: /api/login/
- Profile: /api/profile/<pk>/
- Offers: /api/offers/
- Orders: /api/orders/
- Reviews: /api/reviews/

For details and parameters, see the API documentation or check the docstrings in the code.

### Using Seed Data (Docker)

> ⚠️ Warning: Running the seed script will **DELETE ALL EXISTING DATA** (users, offers, orders, reviews, …).
> Use only in development or with caution in production.

**in a running container**

Dev:
```bash
docker compose --profile dev up -d --build
docker compose --profile dev exec web sh -lc "python manage.py shell < seed.py"
```

The script uses Faker to generate demo users, business profiles, offers, orders, and reviews for Coderr.

### API Documentation (Swagger & Redoc)

This project provides an interactive API documentation using Swagger UI and Redoc.
After starting the development server, you can access the documentation at:

- http://localhost:8000/swagger/ (Swagger UI)
- http://localhost:8000/redoc/ (Redoc UI)

## With these tools, you can:
- Browse all endpoints, parameters, and data models.
- Try out requests directly in the browser (for example, login, create offers, post reviews).
- See the expected responses and possible error codes.

## Tip:
For endpoints that require authentication, log in using the /api/login/ endpoint to obtain your token.
Then, click the “Authorize” button in the Swagger UI and enter your token as:

Token <your_token_here>

This will allow you to access all protected endpoints directly from the documentation UI.

## Development Tips
```bash
**Testing**  
Run tests inside the running container:

# Tests im Container (DEV-Profile):
docker compose --profile dev exec web sh -lc "
  python -m coverage run manage.py test && coverage report
"

# Tests im Container (PROD-Profile):
docker compose --profile prod exec web-prod sh -lc "
  python -m coverage run manage.py test && coverage report
"

# Logs:
docker compose logs -f web       # dev
docker compose logs -f web-prod  # prod

**Environment variables**  
Sensitive settings are loaded from `.env` (see `.env.example` for reference).

**Admin UI**  
Access Django Admin at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) (credentials set in `.env`).
```
---