# Production-Ready Directory Structure

## New Structure Overview

```
airliner-administration/
├── services/                          # All microservices
│   ├── usermanagement/                # User Management Service
│   │   ├── app/                      # Application code
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # Entry point
│   │   │   ├── config.py            # Configuration
│   │   │   ├── models/              # Database models
│   │   │   ├── views/               # API endpoints
│   │   │   ├── services/            # Business logic
│   │   │   ├── schemas/             # JSON schemas
│   │   │   ├── grpc/                # gRPC handlers
│   │   │   └── kafka/               # Kafka handlers
│   │   ├── migrations/              # Database migrations
│   │   ├── tests/                   # Service tests
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   ├── booking/                      # Flight Booking Service
│   ├── notification/                 # Notification Service
│   └── auth/                         # Auth/Token Service
├── common/                           # Shared libraries
│   └── pyportal_common/             # Common utilities
│       ├── app_handlers/
│       ├── db_handlers/
│       ├── error_handlers/
│       ├── grpc_service_handlers/
│       ├── kafka_service_handlers/
│       └── logging_handlers/
├── infrastructure/                   # Infrastructure configs
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   └── kubernetes/                  # K8s deployments
│       ├── usermanagement/
│       ├── booking/
│       ├── notification/
│       └── auth/
├── config/                           # Configuration files
│   ├── development/
│   ├── staging/
│   └── production/
├── tests/                            # Integration tests
│   ├── integration/
│   └── e2e/
├── scripts/                          # Utility scripts
│   ├── setup.sh
│   ├── migrate.sh
│   └── deploy.sh
├── docs/                             # Documentation
│   ├── api/
│   ├── architecture/
│   └── deployment/
├── proto/                            # Protocol definitions
│   └── token_proto_v1/
└── README.md
```

