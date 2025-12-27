#!/usr/bin/env python3
"""
Health Check Utility for EventStreamMonitor Services

This script provides comprehensive health checking for all microservices,
including connectivity, health endpoints, and service status monitoring.
"""
import requests
import socket
import time
import sys
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ServiceHealth:
    """Service health status container"""
    name: str
    url: str
    port: int
    is_reachable: bool
    is_healthy: bool
    response_time: float
    status_code: int = 0
    error_message: str = ""

SERVICES = {
    "usermanagement": {
        "url": "http://localhost:5001",
        "port": 5001,
        "health_endpoint": "/health",
        "name": "User Management"
    },
    "taskprocessing": {
        "url": "http://localhost:5002",
        "port": 5002,
        "health_endpoint": "/health",
        "name": "Task Processing"
    },
    "notification": {
        "url": "http://localhost:5003",
        "port": 5003,
        "health_endpoint": "/health",
        "name": "Notification"
    },
    "logmonitor": {
        "url": "http://localhost:5004",
        "port": 5004,
        "health_endpoint": "/health",
        "name": "Log Monitor"
    }
}


def check_port_connectivity(host: str, port: int, timeout: int = 3) -> bool:
    """
    Check if a port is open and accessible

    Args:
        host: Hostname or IP address
        port: Port number
        timeout: Connection timeout in seconds

    Returns:
        True if port is accessible, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except (socket.error, OSError):
        return False


def check_service_health(service_config: Dict) -> ServiceHealth:
    """
    Perform comprehensive health check for a service

    Args:
        service_config: Service configuration dictionary

    Returns:
        ServiceHealth object with health status
    """
    name = service_config.get("name", "Unknown")
    url = service_config["url"]
    port = service_config["port"]
    health_endpoint = service_config.get("health_endpoint", "/health")

    # Check port connectivity
    is_reachable = check_port_connectivity("localhost", port)

    # Check health endpoint
    is_healthy = False
    response_time = 0.0
    status_code = 0
    error_message = ""

    if is_reachable:
        try:
            start_time = time.time()
            response = requests.get(
                f"{url}{health_endpoint}",
                timeout=5
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            status_code = response.status_code
            is_healthy = response.status_code == 200
        except requests.exceptions.Timeout:
            error_message = "Request timeout"
        except requests.exceptions.ConnectionError:
            error_message = "Connection refused"
        except (requests.exceptions.RequestException, ValueError) as e:
            error_message = str(e)
    else:
        error_message = "Port not accessible"

    return ServiceHealth(
        name=name,
        url=url,
        port=port,
        is_reachable=is_reachable,
        is_healthy=is_healthy,
        response_time=response_time,
        status_code=status_code,
        error_message=error_message
    )


def print_health_status(health: ServiceHealth):
    """
    Print formatted health status for a service

    Args:
        health: ServiceHealth object
    """
    status_icon = "✓" if health.is_healthy else "✗"
    status_text = "HEALTHY" if health.is_healthy else "UNHEALTHY"

    print(f"\n{status_icon} {health.name}")
    print(f"  URL: {health.url}")
    print(f"  Port: {health.port}")
    print(f"  Status: {status_text}")

    if health.is_reachable:
        print(f"  Response Time: {health.response_time:.2f}ms")
        print(f"  Status Code: {health.status_code}")
    else:
        print(f"  Error: {health.error_message}")


def main():
    """Main health check function"""
    print("=" * 70)
    print("EVENTSTREAMMONITOR - SERVICE HEALTH CHECK")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    health_results: List[ServiceHealth] = []

    # Check all services
    for service_config in SERVICES.values():
        health = check_service_health(service_config)
        health_results.append(health)
        print_health_status(health)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    healthy_count = sum(1 for h in health_results if h.is_healthy)
    total_count = len(health_results)

    print(f"Services Healthy: {healthy_count}/{total_count}")

    if healthy_count == total_count:
        print("\n✓ All services are healthy and operational!")
        return 0
    else:
        print("\n✗ Some services are not healthy. Check logs with:")
        print("  docker-compose logs [service-name]")
        return 1

if __name__ == "__main__":
    sys.exit(main())
