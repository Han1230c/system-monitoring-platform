"""
System metrics collector module
Collects CPU, memory, and disk usage
"""
import psutil
from datetime import datetime, timezone

class SystemCollector:
    """Collect system resource metrics"""
    
    @staticmethod
    def get_cpu_usage():
        """Get CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    @staticmethod
    def get_memory_usage():
        """Get memory usage information"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }
    
    @staticmethod
    def get_disk_usage():
        """Get disk usage information"""
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
    
    @staticmethod
    def collect_all():
        """Collect all system metrics"""
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cpu_percent': SystemCollector.get_cpu_usage(),
            'memory': SystemCollector.get_memory_usage(),
            'disk': SystemCollector.get_disk_usage()
        }

# Test code
if __name__ == '__main__':
    collector = SystemCollector()
    metrics = collector.collect_all()
    
    print("\n=== System Metrics ===")
    print(f"Timestamp: {metrics['timestamp']}")
    print(f"CPU: {metrics['cpu_percent']}%")
    print(f"Memory: {metrics['memory']['percent']}%")
    print(f"Disk: {metrics['disk']['percent']}%")
    print("=" * 40)
