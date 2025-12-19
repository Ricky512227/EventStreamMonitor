# EventStreamMonitor

Real-time microservices monitoring platform with Kafka event streaming and error tracking.

## What it does

EventStreamMonitor collects logs from multiple microservices, streams them through Kafka, filters errors automatically, and displays everything in a live dashboard. Useful for monitoring distributed systems and catching issues in real-time.

## Features

- Real-time log collection from multiple services
- Kafka-based event streaming
- Automatic error filtering and tracking
- Live monitoring dashboard
- Redis caching
- Microservices architecture with Docker

## Quick Start

```bash
# Start all services
docker-compose up -d

# Access dashboard
open http://localhost:5004

# Test error streaming
python3 scripts/quick_stream_errors.py
```

## Services

- **User Management** (Port 5001) - User registration and management
- **Task Processing** (Port 5002) - Background task processing
- **Notification** (Port 5003) - Event-driven notifications  
- **Log Monitor** (Port 5004) - Real-time error monitoring dashboard

## Tech Stack

Python, Flask, Apache Kafka, Redis, PostgreSQL, Docker

## Documentation

- [Quick Start Guide](QUICK_START.md)
- [Architecture Overview](MICROSERVICES_ARCHITECTURE.md)
- [Setup Guide](MICROSERVICES_SETUP.md)
