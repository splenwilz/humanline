# Humanline Backend - Secure FastAPI Application

A modern, secure backend API built with FastAPI, SQLAlchemy, PostgreSQL, and comprehensive security features.

## 🚀 Features

- **JWT Authentication**: Secure token-based authentication with bcrypt password hashing
- **PostgreSQL Database**: Async SQLAlchemy with Alembic migrations
- **Security Middleware**: Rate limiting, security headers, CORS protection
- **Input Validation**: Pydantic schemas for request/response validation
- **Clean Architecture**: Organized code structure with separation of concerns
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Production Ready**: Comprehensive error handling and security best practices

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Async ORM for database operations
- **Alembic**: Database migration management
- **PostgreSQL**: Robust relational database with asyncpg driver
- **JWT**: JSON Web Tokens for secure authentication
- **bcrypt**: Secure password hashing
- **Pydantic**: Data validation and serialization
- **uvicorn**: ASGI server for production deployment

## 📋 Prerequisites

- Python 3.13+
- PostgreSQL 12+
- uv (Python package manager)

## 🔧 Installation & Setup

1. **Clone and navigate to the project:**
   ```bash
   cd backend3
   ```

2. **Create virtual environment:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE backend3_db;
   CREATE USER backend3_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE backend3_db TO backend3_user;
   ```

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the application:**
   ```bash
   ./start.sh
   # Or manually: uvicorn backend3.main:app --reload
   ```

## 📖 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

### Register a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Use JWT token:
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🏗️ Project Structure

```
backend3/
├── src/backend3/           # Main application package
│   ├── api/               # API endpoints
│   │   ├── auth.py        # Authentication routes
│   │   └── users.py       # User management routes
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration settings
│   │   ├── database.py    # Database setup
│   │   ├── dependencies.py # FastAPI dependencies
│   │   └── security.py    # Security utilities
│   ├── middleware/        # Custom middleware
│   │   └── security.py    # Security middleware
│   ├── models/            # SQLAlchemy models
│   │   └── user.py        # User model
│   ├── schemas/           # Pydantic schemas
│   │   ├── auth.py        # Auth schemas
│   │   └── user.py        # User schemas
│   ├── services/          # Business logic
│   │   ├── auth_service.py # Authentication service
│   │   └── user_service.py # User service
│   └── main.py            # FastAPI application
├── alembic/               # Database migrations
├── env.example            # Environment variables template
├── start.sh              # Startup script
└── README.md             # This file
```

## 🔒 Security Features

- **Password Security**: bcrypt hashing with configurable rounds
- **JWT Tokens**: Secure token generation with expiration
- **Rate Limiting**: IP-based request limiting
- **Security Headers**: XSS, clickjacking, and content type protection
- **CORS**: Configurable cross-origin resource sharing
- **Input Validation**: Comprehensive request/response validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

## 🗄️ Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## 🧪 Testing

The application includes comprehensive error handling and validation. Test the API using:

1. **Health Check**: `GET /health`
2. **User Registration**: `POST /api/v1/auth/register`
3. **User Login**: `POST /api/v1/auth/login`
4. **Protected Routes**: Include `Authorization: Bearer <token>` header

## 🔧 Debug Toolbar (Development Only)

The FastAPI Debug Toolbar is automatically enabled in development mode and provides:

- **SQL Query Panel**: View all database queries with execution time
- **Profiling Panel**: Performance profiling of request processing
- **Request Variables Panel**: Inspect request data and parameters
- **Headers Panel**: View all request/response headers
- **Timer Panel**: Detailed timing information

**Access the debug toolbar:**
1. Make any API request through your browser or tools
2. Look for the debug toolbar icon/panel in the response
3. The toolbar provides detailed debugging information for each request

**Note**: Debug toolbar is automatically disabled in production for security.

## 🚀 Production Deployment

1. **Set environment to production:**
   ```bash
   export ENVIRONMENT=production
   ```

2. **Use a production ASGI server:**
   ```bash
   gunicorn backend3.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

3. **Set up reverse proxy** (nginx recommended)

4. **Configure SSL/TLS** for HTTPS

5. **Set up monitoring** and logging

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing secret | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `ALLOWED_ORIGINS` | CORS allowed origins | localhost:3000 |
| `ENVIRONMENT` | App environment | development |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive comments explaining business logic
3. Include proper error handling
4. Update documentation for new features
5. Test all endpoints before submitting

## 📄 License

MIT License - see LICENSE file for details
