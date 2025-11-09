"""
Network connectivity checker module
Checks host reachability and URL availability
"""
import socket
import time
import requests

class NetworkCollector:
    """Network connectivity checker"""
    
    @staticmethod
    def check_host(host, port=80, timeout=3):
        """Check if a host is reachable"""
        try:
            start_time = time.time()
            socket.create_connection((host, port), timeout=timeout)
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            return {
                'host': host,
                'port': port,
                'status': 'up',
                'latency_ms': round(latency, 2)
            }
        except Exception as e:
            return {
                'host': host,
                'port': port,
                'status': 'down',
                'error': str(e)
            }
    
    @staticmethod
    def check_url(url, timeout=5):
        """Check if a URL is accessible"""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=timeout)
            latency = (time.time() - start_time) * 1000
            
            return {
                'url': url,
                'status_code': response.status_code,
                'status': 'up' if response.status_code == 200 else 'degraded',
                'latency_ms': round(latency, 2)
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'down',
                'error': str(e)
            }
    
    @staticmethod
    def collect_all(targets=None):
        """Collect all network check results"""
        if targets is None:
            # Default check targets
            targets = [
                {'type': 'host', 'target': 'google.com', 'port': 80},
                {'type': 'url', 'target': 'https://www.google.com'}
            ]
        
        results = []
        for target in targets:
            if target['type'] == 'host':
                result = NetworkCollector.check_host(
                    target['target'], 
                    target.get('port', 80)
                )
            elif target['type'] == 'url':
                result = NetworkCollector.check_url(target['target'])
            results.append(result)
        
        return results

# Test code
if __name__ == '__main__':
    collector = NetworkCollector()
    results = collector.collect_all()
    
    print("\n=== Network Check Results ===")
    for result in results:
        print(result)
    print("=" * 50)
