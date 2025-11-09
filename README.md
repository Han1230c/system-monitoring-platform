# System Monitoring & Alerting Platform

A distributed system monitoring solution built with Python, Flask, and SQLite. Collects real-time metrics from multiple servers and provides centralized monitoring through a web dashboard.

## Features

- **Real-time Monitoring**: Collect CPU, memory, disk, and network metrics every 60 seconds
- **Distributed Architecture**: Lightweight agents report to central server
- **RESTful API**: Clean API design for data collection and retrieval
- **Data Persistence**: SQLite database with optimized schema
- **Automatic Failover**: Agents retry failed connections with exponential backoff

## Architecture
```
┌─────────────────┐
│  Web Dashboard  │  (Coming Soon)
└────────┬────────┘
         │
         ↓
┌────────────────────┐
│   Flask API Server │
│   - Receive metrics │
│   - Store data      │
│   - Query API       │
└────────┬───────────┘
         │
         ↓
┌─────────────────┐
│ SQLite Database │
└─────────────────┘
         ↑
         │
    ┌────┴────┬────────┐
    │         │        │
┌───▼──┐  ┌──▼───┐ ┌──▼───┐
│Agent1│  │Agent2│ │Agent3│
└──────┘  └──────┘ └──────┘
```

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Han1230c/system-monitoring-platform.git
cd system-monitoring-platform
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
# Install agent dependencies
cd agent
pip install -r requirements.txt

# Install server dependencies
cd ../server
pip install -r requirements.txt
```

### 4. Start the Server
```bash
cd server
export PORT=5001  # Optional: change port if 5000 is in use
python app.py
```

Server will start on `http://localhost:5001`

### 5. Run the Agent

In a new terminal:
```bash
cd agent
source ../venv/bin/activate
python agent.py
```

The agent will start collecting and sending metrics every 60 seconds.

## Configuration

### Agent Configuration

Edit `agent/.env`:
```bash
AGENT_ID=agent-001
AGENT_NAME=Production-Server-01
SERVER_URL=http://localhost:5001
COLLECTION_INTERVAL=60
```

### Server Configuration

Edit `server/.env`:
```bash
SECRET_KEY=your-secret-key
PORT=5001
FLASK_ENV=development
```

## API Endpoints

### POST /api/v1/metrics
Submit metrics from agent

**Request Body:**
```json
{
  "agent_id": "agent-001",
  "agent_name": "Production-Server-01",
  "timestamp": "2024-11-09T20:18:47.029778+00:00",
  "system": {
    "cpu_percent": 13.3,
    "memory": {
      "percent": 69.9
    },
    "disk": {
      "percent": 8.1
    }
  },
  "network": [...]
}
```

### GET /api/v1/agents
List all registered agents

### GET /api/v1/metrics/{agent_id}/latest
Get latest metrics for specific agent

## Project Structure
```
system-monitoring-platform/
├── agent/                  # Monitoring agent
│   ├── collectors/        # Data collection modules
│   │   ├── system.py     # CPU/memory/disk metrics
│   │   └── network.py    # Network connectivity checks
│   ├── agent.py          # Main agent program
│   ├── config.py         # Agent configuration
│   └── requirements.txt
│
├── server/                # Flask API server
│   ├── app.py            # Main Flask application
│   ├── models.py         # Database models
│   ├── config.py         # Server configuration
│   └── requirements.txt
│
├── database/             # Database schema
│   └── init.sql          # SQL initialization script
│
└── README.md
```

## Technology Stack

- **Backend**: Python, Flask
- **Database**: SQLite (development), PostgreSQL ready
- **Agent Libraries**: psutil, requests
- **API**: RESTful with JSON

## Development Status

✅ Agent data collection  
✅ Flask API server  
✅ Database integration  
✅ Real-time data flow  
🚧 Web dashboard (in progress)  
🚧 Alert system (planned)  
🚧 Docker deployment (planned)  

## Metrics Collected

- **System Metrics**
  - CPU usage percentage
  - Memory usage (total, used, available, percent)
  - Disk usage (total, used, free, percent)

- **Network Checks**
  - Host reachability
  - Latency measurements
  - Connection status

## License

MIT License
