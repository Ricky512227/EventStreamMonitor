# Quick Start Guide - Microservices Setup

## ✅ What's Been Created

Your codebase has been successfully split into microservices:

1. **User Management Service** (`src/usermanagement_service/`)
   - User registration
   - Publishes events to Kafka

2. **Flight Booking Service** (`src/flightbooking_service/`)
   - Create, get, and cancel bookings
   - Publishes booking events to Kafka

3. **Notification Service** (`src/notification_service/`)
   - Consumes events from Kafka
   - Logs notifications to database

4. **Token Management Service** (`src/tokenmanagement_service/`)
   - Existing auth service (needs docker-compose integration)

## 🚀 Starting Services

```bash
# Start all services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Stop all
docker-compose down
```

## 📋 Service Ports

- **User Management**: http://localhost:5001
- **Flight Booking**: http://localhost:5002
- **Notification**: http://localhost:5003
- **Kafka**: localhost:9092 (external), kafka:29092 (internal)
- **Zookeeper**: localhost:2181

## 🗄️ Databases

- **User Management DB**: localhost:3304
- **Auth DB**: localhost:3305
- **Booking DB**: localhost:3306
- **Notification DB**: localhost:3307

## 📝 Next Steps

1. **Run Database Migrations**: Set up tables for each service
2. **Test Endpoints**: Use the test scripts in `tests/`
3. **Add Flight Management**: Create endpoints for managing flights
4. **Complete Auth Integration**: Add token service to docker-compose
5. **Add API Gateway**: For unified entry point

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Stop old containers
docker-compose down
docker stop $(docker ps -aq)

# Restart
docker-compose up -d
```

### Kafka Not Starting
```bash
# Check Kafka logs
docker-compose logs kafka

# Restart Kafka
docker-compose restart kafka
```

### Service Not Starting
```bash
# Check service logs
docker-compose logs [service-name]

# Rebuild service
docker-compose up -d --build [service-name]
```

## 📚 Documentation

- `MICROSERVICES_ARCHITECTURE.md` - Architecture overview
- `MICROSERVICES_SETUP.md` - Detailed setup guide
- `MICROSERVICES_SUMMARY.md` - Implementation summary

