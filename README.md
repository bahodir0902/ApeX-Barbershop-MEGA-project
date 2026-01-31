# ApeX Barbershop API

A production-grade REST API for barbershop management built with Django REST Framework.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.1-green)
![DRF](https://img.shields.io/badge/DRF-3.16-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🚀 Features

### Core Features
- **User Management**: Custom user model with role-based access control (Client, Barber, Owner, Admin)
- **Barbershop Management**: Full CRUD operations for barbershops, barbers, and haircuts
- **Appointment Booking**: Complete booking system with availability checking and conflict prevention
- **Feedback System**: Customer reviews and ratings with barber responses

### Authentication & Security
- **JWT Authentication**: Secure token-based authentication with refresh tokens
- **Google OAuth**: Social login integration
- **Role-Based Permissions**: Fine-grained access control
- **Idempotent Requests**: Prevent duplicate bookings

### Production Features
- **PostgreSQL Database**: With trigram similarity search for fuzzy matching
- **Redis Caching**: High-performance caching layer
- **Celery + Celery Beat**: Asynchronous task processing and scheduled jobs
- **S3 Storage**: Configurable cloud storage for media files
- **Structured Logging**: JSON-formatted logs for monitoring
- **Custom Exception Handling**: Consistent error responses

### Admin & Documentation
- **Unfold Admin**: Beautiful, modern admin interface with custom dashboards
- **DRF Spectacular**: OpenAPI 3.0 documentation with Swagger UI and ReDoc
- **Health Checks**: Kubernetes-ready health endpoints

### DevOps
- **Docker & Docker Compose**: Containerized deployment
- **Kubernetes Manifests**: Production-ready K8s configuration
- **GitHub Actions CI/CD**: Automated testing and deployment
- **Prometheus & Grafana**: Monitoring and observability

## 📋 Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

## 🛠️ Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/apex-barbershop-api.git
   cd apex-barbershop-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Docker Development

```bash
docker-compose up -d
```

## 🔗 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login with email/phone |
| POST | `/api/v1/auth/logout/` | Logout (blacklist token) |
| POST | `/api/v1/auth/token/` | Get JWT tokens |
| POST | `/api/v1/auth/token/refresh/` | Refresh access token |
| POST | `/api/v1/auth/password/change/` | Change password |
| POST | `/api/v1/auth/google/` | Google OAuth login |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me/` | Get current user |
| PATCH | `/api/v1/users/update_me/` | Update current user |
| GET | `/api/v1/users/` | List users (admin only) |
| DELETE | `/api/v1/users/{id}/` | Delete user |

### Barbershops
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/barbershops/` | List barbershops |
| POST | `/api/v1/barbershops/` | Create barbershop |
| GET | `/api/v1/barbershops/{id}/` | Get barbershop detail |
| PATCH | `/api/v1/barbershops/{id}/` | Update barbershop |
| DELETE | `/api/v1/barbershops/{id}/` | Delete barbershop |
| GET | `/api/v1/barbershops/{id}/barbers/` | Get barbershop's barbers |
| GET | `/api/v1/barbershops/{id}/haircuts/` | Get barbershop's haircuts |

### Barbers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/barbers/` | List barbers |
| POST | `/api/v1/barbers/` | Create barber |
| GET | `/api/v1/barbers/{id}/` | Get barber detail |
| PATCH | `/api/v1/barbers/{id}/` | Update barber |
| GET | `/api/v1/barbers/{id}/available_days/` | Get available days |
| GET | `/api/v1/barbers/{id}/available_slots/` | Get available time slots |
| PATCH | `/api/v1/barbers/{id}/update_schedule/` | Update schedule |

### Haircuts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/haircuts/` | List haircuts |
| POST | `/api/v1/haircuts/` | Create haircut |
| GET | `/api/v1/haircuts/{id}/` | Get haircut detail |
| PATCH | `/api/v1/haircuts/{id}/` | Update haircut |
| GET | `/api/v1/haircuts/{id}/barbers/` | Get barbers for haircut |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/appointments/` | List appointments |
| POST | `/api/v1/appointments/` | Create appointment |
| GET | `/api/v1/appointments/{id}/` | Get appointment detail |
| DELETE | `/api/v1/appointments/{id}/` | Cancel appointment |
| POST | `/api/v1/appointments/{id}/complete/` | Complete appointment |
| GET | `/api/v1/appointments/my_appointments/` | Get my appointments |

### Feedbacks
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/feedbacks/` | List feedbacks |
| POST | `/api/v1/feedbacks/` | Create feedback |
| GET | `/api/v1/feedbacks/{id}/` | Get feedback detail |
| DELETE | `/api/v1/feedbacks/{id}/` | Delete feedback |
| POST | `/api/v1/feedbacks/{id}/respond/` | Add barber response |

## 📚 API Documentation

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run specific test class
pytest tests/test_users.py::TestUserModel
```

## 🔧 Code Quality

```bash
# Install pre-commit hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with Ruff
ruff check .
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Run migrations
docker-compose exec api python manage.py migrate

# Create superuser
docker-compose exec api python manage.py createsuperuser

# Stop all services
docker-compose down
```

## ☸️ Kubernetes Deployment

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -n apex-barbershop

# View logs
kubectl logs -f deployment/apex-api -n apex-barbershop
```

## 📊 Monitoring

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000` (admin/admin)

## 🔒 Environment Variables

See `.env.example` for all available configuration options.

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributors

- ApeX Barbershop Team

## 🙏 Acknowledgments

- Django REST Framework
- Unfold Admin
- DRF Spectacular
