# Real-Time Log Monitoring - Quick Start

## 🚀 Quick Start

### 1. Start Services

```bash
# Start all services including log monitor
docker-compose up -d

# Verify log monitor is running
docker-compose ps logmonitor-service
```

### 2. Access Dashboard

Open your browser: **http://localhost:5004**

The dashboard will automatically:
- Show error statistics
- Display recent errors
- Auto-refresh every 5 seconds

### 3. Generate Test Errors

```bash
# Trigger an error in a service
curl -X POST http://localhost:5001/api/v1/airliner/registerUser \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}'

# Check dashboard - error should appear within 5 seconds
```

## 📊 API Endpoints

### Get All Errors
```bash
curl http://localhost:5004/api/v1/logs/errors?limit=50
```

### Get Statistics
```bash
curl http://localhost:5004/api/v1/logs/stats
```

### Get Errors by Service
```bash
curl http://localhost:5004/api/v1/logs/errors/usermanagement
```

## 🔍 Verify Kafka Topics

```bash
# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Should see:
# - application-logs
# - application-logs-errors

# Consume logs
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic application-logs-errors \
  --from-beginning
```

## 📈 Grafana Setup

1. Install Grafana (or use Docker):
   ```bash
   docker run -d -p 3000:3000 grafana/grafana
   ```

2. Add Data Source:
   - Type: JSON API
   - URL: http://localhost:5004/api/v1/grafana
   - Access: Server

3. Create Dashboard:
   - Add panel with query: `error_count`
   - Add panel with query: `error_by_service`
   - Add panel with query: `error_by_level`

## ✨ Features

- ✅ Real-time error monitoring
- ✅ Multi-service log collection
- ✅ Automatic error filtering
- ✅ Beautiful dashboard
- ✅ Grafana integration
- ✅ REST API for automation

## 🎯 Why This Shines

1. **DevOps Skills**: Shows understanding of monitoring and observability
2. **Real-Time Processing**: Demonstrates event-driven architecture
3. **Production Ready**: Error handling, resilience, scalability
4. **Modern Stack**: Kafka, Python, Grafana - industry standard tools

## 📝 Next Steps

1. View dashboard: http://localhost:5004
2. Check API: http://localhost:5004/api/v1/logs/stats
3. Set up Grafana dashboards
4. Add alerting for critical errors

For detailed documentation, see `docs/log_monitoring_system.md`

