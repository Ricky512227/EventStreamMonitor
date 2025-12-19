#!/usr/bin/env python3
"""
Load Testing Script for All Services
Tests concurrent performance with Gunicorn workers
"""
import requests
import time
import json
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Tuple
from datetime import datetime


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


def make_request(service_name: str, service_config: Dict, endpoint: str, 
                 request_num: int) -> LoadTestResult:
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
        response_time = (time.time() - start_time) * 1000
        return LoadTestResult(
            service=service_name,
            endpoint=endpoint,
            status_code=0,
            response_time=response_time,
            success=False,
            error="Timeout"
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return LoadTestResult(
            service=service_name,
            endpoint=endpoint,
            status_code=0,
            response_time=response_time,
            success=False,
            error=str(e)[:50]
        )


def run_load_test(service_name: str, service_config: Dict, endpoint: str,
                  num_requests: int, concurrent_requests: int) -> List[LoadTestResult]:
    """
    Run load test for a service endpoint
    
    Args:
        service_name: Name of the service
        service_config: Service configuration dict
        endpoint: Endpoint to test
        num_requests: Total number of requests
        concurrent_requests: Number of concurrent requests
    
    Returns:
        List of LoadTestResult objects
    """
    results = []
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        # Submit all requests
        futures = [
            executor.submit(make_request, service_name, service_config, endpoint, i)
            for i in range(num_requests)
        ]
        
        # Collect results as they complete
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"Error getting result: {e}")
    
    return results


def calculate_statistics(results: List[LoadTestResult]) -> Dict:
    """Calculate statistics from results"""
    if not results:
        return {}
    
    response_times = [r.response_time for r in results]
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    status_codes = {}
    for r in results:
        status_codes[r.status_code] = status_codes.get(r.status_code, 0) + 1
    
    stats = {
        "total_requests": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": (len(successful) / len(results)) * 100 if results else 0,
        "response_times": {
            "min": min(response_times),
            "max": max(response_times),
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
        },
        "status_codes": status_codes
    }
    
    # Calculate percentiles if we have enough data
    if len(response_times) >= 10:
        sorted_times = sorted(response_times)
        stats["response_times"]["p95"] = sorted_times[int(len(sorted_times) * 0.95)]
        stats["response_times"]["p99"] = sorted_times[int(len(sorted_times) * 0.99)]
    
    return stats


def print_results(service_name: str, endpoint: str, stats: Dict):
    """Print formatted test results"""
    print(f"\n{'='*70}")
    print(f"Service: {service_name.upper()} | Endpoint: {endpoint}")
    print(f"{'='*70}")
    print(f"Total Requests:     {stats['total_requests']}")
    print(f"Successful:         {stats['successful']} ({stats['success_rate']:.1f}%)")
    print(f"Failed:             {stats['failed']}")
    
    rt = stats['response_times']
    print(f"\nResponse Times (ms):")
    print(f"  Min:              {rt['min']:.2f}")
    print(f"  Max:              {rt['max']:.2f}")
    print(f"  Mean:             {rt['mean']:.2f}")
    print(f"  Median:           {rt['median']:.2f}")
    if 'p95' in rt:
        print(f"  p95:              {rt['p95']:.2f}")
    if 'p99' in rt:
        print(f"  p99:              {rt['p99']:.2f}")
    
    print(f"\nStatus Codes:")
    for code, count in stats['status_codes'].items():
        print(f"  {code}: {count}")


def test_all_services(num_requests: int = 100, concurrent: int = 10):
    """Test all services with load"""
    print("\n" + "="*70)
    print("LOAD TESTING ALL SERVICES")
    print(f"Total Requests per Endpoint: {num_requests}")
    print(f"Concurrent Requests: {concurrent}")
    print(f"Target: Testing Gunicorn multi-worker performance")
    print("="*70)
    
    all_results = {}
    
    # Test each service
    for service_name, service_config in SERVICES.items():
        print(f"\n\nTesting {service_name}...")
        
        # Test each endpoint
        for endpoint_name, endpoint_path in service_config['endpoints'].items():
            print(f"\n  → Testing {endpoint_path}...")
            
            start_time = time.time()
            results = run_load_test(
                service_name, 
                service_config, 
                endpoint_path,
                num_requests, 
                concurrent
            )
            total_time = time.time() - start_time
            
            stats = calculate_statistics(results)
            stats['total_time'] = total_time
            stats['requests_per_second'] = num_requests / total_time if total_time > 0 else 0
            
            all_results[f"{service_name}_{endpoint_name}"] = {
                'stats': stats,
                'results': results
            }
            
            print_results(service_name, endpoint_path, stats)
            print(f"  Total Time: {total_time:.2f}s")
            print(f"  Requests/sec: {stats['requests_per_second']:.2f}")
    
    # Summary
    print("\n\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    for key, data in all_results.items():
        service, endpoint = key.split('_', 1)
        stats = data['stats']
        print(f"\n{service}/{endpoint}:")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Avg Response: {stats['response_times']['mean']:.2f}ms")
        print(f"  Throughput: {stats['requests_per_second']:.2f} req/sec")


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    num_requests = 100
    concurrent = 10
    
    if len(sys.argv) > 1:
        num_requests = int(sys.argv[1])
    if len(sys.argv) > 2:
        concurrent = int(sys.argv[2])
    
    print(f"\nLoad Test Configuration:")
    print(f"  Requests per endpoint: {num_requests}")
    print(f"  Concurrent requests: {concurrent}")
    print(f"\nStarting in 3 seconds...")
    time.sleep(3)
    
    try:
        test_all_services(num_requests, concurrent)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()

