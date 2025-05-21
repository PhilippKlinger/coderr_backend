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
# Clone the repository
git clone git@github.com:PhilippKlinger/coderr_backend.git
cd coderr_backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# (Optional) Create a superuser
python manage.py createsuperuser

# (Optional) Seed database with fake data for testing
python manage.py shell < seed.py

# Start the development server
python manage.py runserver

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

### Using Seed Data

To quickly fill your database with demo data for testing, you can use the included seed.py script.
Warning: Running the seed script will DELETE ALL EXISTING DATA (including users, offers, orders, and reviews) and recreate the demo content from scratch.
If you already created a superuser, you will need to recreate it afterwards.

```bash
python manage.py shell < seed.py
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