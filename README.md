# EventStreamMonitor

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Kafka](https://img.shields.io/badge/Apache%20Kafka-Event%20Streaming-orange.svg)](https://kafka.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Real-time microservices monitoring platform with Kafka event streaming, error tracking, and live dashboard.

## 🎯 Overview

EventStreamMonitor is a production-ready, real-time microservices monitoring platform that collects, streams, and visualizes application logs and errors across multiple services in real-time. Perfect for monitoring distributed systems and catching issues as they happen.

## ✨ Features

- 🔄 **Real-time log collection** from multiple microservices
- 📡 **Kafka-based event streaming** for scalable log processing
- 🚨 **Automatic error filtering and tracking** (ERROR, CRITICAL levels)
- 📊 **Live monitoring dashboard** with real-time updates
- ⚡ **Redis caching** for performance optimization
- 🐳 **Microservices architecture** with Docker containerization
- 🔍 **Service-level error breakdown** and statistics
- 📈 **Grafana-ready** for advanced visualization

## 🏗️ Architecture

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
```

## 🚀 Quick Start

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

## 📦 Services

| Service | Port | Description |
|---------|------|-------------|
| **User Management** | 5001 | User registration, authentication, and management |
| **Task Processing** | 5002 | Background task processing and management |
| **Notification** | 5003 | Event-driven notification system |
| **Log Monitor** | 5004 | Real-time error monitoring dashboard |

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask
- **Message Broker**: Apache Kafka
- **Cache/Sessions**: Redis
- **Databases**: PostgreSQL (per service)
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Custom Dashboard, Grafana-ready
- **API**: RESTful APIs

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Get up and running quickly
- [Architecture Overview](MICROSERVICES_ARCHITECTURE.md) - System design details
- [Setup Guide](MICROSERVICES_SETUP.md) - Detailed setup instructions
- [Redis Integration](REDIS_SETUP.md) - Redis caching setup
- [Log Monitoring](LOG_MONITORING_QUICKSTART.md) - Log monitoring system guide

## 🔧 Development

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

# Run integration tests
cd tests
python3 -m pytest integration/
```

## 📊 Use Cases

- **DevOps Monitoring**: Monitor multiple microservices from one dashboard
- **Development & Debugging**: Real-time error visibility during development
- **Production Monitoring**: Track errors and service health in production
- **Learning & Portfolio**: Demonstrate microservices, Kafka, and monitoring skills

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Apache Kafka for event streaming
- Flask for the web framework
- Docker for containerization
- Redis for caching

## 📞 Contact

For questions or suggestions, please open an issue on GitHub.

---

⭐ If you find this project useful, please consider giving it a star!
