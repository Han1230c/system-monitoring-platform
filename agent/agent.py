"""
Monitoring Agent main program
Periodically collects system metrics and sends to central server
"""
import time
import requests
import logging
from datetime import datetime, timezone
from config import Config
from collectors.system import SystemCollector
from collectors.network import NetworkCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoringAgent:
    """Monitoring Agent main class"""
    
    def __init__(self):
        self.agent_id = Config.AGENT_ID
        self.agent_name = Config.AGENT_NAME
        self.server_url = Config.API_ENDPOINT
        self.interval = Config.COLLECTION_INTERVAL
        
        logger.info(f"Agent initialized: {self.agent_name} (ID: {self.agent_id})")
        logger.info(f"Server URL: {self.server_url}")
        logger.info(f"Collection interval: {self.interval}s")
    
    def collect_metrics(self):
        """Collect all metrics"""
        try:
            # Collect system metrics
            system_metrics = SystemCollector.collect_all()
            
            # Collect network metrics
            network_metrics = NetworkCollector.collect_all(Config.NETWORK_TARGETS)
            
            # Assemble data
            data = {
                'agent_id': self.agent_id,
                'agent_name': self.agent_name,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'system': system_metrics,
                'network': network_metrics
            }
            
            logger.info(f"Metrics collected - CPU: {system_metrics['cpu_percent']}%, "
                       f"Memory: {system_metrics['memory']['percent']}%, "
                       f"Disk: {system_metrics['disk']['percent']}%")
            
            return data
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None
    
    def send_metrics(self, data):
        """Send metrics to server"""
        if data is None:
            return False
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                response = requests.post(
                    self.server_url,
                    json=data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info("Metrics sent successfully")
                    return True
                else:
                    logger.warning(f"Server returned status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection failed (attempt {attempt + 1}/{Config.MAX_RETRIES})")
                if attempt < Config.MAX_RETRIES - 1:
                    time.sleep(Config.RETRY_DELAY)
            except Exception as e:
                logger.error(f"Error sending metrics: {e}")
                break
        
        logger.error("Failed to send metrics after all retries")
        return False
    
    def run_local_test(self, iterations=3):
        """Local test mode - collect data but don't send"""
        logger.info("Running in LOCAL TEST mode")
        
        for i in range(iterations):
            print(f"\n{'='*60}")
            print(f"Collection #{i+1}/{iterations}")
            print('='*60)
            
            metrics = self.collect_metrics()
            
            if metrics:
                print(f"\nAgent: {metrics['agent_name']} ({metrics['agent_id']})")
                print(f"Time: {metrics['timestamp']}")
                print(f"\nSystem Metrics:")
                print(f"  CPU: {metrics['system']['cpu_percent']}%")
                print(f"  Memory: {metrics['system']['memory']['percent']}%")
                print(f"  Disk: {metrics['system']['disk']['percent']}%")
                print(f"\nNetwork Checks:")
                for check in metrics['network']:
                    status = check.get('status', 'unknown')
                    if 'host' in check:
                        print(f"  {check['host']}:{check['port']} - {status} ({check.get('latency_ms', 'N/A')}ms)")
                    elif 'url' in check:
                        print(f"  {check['url']} - {status} ({check.get('latency_ms', 'N/A')}ms)")
            
            if i < iterations - 1:
                print(f"\nWaiting {self.interval} seconds...")
                time.sleep(self.interval)
        
        print(f"\n{'='*60}")
        print("Local test completed!")
        print('='*60)
    
    def run(self):
        """Main run loop"""
        logger.info("Agent started, collecting metrics...")
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Send to server
                self.send_metrics(metrics)
                
                # Wait for next collection
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(self.interval)

if __name__ == '__main__':
    import sys
    
    agent = MonitoringAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Local test mode
        agent.run_local_test(iterations=3)
    else:
        # Normal mode (will try to send to server)
        agent.run()
