Inventory Management System APIAn enterprise-ready RESTful API built with Django and Django REST Framework (DRF). This system provides a robust backend for managing product inventory, categories, user roles, and detailed audit logging.

# Table of Contents
Architecture
Key Features
Authentication & Security
Tech Stack
Setup & Installation
API Documentation
Technical Decisions
Deployment

# Architecture
The project follows a decoupled, monolithic architecture with a clear separation between data models, business logic (serializers), and access control (permissions).

## Models: 
    Normalized database schema using SQLite (development) or PostgreSQL (production).Serializers: Handles complex data validation and automated log generation.
## Permissions: 
    Custom Role-Based Access Control (RBAC) governing three tiers of users.
## Audit Logging: 
    Automated tracking of stock changes and administrative user actions.

# Key Features
## Inventory Management: 
    Full CRUD operations on inventory items with SKU tracking and low-stock thresholds.
## Categorization: 
    Hierarchical organization of items with "get-or-create" logic during item creation.
## Role-Based Access Control (RBAC):
* Manager: 
    Full administrative control.
* Staff: 
    View and update stock quantities only.
* User:
     Read-only access.

# Audit Trail: 
    Every stock modification and administrative change is logged with a user timestamp.
# Password Recovery: 
    Secure password reset flow integrated with SendGrid.

# Authentication & Security
The API utilizes JWT (JSON Web Tokens) for stateless authentication.
* Token Generation: Handled by MyTokenObtainPairView, which injects the user's role into the response payload.
* Token Refreshing: Implemented via TokenRefreshView for improved security and session longevity.
* Environment Safety: All sensitive keys (Secret Key, SendGrid API) are managed via .env files.
* CORS/CSRF: Configured to support specific frontend origins (GitHub Codespaces and Render production).

# Tech Stack
    * Component      ///    Technology
    * Framework      ///    Django 6.0+
    * API            ///    Django REST Framework
    * Auth           ///    SimpleJWT
    * Email          ///    SendGrid
    * Static Files   ///    WhiteNoise
    * Server         ///    Gunicorn

# Setup & Installation
## Prerequisites
* Python 3.10+
* Virtualenv or Pipenv

# Local Installation

## Clone the repository:
    git clone <https://github.com/AndrewStattADA/InvManSys-Backend>
    cd <InvManSys-Backend>
 
## Set up Virtual Environment: 
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate

## Install Dependencies:
    pip install -r requirements.txt

## Environment Variables:
    Create a .env file in the root directory:
    SECRET_KEY=your_secret_key
    SENDGRID_API_KEY=your_api_key
    FRONTEND_URL=http://localhost:5173

## Run Migrations & Initialize:
    python manage.py migrate
    python createsuperuser.py  # Scripted superuser creation

## Start Server:
    python manage.py runserver

# Quality Assurance & Testing
The system includes a comprehensive test suite using APITestCase to ensure stability across authentication, permissions, and data integrity.

## Test Categories
    Authentication Flows: Verifies registration, duplicate email prevention, and the secure password reset lifecycle.
    Role-Based Permissions: Ensures Staff cannot delete items and Managers have appropriate oversight.
    Audit Integrity: Confirms that every API action triggers the correct entry in the StockLog.
    Model Logic: Unit tests for string representations and database relationships.

## Executing Tests
Run the full suite with coverage reporting:
### Run all tests
python manage.py test
### Run with coverage (requires coverage package)
coverage run manage.py test
coverage report

# API Documentation
    Endpoint,               Method,     Description,            Access Level
    /api/token/,            POST,       Login & get JWT,        Public
    /api/register/,         POST,       Register new user,      Public
    /api/items/,GET/        POST,       List/Create items,      Auth Required
    /api/users/,GET/        PUT,        Manage users,           Manager/Admin
    /api/stock-logs/,       GET,        View audit trail,       Staff+


# Technical Decisions. 
    1. Custom Permission ClassesInstead of standard Django groups, I implemented IsManagerOrReadOnly in permissions.py. This ensures that staff members can perform their duties (updating stock) without the risk of deleting records or changing item identities.
    2. Automated LoggingThe InventoryItemSerializer and StockLog model work in tandem. By overriding the update and create methods in the serializer, the system guarantees that no stock change happens without a corresponding audit log entry.
    3. Production Readiness with WhiteNoiseTo ensure the system works out-of-the-box on platforms like Render, I integrated WhiteNoise for static file serving and added a dynamic ALLOWED_HOSTS configuration in settings.py.

# Deployment 
    This project is optimized for deployment on Render.

    Build Command: pip install -r requirements.txt && python manage.py migrate
    Start Command: gunicorn backend_core.wsgi
    Static Files: Handled automatically by WhiteNoise; ensure python manage.py collectstatic is run during build.

    NOTE: If using the Render Free Tier with SQLite, the database will reset on every restart. For production data persistence, connect a PostgreSQL instance.