# Production-Ready Microservices Structure

## Overview
This repository has been reorganized into a production-ready microservices architecture.

## Directory Structure

```
.
├── services/                    # All microservices
│   ├── usermanagement/         # User Management Service
│   ├── booking/                # Flight Booking Service
│   ├── notification/           # Notification Service
│   └── auth/                   # Authentication Service
├── common/                     # Shared libraries
│   └── pyportal_common/        # Common utilities
├── infrastructure/             # Infrastructure configurations
│   ├── docker/                 # Docker Compose files
│   └── kubernetes/             # Kubernetes manifests
├── config/                     # Environment configurations
│   ├── development/
│   ├── staging/
│   └── production/
├── tests/                      # Integration and E2E tests
├── scripts/                    # Utility scripts
├── docs/                       # Documentation
└── proto/                      # Protocol definitions
```

## Service Structure

Each service follows this structure:
```
service-name/
├── app/                        # Application code
│   ├── main.py                # Entry point
│   ├── config.py              # Configuration
│   ├── models/                # Database models
│   ├── views/                 # API endpoints
│   ├── services/              # Business logic
│   ├── schemas/               # JSON schemas
│   ├── grpc/                  # gRPC handlers (if applicable)
│   └── kafka/                 # Kafka handlers (if applicable)
├── migrations/                # Database migrations
├── tests/                     # Service tests
├── Dockerfile                 # Service Dockerfile
├── requirements.txt           # Python dependencies
├── .env.example               # Environment template
└── README.md                  # Service documentation
```

## Quick Start

### Development
```bash
# Start all services
cd infrastructure/docker
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Building Individual Services
```bash
# Build a service
cd services/usermanagement
docker build -t usermanagement-service .

# Run service
docker run -p 9091:9091 --env-file .env usermanagement-service
```

## Configuration

1. Copy `.env.example` to `.env` in each service directory
2. Update configuration values in `config/development/`
3. For production, use `config/production/` with secure values

## Migration from Old Structure

The old structure in `src/` is preserved. To migrate:

1. Run the migration script:
   ```bash
   ./scripts/migrate_to_production_structure.sh
   ```

2. Update imports in service code to use new paths

3. Update Dockerfiles to use new structure

## Deployment

### Docker Compose
```bash
cd infrastructure/docker
docker-compose -f docker-compose.yml up -d
```

### Kubernetes
```bash
kubectl apply -f infrastructure/kubernetes/
```

## Testing

```bash
# Run integration tests
pytest tests/integration/

# Run E2E tests
pytest tests/e2e/
```

## Documentation

- Architecture: `docs/architecture/`
- API Documentation: `docs/api/`
- Deployment Guides: `docs/deployment/`

