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
  - `GET /api/v1/airliner/getUser/<id>` - Get user info
  - `DELETE /api/v1/airliner/deleteUser/<id>` - Delete user
- **gRPC**: User validation for token generation
- **Kafka**: Publishes user registration events

### 2. Token Management Service (Auth Service)
- **Purpose**: Handles authentication, JWT token generation and validation
- **Port**: TBD
- **Database**: Separate PostgreSQL database
- **Endpoints**:
  - `POST /api/v1/airliner/login` - User login
  - `POST /api/v1/airliner/generateToken` - Generate JWT token
- **gRPC**: Token validation service

### 3. Flight Booking Service
- **Purpose**: Manages flight bookings, aeroplanes, and flight schedules
- **Port**: 5002 (9092 internal)
- **Database**: `FLIGHT_BOOKINGS` (PostgreSQL)
- **Endpoints**:
  - `POST /api/v1/airliner/flights` - Create flight
  - `GET /api/v1/airliner/flights` - List flights
  - `GET /api/v1/airliner/flights/<id>` - Get flight details
  - `POST /api/v1/airliner/bookings` - Create booking
  - `GET /api/v1/airliner/bookings/<id>` - Get booking details
  - `PUT /api/v1/airliner/bookings/<id>/cancel` - Cancel booking
- **Kafka**: Publishes booking events (created, cancelled, confirmed)

### 4. Notification Service
- **Purpose**: Handles all notifications via email, SMS, push notifications
- **Port**: 5003 (9093 internal)
- **Database**: `NOTIFICATIONS` (PostgreSQL) - for notification logs
- **Kafka Consumer**: Consumes events from other services
- **Topics**:
  - `user-registration-events` - User registration notifications
  - `booking-events` - Booking confirmation/cancellation notifications
  - `flight-updates` - Flight schedule change notifications

## Service Communication

### Synchronous Communication
- **REST API**: For external clients and service-to-service calls
- **gRPC**: For internal service-to-service communication (high performance)

### Asynchronous Communication
- **Kafka**: Event-driven communication between services
  - User Management → Notification Service (user registered)
  - Flight Booking → Notification Service (booking created/cancelled)

## Infrastructure

### Databases
- `REGISTRATIONS` - User Management Service
- `AUTH_TOKENS` - Token Management Service
- `FLIGHT_BOOKINGS` - Flight Booking Service
- `NOTIFICATIONS` - Notification Service (logs)

### Message Broker
- **Kafka**: Single Kafka cluster for all event streaming
  - Topics: `user-registration-events`, `booking-events`, `flight-updates`

## Deployment

### Docker Compose Services
- `registration-db` - PostgreSQL for User Management
- `auth-db` - PostgreSQL for Token Management
- `booking-db` - PostgreSQL for Flight Booking
- `notification-db` - PostgreSQL for Notification logs
- `kafka` - Kafka broker
- `zookeeper` - Kafka dependency
- `usermanagement-service` - User Management microservice
- `auth-service` - Token Management microservice
- `booking-service` - Flight Booking microservice
- `notification-service` - Notification microservice

