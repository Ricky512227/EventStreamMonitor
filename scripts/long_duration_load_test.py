#!/usr/bin/env python3
"""
Long Duration Load Testing Script for All Services
Runs continuous load testing for a specified duration (default: 1 hour)
"""
import requests
import time
import json
import statistics
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from datetime import datetime, timedelta

# Service endpoints
SERVICES = {
    "usermanagement": {
        "url": "http://localhost:5001",
        "endpoints": {
            "list": "/api/v1/eventstreammonitor/users/1000",  # GET endpoint
            "health": "/health"
        },
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Host": "localhost:5001"
        }
    },
    "taskprocessing": {
        "url": "http://localhost:5002",
        "endpoints": {
            "list": "/api/v1/eventstreammonitor/tasks",  # GET endpoint
            "health": "/health"
        },
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    },
    "notification": {
        "url": "http://localhost:5003",
        "endpoints": {
            "health": "/health"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    },
    "logmonitor": {
        "url": "http://localhost:5004",
        "endpoints": {
            "stats": "/api/v1/logs/stats",
            "errors": "/api/v1/logs/errors?limit=10"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    }
}


class LoadTestResult:
    """Results from a single request"""
    def __init__(self, service: str, endpoint: str, status_code: int, 
                 response_time: float, success: bool, error: str = None):
        self.service = service
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_time = response_time
        self.success = success
        self.error = error
        self.timestamp = datetime.now()


def make_request(service_name: str, service_config: Dict, endpoint: str) -> LoadTestResult:
    """
    Make a single HTTP request and measure response time

    Returns:
        LoadTestResult object
    """
    url = f"{service_config['url']}{endpoint}"
    headers = service_config.get('headers', {})

    start_time = time.time()
    try:
        if endpoint in ['/health', '/api/v1/logs/stats', '/api/v1/logs/errors?limit=10']:
            response = requests.get(url, headers=headers, timeout=10)
        else:
            # GET request for list endpoints
            response = requests.get(url, headers=headers, timeout=10)

        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        success = response.status_code in [200, 201, 404]  # 404 is OK for missing resources
        error = None if success else f"HTTP {response.status_code}"

        return LoadTestResult(
            service=service_name,
            endpoint=endpoint,
            status_code=response.status_code,
            response_time=response_time,
            success=success,
            error=error
        )
    except requests.exceptions.Timeout:
        return LoadTestResult(
            service=service_name,
            endpoint=endpoint,
            status_code=0,
            response_time=(time.time() - start_time) * 1000,
            success=False,
            error="Timeout"
        )
    except Exception as e:
        return LoadTestResult(
            service=service_name,
            endpoint=endpoint,
            status_code=0,
            response_time=(time.time() - start_time) * 1000,
            success=False,
            error=str(e)
        )


def run_load_test_cycle(concurrent_requests: int = 20) -> Dict[str, List[LoadTestResult]]:
    """
    Run a single cycle of load tests across all services

    Args:
        concurrent_requests: Number of concurrent requests per endpoint

    Returns:
        Dictionary of results by service
    """
    all_results = {service: [] for service in SERVICES.keys()}

    with ThreadPoolExecutor(max_workers=concurrent_requests * 4) as executor:
        futures = []

        # Submit requests for all services and endpoints
        for service_name, service_config in SERVICES.items():
            for endpoint_name, endpoint_path in service_config['endpoints'].items():
                for _ in range(concurrent_requests):
                    future = executor.submit(
                        make_request, 
                        service_name, 
                        service_config, 
                        endpoint_path
                    )
                    futures.append(future)

        # Collect results
        for future in as_completed(futures):
            result = future.result()
            all_results[result.service].append(result)

    return all_results


def calculate_stats(results: List[LoadTestResult]) -> Dict:
    """Calculate statistics for a list of results"""
    if not results:
        return {
            "total": 0,
            "success": 0,
            "failed": 0,
            "success_rate": 0.0,
            "avg_response_time": 0.0,
            "min_response_time": 0.0,
            "max_response_time": 0.0,
            "p50": 0.0,
            "p95": 0.0,
            "p99": 0.0
        }

    response_times = [r.response_time for r in results]
    success_count = sum(1 for r in results if r.success)

    sorted_times = sorted(response_times)
    total = len(results)

    return {
        "total": total,
        "success": success_count,
        "failed": total - success_count,
        "success_rate": (success_count / total * 100) if total > 0 else 0.0,
        "avg_response_time": statistics.mean(response_times),
        "min_response_time": min(response_times),
        "max_response_time": max(response_times),
        "p50": statistics.median(sorted_times),
        "p95": sorted_times[int(len(sorted_times) * 0.95)] if len(sorted_times) > 0 else 0.0,
        "p99": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 0 else 0.0
    }


def format_time(seconds: float) -> str:
    """Format seconds into readable time string"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    """Main load test runner"""
    # Parse command line arguments
    duration_hours = 1.0
    concurrent_requests = 20
    report_interval = 60  # Report every 60 seconds

    if len(sys.argv) > 1:
        duration_hours = float(sys.argv[1])
    if len(sys.argv) > 2:
        concurrent_requests = int(sys.argv[2])
    if len(sys.argv) > 3:
        report_interval = int(sys.argv[3])

    duration_seconds = duration_hours * 3600
    end_time = datetime.now() + timedelta(seconds=duration_seconds)

    print("=" * 80)
    print("LONG DURATION LOAD TEST")
    print("=" * 80)
    print(f"Duration: {duration_hours} hour(s)")
    print(f"Concurrent requests per endpoint: {concurrent_requests}")
    print(f"Report interval: {report_interval} seconds")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    # Accumulate all results
    cumulative_results = {service: [] for service in SERVICES.keys()}
    cycle_count = 0
    last_report_time = time.time()
    start_time = time.time()

    try:
        while datetime.now() < end_time:
            cycle_count += 1
            elapsed = time.time() - start_time

            # Run a cycle of load tests
            cycle_results = run_load_test_cycle(concurrent_requests)

            # Accumulate results
            for service, results in cycle_results.items():
                cumulative_results[service].extend(results)

            # Periodic reporting
            if time.time() - last_report_time >= report_interval:
                elapsed_time = time.time() - start_time
                remaining_time = duration_seconds - elapsed_time

                print(f"\n[{format_time(elapsed)}] Cycle {cycle_count} - Progress Report")
                print("-" * 80)

                total_requests = 0
                total_success = 0

                for service_name in SERVICES.keys():
                    if cumulative_results[service_name]:
                        stats = calculate_stats(cumulative_results[service_name])
                        total_requests += stats['total']
                        total_success += stats['success']

                        print(f"\n{service_name.upper()}:")
                        print(f"  Total Requests: {stats['total']}")
                        print(f"  Success Rate: {stats['success_rate']:.2f}% ({stats['success']}/{stats['total']})")
                        print(f"  Avg Response Time: {stats['avg_response_time']:.2f}ms")
                        print(f"  p50: {stats['p50']:.2f}ms | p95: {stats['p95']:.2f}ms | p99: {stats['p99']:.2f}ms")

                print(f"\nOVERALL:")
                print(f"  Total Requests: {total_requests}")
                print(f"  Success Rate: {(total_success/total_requests*100) if total_requests > 0 else 0:.2f}%")
                print(f"  Elapsed: {format_time(elapsed)} | Remaining: {format_time(remaining_time)}")
                print("=" * 80)

                last_report_time = time.time()

            # Small delay between cycles to avoid overwhelming
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nLoad test interrupted by user")

    # Final summary
    elapsed_time = time.time() - start_time
    print("\n\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total Duration: {format_time(elapsed_time)}")
    print(f"Total Cycles: {cycle_count}")
    print()

    total_requests = 0
    total_success = 0

    for service_name in SERVICES.keys():
        if cumulative_results[service_name]:
            stats = calculate_stats(cumulative_results[service_name])
            total_requests += stats['total']
            total_success += stats['success']

            print(f"{service_name.upper()}:")
            print(f"  Total Requests: {stats['total']}")
            print(f"  Successful: {stats['success']} | Failed: {stats['failed']}")
            print(f"  Success Rate: {stats['success_rate']:.2f}%")
            print(f"  Response Times (ms):")
            print(f"    Avg: {stats['avg_response_time']:.2f}")
            print(f"    Min: {stats['min_response_time']:.2f} | Max: {stats['max_response_time']:.2f}")
            print(f"    p50: {stats['p50']:.2f} | p95: {stats['p95']:.2f} | p99: {stats['p99']:.2f}")

            # Calculate throughput
            throughput = stats['total'] / elapsed_time if elapsed_time > 0 else 0
            print(f"  Throughput: {throughput:.2f} req/sec")
            print()

    print("=" * 80)
    print(f"OVERALL STATISTICS:")
    print(f"  Total Requests: {total_requests}")
    print(f"  Successful: {total_success} | Failed: {total_requests - total_success}")
    print(f"  Overall Success Rate: {(total_success/total_requests*100) if total_requests > 0 else 0:.2f}%")
    print(f"  Overall Throughput: {(total_requests/elapsed_time) if elapsed_time > 0 else 0:.2f} req/sec")
    print("=" * 80)

    # Save results to file
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    os.makedirs(results_dir, exist_ok=True)
    results_file = os.path.join(results_dir, f"long_load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    results_data = {
        "test_duration_seconds": elapsed_time,
        "total_cycles": cycle_count,
        "services": {}
    }

    for service_name in SERVICES.keys():
        if cumulative_results[service_name]:
            results_data["services"][service_name] = calculate_stats(cumulative_results[service_name])

    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"\nResults saved to: {results_file}")

if __name__ == "__main__":
    main()
