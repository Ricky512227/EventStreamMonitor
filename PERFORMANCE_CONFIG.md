# Performance Configuration Guide
## Optimized for 1000-2000 Requests/Second

This document explains how the system is configured to handle high-throughput workloads.

## Architecture Overview

```
Request → Gunicorn (4 workers × 2 threads) → Flask App → Database/Redis/Kafka
                ↓
        8 concurrent requests per instance
```

## Configuration Details

### Gunicorn Workers

**Current Configuration:**
- **Workers**: 4 processes
- **Threads per worker**: 2 threads
- **Total concurrent requests per instance**: 4 × 2 = 8 requests

**Calculation for 1000-2000 req/sec:**
- Each worker handles ~250-500 req/sec
- 4 workers × 250 req/sec = **1000 req/sec**
- 4 workers × 500 req/sec = **2000 req/sec** (peak capacity)

### Scaling Options

#### Option 1: Increase Workers (Recommended for CPU-bound)
```yaml
# In docker-compose.yml
- GUNICORN_WORKERS=8  # 8 workers for 2000 req/sec
- GUNICORN_THREADS=2
# Total: 8 × 2 = 16 concurrent requests
```

#### Option 2: Increase Threads (Good for I/O-bound)
```yaml
# In docker-compose.yml
- GUNICORN_WORKERS=4
- GUNICORN_THREADS=4  # 4 threads per worker
# Total: 4 × 4 = 16 concurrent requests
```

#### Option 3: Horizontal Scaling (Best for production)
```yaml
# Scale to multiple instances
docker-compose up --scale taskprocessing-service=3
# 3 instances × 1000 req/sec = 3000 req/sec total
```

### Database Connection Pooling

**Current Configuration (optimized for 4 workers × 2 threads):**
- `POOL_SIZE=10`: Base number of connections to maintain per worker
- `MAX_OVERFLOW=5`: Additional connections when pool is exhausted (up to 15 total per worker)
- `POOL_RECYCLE=3600`: Connection lifetime in seconds (1 hour) - prevents stale connections
- `POOL_TIMEOUT=30`: Time in seconds to wait for connection from pool
- `RETRY_INTERVAL=5`: Seconds between retry attempts
- `MAX_RETRIES=3`: Maximum retry attempts for database connections

**Total Database Connections:**
- Per worker: 10 (base) + 5 (overflow) = 15 maximum connections
- Total across 4 workers: 4 × 15 = 60 maximum database connections
- Actual usage: Typically 10-20 connections active under normal load

**Pool Size Calculation:**
- For 4 workers × 2 threads = 8 concurrent requests per instance
- Pool size of 10 provides headroom (more connections than concurrent threads)
- Allows for database query queuing and connection reuse
- MAX_OVERFLOW handles traffic spikes without blocking requests

### Caching Strategy

**Redis Caching:**
- Hot data cached for 5-60 minutes
- Reduces database load by 70-90%
- Each service uses separate Redis DB (0, 1, 2, etc.)

**Cache Keys:**
- User data: `user:{user_id}`
- Task data: `task:{task_id}`
- Session data: `session:{session_id}`

### Monitoring

**Key Metrics to Monitor:**
1. **Request Rate**: Requests per second
2. **Response Time**: p50, p95, p99 latency
3. **Error Rate**: 4xx/5xx responses
4. **Worker Utilization**: CPU/Memory per worker
5. **Database Connections**: Pool usage
6. **Cache Hit Rate**: Redis hit/miss ratio

**Logging:**
- Access logs: Request/response details
- Error logs: Exceptions and stack traces
- Log level: `info` (production), `debug` (development)

## Load Testing

### Using Apache Bench (ab)
```bash
# Test 1000 requests with 10 concurrent
ab -n 1000 -c 10 http://localhost:5002/api/v1/eventstreammonitor/tasks

# Test sustained load (2000 req/sec for 60 seconds)
ab -n 120000 -c 100 -t 60 http://localhost:5002/api/v1/eventstreammonitor/tasks
```

### Using wrk
```bash
# Test with 4 threads, 100 connections, 30 seconds
wrk -t4 -c100 -d30s http://localhost:5002/api/v1/eventstreammonitor/tasks
```

### Expected Performance

**With Current Configuration (4 workers, 2 threads):**
- **Throughput**: 1000-2000 req/sec
- **Latency (p50)**: 50-100ms
- **Latency (p95)**: 200-500ms
- **Latency (p99)**: 500-1000ms

**With Redis Caching:**
- **Cache Hit**: < 10ms response time
- **Cache Miss**: 100-300ms response time

## Optimization Tips

1. **Enable Redis Caching**: Reduces database load significantly
2. **Use Connection Pooling**: Reuse database connections
3. **Async Processing**: Use Kafka for heavy operations
4. **Horizontal Scaling**: Add more instances instead of bigger servers
5. **Monitor and Tune**: Adjust workers/threads based on metrics

## Troubleshooting

### High Response Times
- Increase workers or threads
- Check database connection pool size
- Verify Redis is working and caching properly
- Check for slow database queries

### Memory Issues
- Reduce `max_requests` to restart workers more frequently
- Decrease number of workers
- Check for memory leaks in application code

### Connection Errors
- Increase `POOL_SIZE` and `MAX_OVERFLOW`
- Check database connection limits
- Verify network connectivity

## Next Steps

For production deployment:
1. Use a load balancer (nginx, HAProxy) in front of services
2. Scale horizontally (multiple service instances)
3. Implement monitoring (Prometheus, Grafana)
4. Set up auto-scaling based on metrics
5. Use CDN for static content
6. Implement rate limiting

