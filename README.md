# VGreen Backend API

FastAPI backend with SQLAlchemy ORM for the VGreen application.

## Project Structure

```
backend/
├── api/                 # API route handlers
│   ├── health_routes.py # Health check and test endpoints
│   └── user_routes.py   # User CRUD endpoints
├── models/              # SQLAlchemy database models
│   └── user.py          # User model
├── schemas/             # Pydantic request/response schemas
│   └── user.py          # User schemas
├── services/            # Business logic layer
│   └── user_service.py  # User service with database operations
├── config.py            # Configuration and settings
├── database.py          # Database connection and session setup
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md            # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Database

Update `.env` file with your MySQL credentials:

```
DB_USER=root
DB_PASSWORD=root
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=vgreen
```

Make sure MySQL is running and the database `vgreen` exists.

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

- **GET** `/api/health/` - Health check endpoint
- **GET** `/api/health/test` - Test endpoint

### Users

- **POST** `/api/users/` - Create a new user
- **GET** `/api/users/` - List all users (with pagination)
- **GET** `/api/users/{user_id}` - Get user by ID
- **PUT** `/api/users/{user_id}` - Update user
- **DELETE** `/api/users/{user_id}` - Delete user

## API Documentation

Once the server is running, access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Example Requests

### Create User

```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "full_name": "John Doe",
    "password": "securepassword123"
  }'
```

### Test Endpoint

```bash
curl "http://localhost:8000/api/health/test"
```

### List Users

```bash
curl "http://localhost:8000/api/users/?skip=0&limit=10"
```

## Database Models

### User

- `id` (Integer, Primary Key)
- `email` (String, Unique)
- `username` (String, Unique)
- `full_name` (String, Optional)
- `hashed_password` (String)
- `is_active` (Boolean, Default: True)
- `created_at` (DateTime)
- `updated_at` (DateTime)

## Technologies Used

- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation using Python type hints
- **MySQL** - Database
- **Uvicorn** - ASGI server
- **Passlib** - Password hashing
