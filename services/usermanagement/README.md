# User Management Service

## Overview
Microservice responsible for user registration, user data management, and user validation.

## Features
- User registration
- User data retrieval
- User deletion
- gRPC server for user validation
- Kafka producer for user events

## API Endpoints
- `POST /api/v1/airliner/registerUser` - Register new user
- `GET /api/v1/airliner/getUser/<id>` - Get user information
- `DELETE /api/v1/airliner/deleteUser/<id>` - Delete user

## Configuration
Copy `.env.example` to `.env` and update with your configuration.

## Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Run service
python app/main.py
```

## Running with Docker
```bash
docker build -t usermanagement-service .
docker run -p 9091:9091 --env-file .env usermanagement-service
```

## Testing
```bash
pytest tests/
```

