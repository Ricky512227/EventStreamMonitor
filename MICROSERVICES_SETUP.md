# Microservices Setup Guide

## Overview
This guide explains how to set up and run all microservices in the Airliner Administration system.

## Services Architecture

### 1. User Management Service
- **Port**: 5001 (external), 9091 (internal)
- **Database**: `REGISTRATIONS` (PostgreSQL on port 3304)
- **Endpoints**:
  - `POST /api/v1/airliner/registerUser` - Register new user
- **Kafka**: Publishes to `user-registration-events` topic

### 2. Flight Booking Service
- **Port**: 5002 (external), 9092 (internal)
- **Database**: `FLIGHT_BOOKINGS` (PostgreSQL on port 3306)
- **Endpoints**:
  - `POST /api/v1/airliner/bookings` - Create booking
  - `GET /api/v1/airliner/bookings/<id>` - Get booking
  - `PUT /api/v1/airliner/bookings/<id>/cancel` - Cancel booking
- **Kafka**: Publishes to `booking-events` topic

### 3. Notification Service
- **Port**: 5003 (external), 9093 (internal)
- **Database**: `NOTIFICATIONS` (PostgreSQL on port 3307)
- **Kafka Consumer**: Consumes from:
  - `user-registration-events`
  - `booking-events`
  - `flight-updates`

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
- **Topics**:
  - `user-registration-events`
  - `booking-events`
  - `flight-updates`

## Running the Services

### Start All Services
```bash
docker-compose up -d --build
```

### Start Individual Services
```bash
# User Management
docker-compose up -d usermanagement-service

# Flight Booking
docker-compose up -d booking-service

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
docker-compose logs -f booking-service
docker-compose logs -f notification-service
```

## Testing the Services

### Test User Registration
```bash
curl -X POST http://localhost:5001/api/v1/airliner/registerUser \
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

### Test Booking Creation
```bash
curl -X POST http://localhost:5002/api/v1/airliner/bookings \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "userId": 1000,
    "flightId": 1000,
    "numberOfSeats": 2
  }'
```

## Environment Variables

Each service has its own `.env.dev` file:
- `src/usermanagement_service/.env.dev`
- `src/flightbooking_service/.env.dev`
- `src/notification_service/.env.dev`

## Next Steps

1. **Complete Token Management Service**: Add to docker-compose
2. **Add Flight Management**: Create endpoints for managing flights
3. **Implement gRPC Communication**: For service-to-service calls
4. **Add API Gateway**: For routing and authentication
5. **Add Monitoring**: Prometheus, Grafana for observability

