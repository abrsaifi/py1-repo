"""Load testing script for DocPro"""
import asyncio
import aiohttp
import time
import csv
from pathlib import Path
import random
import statistics

class LoadTester:
    """Load test DocPro API"""
    
    def __init__(self, base_url='http://localhost:5000', num_concurrent=10, num_requests=100):
        self.base_url = base_url
        self.num_concurrent = num_concurrent
        self.num_requests = num_requests
        self.results = []
        self.errors = []
    
    async def test_endpoint(self, session, method, endpoint, data=None, files=None):
        """Test a single endpoint"""
        start = time.time()
        try:
            if method == 'GET':
                async with session.get(f'{self.base_url}{endpoint}') as resp:
                    duration = time.time() - start
                    return {
                        'endpoint': endpoint,
                        'method': method,
                        'status': resp.status,
                        'duration_ms': duration * 1000,
                        'success': resp.status < 400
                    }
            elif method == 'POST':
                async with session.post(f'{self.base_url}{endpoint}', json=data) as resp:
                    duration = time.time() - start
                    return {
                        'endpoint': endpoint,
                        'method': method,
                        'status': resp.status,
                        'duration_ms': duration * 1000,
                        'success': resp.status < 400
                    }
        except Exception as e:
            duration = time.time() - start
            return {
                'endpoint': endpoint,
                'method': method,
                'status': 0,
                'duration_ms': duration * 1000,
                'success': False,
                'error': str(e)
            }
    
    async def run_concurrent_tests(self, endpoint, method='GET', data=None, count=None):
        """Run concurrent requests"""
        if count is None:
            count = self.num_requests
        
        connector = aiohttp.TCPConnector(limit=self.num_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                self.test_endpoint(session, method, endpoint, data)
                for _ in range(count)
            ]
            
            results = await asyncio.gather(*tasks)
            return results
    
    def test_analytics_endpoint(self):
        """Test analytics endpoint under load"""
        print("\n📊 Testing Analytics Endpoint...")
        results = asyncio.run(self.run_concurrent_tests('/api/analytics/summary', 'GET'))
        return self._process_results(results)
    
    def test_duplicate_remover(self):
        """Test duplicate remover endpoint under load"""
        print("\n🔄 Testing Duplicate Remover Endpoint...")
        data = {'sample': 'data'}
        results = asyncio.run(self.run_concurrent_tests(
            '/api/data/duplicate-remover', 'POST', data, count=20
        ))
        return self._process_results(results)
    
    def test_data_validator(self):
        """Test data validator endpoint under load"""
        print("\n✅ Testing Data Validator Endpoint...")
        data = {'sample': 'data'}
        results = asyncio.run(self.run_concurrent_tests(
            '/api/data/validate', 'POST', data, count=20
        ))
        return self._process_results(results)
    
    def test_advanced_features(self):
        """Test advanced features endpoints"""
        print("\n🚀 Testing Advanced Features...")
        results = asyncio.run(self.run_concurrent_tests(
            '/api/features/cache/stats', 'GET', count=50
        ))
        return self._process_results(results)
    
    def _process_results(self, results):
        """Process and display results"""
        durations = [r['duration_ms'] for r in results]
        success_count = sum(1 for r in results if r['success'])
        
        stats = {
            'total': len(results),
            'success': success_count,
            'failed': len(results) - success_count,
            'min_ms': min(durations),
            'max_ms': max(durations),
            'avg_ms': statistics.mean(durations),
            'median_ms': statistics.median(durations),
            'p95_ms': sorted(durations)[int(len(durations) * 0.95)],
            'p99_ms': sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 100 else None,
            'success_rate': (success_count / len(results)) * 100
        }
        
        print(f"  Total Requests: {stats['total']}")
        print(f"  Success: {stats['success']} ({stats['success_rate']:.1f}%)")
        print(f"  Failed: {stats['failed']}")
        print(f"  Response Times:")
        print(f"    Min: {stats['min_ms']:.2f}ms")
        print(f"    Max: {stats['max_ms']:.2f}ms")
        print(f"    Avg: {stats['avg_ms']:.2f}ms")
        print(f"    Median: {stats['median_ms']:.2f}ms")
        print(f"    P95: {stats['p95_ms']:.2f}ms")
        if stats['p99_ms']:
            print(f"    P99: {stats['p99_ms']:.2f}ms")
        
        return stats
    
    def run_all_tests(self):
        """Run all load tests"""
        print("=" * 60)
        print("🚀 DocPro Load Testing Suite")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Concurrent: {self.num_concurrent}")
        print(f"Total Requests: {self.num_requests}")
        
        all_stats = {}
        
        try:
            all_stats['analytics'] = self.test_analytics_endpoint()
            all_stats['validator'] = self.test_data_validator()
            all_stats['advanced'] = self.test_advanced_features()
            
            print("\n" + "=" * 60)
            print("📊 Summary")
            print("=" * 60)
            
            for endpoint, stats in all_stats.items():
                print(f"\n{endpoint}:")
                print(f"  Success Rate: {stats['success_rate']:.1f}%")
                print(f"  Avg Response: {stats['avg_ms']:.2f}ms")
            
            return all_stats
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

# Usage
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Load test DocPro API')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL')
    parser.add_argument('--concurrent', type=int, default=10, help='Concurrent requests')
    parser.add_argument('--requests', type=int, default=100, help='Total requests per test')
    
    args = parser.parse_args()
    
    tester = LoadTester(args.url, args.concurrent, args.requests)
    tester.run_all_tests()
