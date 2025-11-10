# System Monitoring & Alerting Platform

A distributed system monitoring solution built with Python, Flask, and SQLite. Collects real-time metrics from multiple servers and provides centralized monitoring through a web dashboard.

## 🚀 Live Demo

**Live Application:** [https://system-monitoring-platform.onrender.com](https://system-monitoring-platform.onrender.com)

*Note: The free tier may take 50 seconds to wake up on first visit.*

## ✨ Features

- **Real-time Monitoring**: Collect CPU, memory, disk, and network metrics every 60 seconds
- **Distributed Architecture**: Lightweight agents report to central server
- **Data Visualization**: Interactive charts with Chart.js showing historical trends
- **RESTful API**: Clean API design for data collection and retrieval
- **Responsive Dashboard**: Bootstrap-based UI that works on all devices
- **Time Range Selection**: View metrics across 1 hour, 6 hours, 24 hours, or 7 days
- **Automatic Failover**: Agents retry failed connections with exponential backoff

## 🏗️ Architecture
```
┌─────────────────┐
│  Web Dashboard  │  https://system-monitoring-platform.onrender.com
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

## 🚀 Quick Start

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
pip install -r requirements.txt
```

### 4. Start the Server (Local)
```bash
cd server
export PORT=5001
python app.py
```

Server will start on `http://localhost:5001`

### 5. Run the Agent (Local)

In a new terminal:
```bash
cd agent
source ../venv/bin/activate
python agent.py
```

The agent will start collecting and sending metrics every 60 seconds.

## ⚙️ Configuration

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

## 📡 API Endpoints

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
    "memory": { "percent": 69.9 },
    "disk": { "percent": 8.1 }
  },
  "network": [...]
}
```

### GET /api/v1/agents
List all registered agents

### GET /api/v1/metrics/{agent_id}/latest
Get latest metrics for specific agent

### GET /api/v1/metrics/{agent_id}?hours=24
Get historical metrics for specific agent

## 📁 Project Structure
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
├── webapp/               # Web frontend
│   ├── static/
│   │   ├── css/         # Custom styles
│   │   └── js/          # Dashboard & charts logic
│   └── templates/       # HTML templates
│
├── database/             # Database schema
│   └── init.sql         # SQL initialization script
│
├── requirements.txt      # Python dependencies
├── start.sh             # Production start script
└── README.md
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Flask 3.0, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL ready
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **Visualization**: Chart.js 4.4
- **Agent Libraries**: psutil, requests
- **Deployment**: Gunicorn, Render.com
- **API**: RESTful with JSON

## 📊 Development Status

✅ Agent data collection  
✅ Flask API server  
✅ Database integration  
✅ Real-time data flow  
✅ Web dashboard  
✅ Data visualization (Chart.js)  
✅ Cloud deployment  
🚧 Alert system (planned)  
🚧 Docker deployment (planned)  

## 📈 Metrics Collected

- **System Metrics**
  - CPU usage percentage
  - Memory usage (total, used, available, percent)
  - Disk usage (total, used, free, percent)

- **Network Checks**
  - Host reachability
  - Latency measurements (ms)
  - Connection status

## 🚀 Deployment

The application is deployed on Render.com with automatic deployments from the master branch.

**Live URL:** [https://system-monitoring-platform.onrender.com](https://system-monitoring-platform.onrender.com)

### Deploy Your Own

1. Fork this repository
2. Sign up for [Render.com](https://render.com)
3. Create a new Web Service
4. Connect your forked repository
5. Render will automatically detect the configuration

## 📝 License

MIT License

## 🔗 Links

- **Live Demo**: [https://system-monitoring-platform.onrender.com](https://system-monitoring-platform.onrender.com)
- **GitHub**: [https://github.com/Han1230c/system-monitoring-platform](https://github.com/Han1230c/system-monitoring-platform)

---

**Built with ❤️ using Python, Flask, and Chart.js**
