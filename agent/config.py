"""
Agent configuration file
"""
import os
from dotenv import load_dotenv
import socket

load_dotenv()

class Config:
    # Agent identification
    AGENT_ID = os.getenv('AGENT_ID', socket.gethostname())
    AGENT_NAME = os.getenv('AGENT_NAME', socket.gethostname())
    
    # Server configuration
    SERVER_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
    API_ENDPOINT = f"{SERVER_URL}/api/v1/metrics"
    
    # Data collection configuration
    COLLECTION_INTERVAL = int(os.getenv('COLLECTION_INTERVAL', 60))  # seconds
    
    # Network check targets
    NETWORK_TARGETS = [
        {'type': 'host', 'target': '8.8.8.8', 'port': 53},  # Google DNS
        {'type': 'url', 'target': 'https://www.google.com'}
    ]
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
