import sys
import time
import requests
import json
import os
from collections import defaultdict

def run_benchmark(url, num_requests=50):
    times = []
    query_count = 0
    endpoint_name = url.split('/')[-1]

    print(f"Benchmarking {url} for {num_requests} requests...")
    for i in range(num_requests):
        start_time = time.perf_counter()
        response = requests.get(url)
        end_time = time.perf_counter()
        
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        times.append((end_time - start_time) * 1000) # Convert to ms
        
        # Get query count from the custom header
        if 'X-Query-Count' in response.headers:
            query_count = int(response.headers['X-Query-Count'])
        else:
            print("Warning: X-Query-Count header missing. Make sure DEBUG is True.")

    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"Results for {endpoint_name}:")
    print(f"  Queries Executed: {query_count}")
    print(f"  Average Time: {avg_time:.2f} ms")
    print(f"  Min Time: {min_time:.2f} ms")
    print(f"  Max Time: {max_time:.2f} ms")

    # Load existing submission.json or create empty
    results = {}
    if os.path.exists("submission.json"):
        with open("submission.json", "r") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = {}

    results[endpoint_name] = {
        "query_count": query_count,
        "avg_response_ms": avg_time,
        "min_response_ms": min_time,
        "max_response_ms": max_time
    }

    # Save to submission.json
    with open("submission.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <url>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    run_benchmark(target_url)
