# Test Kafka Error Streaming

## Quick Test Scripts

### 1. Generate One-Time Error Events

```bash
python3 scripts/generate_error_events.py
```

This will:
- Generate 10 random error events
- Send them to Kafka
- Show messages in console
- Errors go to `application-logs-errors` topic

### 2. Continuous Error Streaming

```bash
python3 scripts/stream_errors_to_kafka.py
```

This will:
- Continuously stream errors to Kafka
- Random intervals (2-5 seconds)
- Press Ctrl+C to stop
- Good for testing dashboard auto-refresh

## Verify Errors in Kafka

### Check Error Topic

```bash
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic application-logs-errors \
  --from-beginning \
  --max-messages 5
```

### Check All Logs Topic

```bash
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic application-logs \
  --from-beginning \
  --max-messages 5
```

## Check Dashboard

Open: http://localhost:5004

You should see:
- Error statistics updating
- Recent errors appearing
- Service breakdown

## Check API

```bash
# Get all errors
curl http://localhost:5004/api/v1/logs/errors?limit=10

# Get statistics
curl http://localhost:5004/api/v1/logs/stats

# Get errors by service
curl http://localhost:5004/api/v1/logs/errors/usermanagement
```

## Environment Variables

Set if needed:

```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
python3 scripts/generate_error_events.py
```

## Troubleshooting

### No errors appearing?

1. Check Kafka is running:
   ```bash
   docker-compose ps kafka
   ```

2. Check logmonitor service:
   ```bash
   docker-compose ps logmonitor-service
   docker-compose logs logmonitor-service
   ```

3. Check Kafka topics exist:
   ```bash
   docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092
   ```

### Create topics manually if needed:

```bash
docker-compose exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic application-logs \
  --partitions 1 \
  --replication-factor 1

docker-compose exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic application-logs-errors \
  --partitions 1 \
  --replication-factor 1
```

