# Production-Ready Microservices Structure

This document describes the production-ready directory structure for the Airliner Administration microservices system.

## Directory Structure

```
AirlinerAdminstration/
├── services/                    # All microservices
│   ├── usermanagement/         # User Management Service
│   │   ├── app/                # Application code
│   │   │   ├── main.py         # Service entry point
│   │   │   ├── __init__.py     # Service initialization
│   │   │   ├── app_configs.py  # Configuration
│   │   │   ├── models/         # Database models
│   │   │   ├── views/          # API endpoints
│   │   │   ├── schemas/        # JSON schemas
│   │   │   ├── user_management_grpc/  # gRPC handlers
│   │   │   └── user_management_kafka/ # Kafka handlers
│   │   ├── migrations/         # Database migrations
│   │   ├── tests/              # Service tests
│   │   ├── Dockerfile          # Service Dockerfile
│   │   ├── requirements.txt    # Python dependencies
│   │   └── env.example         # Environment template
│   ├── booking/                # Flight Booking Service
│   │   └── [same structure]
│   ├── notification/           # Notification Service
│   │   └── [same structure]
│   └── auth/                   # Authentication Service
│       └── [same structure]
├── common/                     # Shared libraries
│   └── pyportal_common/        # Common utilities
│       ├── app_handlers/       # App management
│       ├── db_handlers/        # Database handlers
│       ├── error_handlers/     # Error handling
│       ├── grpc_service_handlers/  # gRPC utilities
│       ├── kafka_service_handlers/ # Kafka utilities
│       └── logging_handlers/   # Logging utilities
├── infrastructure/             # Infrastructure configurations
│   ├── docker/
│   │   └── docker-compose.yml  # Docker Compose config
│   └── kubernetes/             # Kubernetes manifests
├── config/                     # Environment configurations
│   ├── development/
│   ├── staging/
│   └── production/
├── tests/                      # Integration and E2E tests
│   ├── integration/
│   └── e2e/
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
├── proto/                      # Protocol definitions (gRPC)
└── logs/                       # Application logs
```

## Key Changes from Old Structure

### 1. Service Organization
- **Old**: `src/usermanagement_service/`
- **New**: `services/usermanagement/app/`

### 2. Common Library
- **Old**: `src/pyportal_common/`
- **New**: `common/pyportal_common/`

### 3. Imports
- **Old**: `from src.pyportal_common...` or `from src.usermanagement_service...`
- **New**: `from common.pyportal_common...` or `from app...` (within service)

### 4. Entry Points
- **Old**: `src/usermanagement_service/usermanagement.py`
- **New**: `services/usermanagement/app/main.py`

### 5. Dockerfiles
- **Old**: `src/Dockerfile.usrmngnt`
- **New**: `services/usermanagement/Dockerfile`

## Building and Running Services

### Using Docker Compose (Recommended)

```bash
# From project root
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# View logs
docker-compose -f infrastructure/docker/docker-compose.yml logs -f

# Stop services
docker-compose -f infrastructure/docker/docker-compose.yml down
```

### Building Individual Services

```bash
# User Management Service
cd services/usermanagement
docker build -f Dockerfile -t usermanagement-service:latest ..

# Booking Service
cd services/booking
docker build -f Dockerfile -t booking-service:latest ..

# Notification Service
cd services/notification
docker build -f Dockerfile -t notification-service:latest ..
```

### Running Services Locally (Development)

```bash
# Set PYTHONPATH and run
export PYTHONPATH=/path/to/AirlinerAdminstration:$PYTHONPATH

# User Management
cd services/usermanagement
python app/main.py

# Booking
cd services/booking
python app/main.py

# Notification
cd services/notification
python app/main.py
```

## Import Patterns

### Within a Service
```python
# Import from common library
from common.pyportal_common.logging_handlers.base_logger import LogMonitor
from common.pyportal_common.app_handlers.app_manager import AppHandler

# Import within service (from app/)
from app.models.user_model import UserBase
from app.views.create_user import register_user
```

### Entry Point (main.py)
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from app import usermanager_app, user_management_logger
```

## Environment Variables

Each service requires environment variables. See `services/*/env.example` for templates.

Key variables:
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `SERVER_IPADDRESS`: Service bind address (default: 0.0.0.0)
- `SERVER_PORT`: Service port (default: 9091/9092/9093)

## Database Migrations

Run migrations for each service:

```bash
# User Management
cd services/usermanagement
flask db upgrade

# Booking
cd services/booking
flask db upgrade

# Notification
cd services/notification
flask db upgrade
```

## Testing

### Service-Level Tests
```bash
# Run tests for a specific service
cd services/usermanagement
python -m pytest tests/
```

### Integration Tests
```bash
# From project root
python -m pytest tests/integration/
```

### E2E Tests
```bash
# Ensure all services are running
python tests/test_all_services.py
```

## Logs

Logs are stored per service:
- `logs/usermanagement/`
- `logs/booking/`
- `logs/notification/`

## Next Steps

1. **Update CI/CD**: Update your CI/CD pipelines to use the new structure
2. **Update Documentation**: Update API documentation and deployment guides
3. **Monitoring**: Set up monitoring and observability for each service
4. **Security**: Review and update security configurations
5. **Performance**: Load test each service independently

## Migration Notes

- The old `src/` directory structure is preserved for reference
- All imports have been updated to use the new paths
- Dockerfiles now use the new structure with proper build contexts
- docker-compose.yml has been updated to use new service paths

## Support

For issues or questions about the new structure, please refer to:
- `STRUCTURE_SUMMARY.md` - Detailed structure documentation
- `MIGRATION_GUIDE.md` - Migration guide from old structure
- `README_PRODUCTION.md` - Production deployment guide

