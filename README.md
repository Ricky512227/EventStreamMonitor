# EventStreamMonitor

A real-time microservices monitoring platform with event streaming, error tracking, and live dashboard visualization.

## Overview

EventStreamMonitor collects logs from multiple microservices, streams them through Apache Kafka, filters errors automatically, and displays them in a real-time dashboard. Built with Python, Flask, Kafka, Redis, and PostgreSQL.

## Features

- Real-time log collection from multiple microservices
- Event streaming with Apache Kafka
- Automatic error filtering and tracking
- Live monitoring dashboard
- Redis caching and session management
- Microservices architecture with Docker

## Quick Start

```bash
# Start all services
docker-compose up -d

# Access dashboard
open http://localhost:5004

# Stream test errors
python3 scripts/quick_stream_errors.py
```

## Services

- **User Management** (Port 5001) - User registration and management
- **Task Processing** (Port 5002) - Background task processing
- **Notification** (Port 5003) - Event-driven notifications
- **Log Monitor** (Port 5004) - Real-time error monitoring dashboard

## Tech Stack

- Python 3.9, Flask
- Apache Kafka
- Redis
- PostgreSQL
- Docker, Docker Compose

## Documentation

- [Quick Start Guide](QUICK_START.md)
- [Architecture Overview](MICROSERVICES_ARCHITECTURE.md)
- [Setup Guide](MICROSERVICES_SETUP.md)

## License

MIT
