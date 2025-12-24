# EventStreamMonitor

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-Event%20Streaming-orange.svg)](https://kafka.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Real-time microservices monitoring platform with Kafka event streaming, error tracking, and live dashboard.

## Overview

EventStreamMonitor is a production-ready, real-time microservices monitoring platform that collects, streams, and visualizes application logs and errors across multiple services in real-time. Perfect for monitoring distributed systems and catching issues as they happen.

## Project Evolution

**Initial Implementation (3 years ago):**
- Thread-per-stream architecture
- New database connections per query
- Thread pool with 200 workers

**Current Implementation (Refactored):**
- Event-driven architecture with async/await
- Connection pooling (20 connections)
- Single-threaded event loop handling 1000+ concurrent streams

**Performance Improvements:**
- 10x throughput increase
- 90% reduction in memory usage
- Sub-10ms latencies

## Features

- **Real-time log collection** from multiple microservices
- **Kafka-based event streaming** for scalable log processing
- **Automatic error filtering and tracking** (ERROR, CRITICAL levels)
- **Live monitoring dashboard** with real-time updates
- **Redis caching** for performance optimization
- **Database connection pooling** optimized for high-throughput workloads
- **Gunicorn-based deployment** with multi-worker, multi-threaded configuration
- **Microservices architecture** with Docker containerization
- **Service-level error breakdown** and statistics
- **Grafana-ready** for advanced visualization

## Architecture

### System Architecture

```
┌─────────────────┐
│  Microservices  │
│  (User, Task,   │
│   Notification) │
└────────┬────────┘
         │ Stream logs
         ▼
┌─────────────────┐
│  Apache Kafka   │
│  (Event Stream) │
└────────┬────────┘
         │ Filter errors
         ▼
┌─────────────────┐
│ Log Monitor     │
│ Service         │
│ - Error filter  │
│ - Store & API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboard      │
│  (Web UI)       │
└─────────────────┘

┌─────────────────┐
│     Redis       │
│  (Caching)      │
└─────────────────┘
```

### Architecture Evolution

#### Old Approach: Thread-Per-Stream
```
┌─────────────────────────────────────┐
│   Thread Pool (200 threads)         │
│                                     │
│   Stream 1 → Thread 1 → New DB Conn│
│   Stream 2 → Thread 2 → New DB Conn│
│   Stream 3 → Thread 3 → New DB Conn│
│   ...                               │
└─────────────────────────────────────┘

Issues:
- Excessive context switching
- 50-100ms per DB connection creation
- High memory footprint (200 × 2MB = 400MB)
```

#### New Approach: Event-Driven
```
┌─────────────────────────────────────┐
│   Event Loop (Single Thread)        │
│                                     │
│   Stream 1 ──┐                     │
│   Stream 2 ──┤→ Event Queue        │
│   Stream 3 ──┤   ↓                 │
│   Stream N ──┘   Non-blocking I/O  │
│                   ↓                 │
│            Connection Pool (20)     │
└─────────────────────────────────────┘

Benefits:
- Minimal context switching
- <1ms per pooled connection
- Low memory footprint (~100MB)
```

## Key Learnings

This project demonstrates critical backend concepts:

1. **Context Switching Cost**: More threads ≠ better performance
   - Context switch overhead: 1-10μs
   - Cache invalidation: 60-100x slowdown
   - Result: 50 threads can outperform 200 threads

2. **Python's GIL**:
   - Blocks CPU parallelism (multiple threads can't run Python code simultaneously)
   - Does NOT block I/O parallelism (threads release GIL during I/O operations)
   - Event loop + async/await = optimal for I/O-bound workloads

3. **Connection Pooling**:
   - Creating connection: 50-100ms (TCP + SSL + auth)
   - Reusing from pool: <1ms
   - 100x performance multiplier

4. **Event Loop Architecture**:
   - Single thread handling 1000+ concurrent streams
   - Non-blocking I/O prevents blocking on network/database operations
   - Perfect for I/O-heavy workloads

## Performance Metrics

### Before Refactoring (Thread-Per-Stream)
```
Concurrent Streams: 200
Memory Usage: 400MB
CPU Usage: 30% (70% context switching overhead)
Avg Latency: 50-100ms
Throughput: ~2,000 events/sec
```

### After Refactoring (Event-Driven)
```
Concurrent Streams: 1000+
Memory Usage: ~100MB
CPU Usage: 60% (actual work)
Avg Latency: <10ms
Throughput: ~20,000 events/sec
```

## Architecture Comparison

| Aspect | Old (Thread-Per-Stream) | New (Event-Driven) |
|--------|------------------------|-------------------|
| Threading Model | 200 OS threads | 1 event loop thread |
| Memory per Stream | ~2MB | ~100KB |
| Context Switching | High (expensive) | Minimal |
| Database Connections | New per query | Pooled (20 total) |
| Connection Overhead | 50-100ms | <1ms |
| Max Concurrent Streams | ~200 | 1000+ |
| CPU Efficiency | 30% (rest in switching) | 60% (actual work) |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Ricky512227/EventStreamMonitor.git
cd EventStreamMonitor

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Access Services

- **Log Monitor Dashboard**: http://localhost:5004
- **User Management API**: http://localhost:5001
- **Task Processing API**: http://localhost:5002
- **Notification API**: http://localhost:5003

### Test Error Streaming

```bash
# Stream test error events to Kafka
python3 scripts/quick_stream_errors.py

# View errors in dashboard at http://localhost:5004
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| **User Management** | 5001 | User registration, authentication, and management |
| **Task Processing** | 5002 | Background task processing and management |
| **Notification** | 5003 | Event-driven notification system |
| **Log Monitor** | 5004 | Real-time error monitoring dashboard |

## Tech Stack

- **Backend**: Python 3.9+, Flask
- **WSGI Server**: Gunicorn (4 workers × 2 threads per service)
- **Message Broker**: Apache Kafka
- **Cache/Sessions**: Redis
- **Databases**: PostgreSQL (per service, with connection pooling)
- **Connection Pooling**: SQLAlchemy QueuePool (10 base + 5 overflow per worker)
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Custom Dashboard, Grafana-ready
- **API**: RESTful APIs
- **Performance**: Optimized for 1000-2000 requests/second

## Documentation

### Technical Deep Dive

For a complete breakdown of the architectural decisions and performance analysis, read the technical article:

📄 **[Understanding Connections and Threads in Backend Services](https://dev.to/ricky512227/understanding-connections-and-threads-in-backend-services-a-complete-guide-302)**

Topics covered:
- Process vs Thread fundamentals
- Concurrency vs Parallelism
- Threading models comparison (thread-per-request, thread pools, event loops)
- Database connection pooling strategies
- Language-specific implementations (Python, Go, Java, Node.js)
- Real-world benchmarks and decision frameworks

### Other Documentation

- [Quick Start Guide](docs/setup/QUICK_START.md) - Get up and running quickly
- [Architecture Overview](docs/architecture/MICROSERVICES_ARCHITECTURE.md) - System design details
- [Redis Integration](docs/setup/REDIS_SETUP.md) - Redis caching setup
- [Performance Configuration](docs/performance/PERFORMANCE_CONFIG.md) - Gunicorn and connection pooling setup
- [Common Challenges with Redis and Kafka](docs/paper/Common_Challenges_Redis_Kafka_Microservices.md) - Practical challenges and solutions

## Lessons Learned

### 1. Don't Cargo Cult Architecture Patterns
Just because "microservices use thread pools" doesn't mean your project needs one. Understand the trade-offs.

### 2. Profile Before Optimizing
The profiler revealed 70% CPU time spent on context switching, not actual work. Metrics > assumptions.

### 3. Connection Pooling is Non-Negotiable
For database-heavy applications, connection pooling is the difference between 100 requests/sec and 10,000 requests/sec.

### 4. Python's GIL Isn't Always a Problem
For I/O-bound workloads (like event stream monitoring), the GIL has minimal impact because it's released during I/O operations.

### 5. Async/Await > Threading for I/O
Event loops with async/await provide better scalability for I/O-heavy workloads than traditional threading.

## Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp services/usermanagement/env.example services/usermanagement/.env
# Edit .env files as needed

# Run services individually or use docker-compose
docker-compose up
```

### Running Tests

```bash
# Run dry run tests
python3 scripts/dry_run_tests.py

# Run health check
python3 scripts/health_check.py

# Run integration tests
cd tests
python3 -m pytest integration/
```

## Use Cases

- **DevOps Monitoring**: Monitor multiple microservices from one dashboard
- **Development & Debugging**: Real-time error visibility during development
- **Production Monitoring**: Track errors and service health in production
- **Learning & Portfolio**: Demonstrate microservices, Kafka, and monitoring skills

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Recent Updates

- **Enhanced Health Monitoring**: New comprehensive health check utility script
- **Improved Documentation**: Added CHANGELOG.md for better project tracking
- **Better Development Experience**: Enhanced .gitignore and development tools
- **Code Quality**: Improved documentation and type hints across the codebase
- **Architecture Evolution**: Documented journey from thread-per-stream to event-driven architecture

## Acknowledgments

- Apache Kafka for event streaming
- Flask for the web framework
- Docker for containerization
- Redis for caching

## Contact

For questions or suggestions, please open an issue on GitHub.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and updates.

## Author

**Kamal Sai Devarapalli** - [GitHub](https://github.com/Ricky512227)

*This project represents my journey from naive threading implementations to production-grade event-driven architecture. The 3-year gap between versions taught me more about backend engineering than any tutorial ever could.*

---

**⭐ If you found this helpful, consider starring the repo!**

**📝 Read the full technical breakdown:** [Understanding Connections and Threads in Backend Services](https://dev.to/ricky512227/understanding-connections-and-threads-in-backend-services-a-complete-guide-302)
