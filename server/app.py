"""
Flask API Server
Receives metrics from agents and provides API endpoints
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from config import Config
from models import db, Agent, SystemMetric, NetworkCheck

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'System Monitoring Platform API',
        'version': '1.0.0'
    })

@app.route('/api/v1/metrics', methods=['POST'])
def receive_metrics():
    """Receive metrics from agents"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Update or create agent
        agent = Agent.query.filter_by(agent_id=data['agent_id']).first()
        if not agent:
            agent = Agent(
                agent_id=data['agent_id'],
                agent_name=data['agent_name']
            )
            db.session.add(agent)
        
        agent.last_seen = datetime.now(timezone.utc)
        agent.status = 'active'
        agent.updated_at = datetime.now(timezone.utc)
        
        # Parse timestamp
        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        # Save system metrics
        system_data = data['system']
        metric = SystemMetric(
            agent_id=data['agent_id'],
            timestamp=timestamp,
            cpu_percent=system_data['cpu_percent'],
            memory_total=system_data['memory']['total'],
            memory_used=system_data['memory']['used'],
            memory_percent=system_data['memory']['percent'],
            disk_total=system_data['disk']['total'],
            disk_used=system_data['disk']['used'],
            disk_percent=system_data['disk']['percent']
        )
        db.session.add(metric)
        
        # Save network checks
        for check in data['network']:
            net_check = NetworkCheck(
                agent_id=data['agent_id'],
                timestamp=timestamp,
                target=check.get('host') or check.get('url'),
                check_type='host' if 'host' in check else 'url',
                status=check['status'],
                latency_ms=check.get('latency_ms'),
                error_message=check.get('error')
            )
            db.session.add(net_check)
        
        db.session.commit()
        
        app.logger.info(f"Metrics received from {data['agent_name']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Metrics received',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error receiving metrics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/agents', methods=['GET'])
def get_agents():
    """Get list of all agents"""
    try:
        agents = Agent.query.all()
        return jsonify({
            'agents': [agent.to_dict() for agent in agents]
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/metrics/<agent_id>/latest', methods=['GET'])
def get_latest_metrics(agent_id):
    """Get latest metrics for an agent"""
    try:
        metric = SystemMetric.query.filter_by(agent_id=agent_id)\
            .order_by(SystemMetric.timestamp.desc()).first()
        
        if not metric:
            return jsonify({
                'status': 'error',
                'message': 'No metrics found'
            }), 404
        
        return jsonify(metric.to_dict())
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
