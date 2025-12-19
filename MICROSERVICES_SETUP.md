# Microservices Setup Guide

## Overview
This guide explains how to set up and run all microservices in the EventStreamMonitor system.

## Services Architecture

### 1. User Management Service
- **Port**: 5001 (external), 9091 (internal)
- **Database**: `REGISTRATIONS` (PostgreSQL on port 3304)
- **Endpoints**:
  - `POST /api/v1/eventstreammonitor/users/register` - Register new user
- **Kafka**: Publishes to `user-registration-events` topic

### 2. Task Processing Service (formerly Booking Service)
- **Port**: 5002 (external), 9092 (internal)
- **Database**: `TASK_PROCESSING` (PostgreSQL on port 3306)
- **Endpoints**:
  - Task management endpoints
  - API endpoints for task processing operations
- **Kafka**: Publishes task-related events

### 3. Notification Service
- **Port**: 5003 (external), 9093 (internal)
- **Database**: `NOTIFICATIONS` (PostgreSQL on port 3307)
- **Kafka Consumer**: Consumes from various event topics including:
  - `user-registration-events`
  - Task processing events
  - Other service events

### 4. Token Management Service (Auth)
- **Port**: TBD
- **Database**: `AUTH_TOKENS` (PostgreSQL on port 3305)
- **Status**: Existing service, needs docker-compose integration

## Infrastructure

### Databases
- All services use PostgreSQL with separate databases
- Each service has its own database instance

### Kafka
- **Broker**: `kafka:29092` (internal), `localhost:9092` (external)
- **Zookeeper**: Required for Kafka
- **Topics**: Various event topics for service communication

## Running the Services

### Start All Services
```bash
docker-compose up -d --build
```

### Start Individual Services
```bash
# User Management
docker-compose up -d usermanagement-service

# Task Processing
docker-compose up -d taskprocessing-service

# Notification
docker-compose up -d notification-service
```

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f usermanagement-service
docker-compose logs -f taskprocessing-service
docker-compose logs -f notification-service
```

## Testing the Services

### Test User Registration
```bash
curl -X POST http://localhost:5001/api/v1/eventstreammonitor/users/register \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Host: localhost:5001" \
  -H "User-Agent: test" \
  -H "Connection: keep-alive" \
  -d '{
    "username": "testuser",
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "password": "TestPass123",
    "dateOfBirth": "1990-01-01"
  }'
```

### Test Task Processing Service
```bash
# Check health endpoint
curl http://localhost:5002/health

# Check service endpoints as defined in the API
```

## Environment Variables

Each service has its own environment configuration in `docker-compose.yml`:
- Database connection pooling parameters (POOL_SIZE, MAX_OVERFLOW, etc.)
- Gunicorn configuration (GUNICORN_WORKERS, GUNICORN_THREADS)
- Service-specific settings

## Performance Configuration

All services are configured with:
- **Gunicorn**: 4 workers × 2 threads per service
- **Database Connection Pooling**: 10 base connections + 5 overflow per worker
- **Target Capacity**: 1000-2000 requests/second per service instance

See [PERFORMANCE_CONFIG.md](PERFORMANCE_CONFIG.md) for detailed configuration and scaling options.

## Next Steps

1. **Complete Token Management Service**: Add to docker-compose
2. **Implement gRPC Communication**: For service-to-service calls
3. **Add API Gateway**: For routing and authentication
4. **Add Monitoring**: Prometheus, Grafana for observability
5. **Load Testing**: Use provided load testing scripts to verify performance

