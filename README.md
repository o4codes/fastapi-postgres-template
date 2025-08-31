# FastAPI PostgreSQL Template

A modern, production-ready FastAPI template with PostgreSQL, Redis, and comprehensive authentication & authorization.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.0-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-D82C20.svg)](https://redis.io/)

## 🌟 Features

- **Modern Stack:**
  - FastAPI for high-performance async API
  - PostgreSQL with SQLAlchemy 2.0 and Alembic
  - Redis for caching
  - Docker & Docker Compose setup

- **Authentication & Authorization:**
  - Role-based access control (RBAC)
  - Permission-based authorization
  - JWT authentication
  - Secure password hashing

- **Project Structure:**
  - Modular application structure
  - Repository pattern implementation
  - Service layer for business logic
  - Clean separation of concerns

- **Developer Experience:**
  - Comprehensive type hints
  - Automatic API documentation
  - Docker development environment
  - Easy-to-use CLI commands

- **Production Ready:**
  - Health checks
  - Logging setup
  - Error handling
  - Database migrations
  - Security best practices

## 🚀 Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/o4codes/fastapi-postgres-template.git
   cd fastapi-postgres-template
   ```

2. **Set up environment variables:**

   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Start with Docker:**

   ```bash
   docker-compose up -d
   ```

   Access the API at [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

4. **Without Docker (local development):**

   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Run migrations
   alembic upgrade head

   # Start the application
   uvicorn app.main:app --reload
   ```

## 🏗️ Project Structure

```bash
.
├── app/
│   ├── api/                    # API modules
│   │   ├── authentication/     # Authentication module
│   │   ├── authorization/      # Authorization module
│   │   └── users/             # Users module
│   ├── commons/               # Shared utilities
│   │   ├── models.py          # Base models
│   │   ├── repository.py      # Base repository
│   │   └── schemas.py         # Base schemas
│   ├── configs/              # Configuration
│   └── main.py              # Application entry point
├── deployments/             # Deployment configurations
├── migrations/             # Database migrations
└── tests/                 # Test suite
```

## 🔒 Authentication & Authorization

The template includes a comprehensive RBAC system:

- **Roles:** Group permissions for easier management
- **Permissions:** Fine-grained access control
- **Users:** Associated with roles for authorization

Example usage:

```python
# Protect an endpoint with permissions
@router.post("/items")
async def create_item(
    item: ItemCreate,
    user: User = Depends(get_current_user),
    has_permission: bool = Depends(require_permission("item:create"))
):
    return await service.create_item(item)
```

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Run linting
flake8 .

# Run type checking
mypy .
```

## 📚 API Documentation

- Swagger UI: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- ReDoc: [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)
- OpenAPI JSON: [http://localhost:8000/api/openapi.json](http://localhost:8000/api/openapi.json)

## 🔧 Configuration

Key configuration options in `.env`:

```ini
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_db

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Application
DEBUG=false
JWT_SECRET_KEY=your-secret-key
```

## 🚢 Deployment

The template includes Docker configurations for easy deployment:

```bash
# Build and start services
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing framework
- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
- [Alembic](https://alembic.sqlalchemy.org/) for database migrations
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
