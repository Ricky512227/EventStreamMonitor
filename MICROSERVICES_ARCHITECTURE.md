# Microservices Architecture

## Overview
This document describes the microservices architecture for the Airliner Administration system.

## Services

### 1. User Management Service
- **Purpose**: Manages user accounts, registration, and user data
- **Port**: 5001 (9091 internal)
- **Database**: `REGISTRATIONS` (PostgreSQL)
- **Endpoints**:
  - `POST /api/v1/airliner/registerUser` - Register new user
  - (Note: Other endpoints may use different URL patterns - check service code for current routes)
- **gRPC**: User validation for token generation
- **Kafka**: Publishes user registration events

### 2. Token Management Service (Auth Service)
- **Purpose**: Handles authentication, JWT token generation and validation
- **Port**: TBD
- **Database**: Separate PostgreSQL database
- **Endpoints**:
  - `POST /api/v1/airliner/login` - User login (check service code for current routes)
  - `POST /api/v1/airliner/generateToken` - Generate JWT token (check service code for current routes)
- **gRPC**: Token validation service

### 3. Task Processing Service
- **Purpose**: Handles task management and processing operations
- **Port**: 5002 (9092 internal)
- **Database**: `TASK_PROCESSING` (PostgreSQL)
- **Endpoints**:
  - `POST /api/v1/eventstreammonitor/tasks` - Create task
  - `GET /api/v1/eventstreammonitor/tasks` - List tasks
  - `GET /api/v1/eventstreammonitor/tasks/<id>` - Get task details
  - `PUT /api/v1/eventstreammonitor/tasks/<id>/cancel` - Cancel task
- **Kafka**: Publishes task processing events

### 4. Notification Service
- **Purpose**: Handles all notifications via email, SMS, push notifications
- **Port**: 5003 (9093 internal)
- **Database**: `NOTIFICATIONS` (PostgreSQL) - for notification logs
- **Kafka Consumer**: Consumes events from other services
- **Topics**:
  - `user-registration-events` - User registration notifications
  - Task processing events
  - Various service events

## Service Communication

### Synchronous Communication
- **REST API**: For external clients and service-to-service calls
- **gRPC**: For internal service-to-service communication (high performance)

### Asynchronous Communication
- **Kafka**: Event-driven communication between services
  - User Management → Notification Service (user registered)
  - Task Processing → Notification Service (task events)

## Infrastructure

### Databases
- `REGISTRATIONS` - User Management Service
- `AUTH_TOKENS` - Token Management Service
- `TASK_PROCESSING` - Task Processing Service
- `NOTIFICATIONS` - Notification Service (logs)

### Message Broker
- **Kafka**: Single Kafka cluster for all event streaming
  - Topics: Various event topics for service communication

## Deployment

### Docker Compose Services
- `registration-db` - PostgreSQL for User Management
- `auth-db` - PostgreSQL for Token Management
- `taskprocessing-db` - PostgreSQL for Task Processing
- `notification-db` - PostgreSQL for Notification logs
- `kafka` - Kafka broker
- `zookeeper` - Kafka dependency
- `usermanagement-service` - User Management microservice
- `auth-service` - Token Management microservice
- `taskprocessing-service` - Task Processing microservice
- `notification-service` - Notification microservice

