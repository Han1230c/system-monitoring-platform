"""
Database models
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Agent(db.Model):
    """Agent information model"""
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), unique=True, nullable=False)
    agent_name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='active')
    last_seen = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }

class SystemMetric(db.Model):
    """System metrics model"""
    __tablename__ = 'system_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), db.ForeignKey('agents.agent_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    cpu_percent = db.Column(db.Float)
    memory_total = db.Column(db.BigInteger)
    memory_used = db.Column(db.BigInteger)
    memory_percent = db.Column(db.Float)
    disk_total = db.Column(db.BigInteger)
    disk_used = db.Column(db.BigInteger)
    disk_percent = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_percent': self.disk_percent
        }

class NetworkCheck(db.Model):
    """Network check results model"""
    __tablename__ = 'network_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), db.ForeignKey('agents.agent_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    target = db.Column(db.String(500), nullable=False)
    check_type = db.Column(db.String(20))
    status = db.Column(db.String(20))
    latency_ms = db.Column(db.Float)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Alert(db.Model):
    """Alert records model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(100), db.ForeignKey('agents.agent_id'), nullable=False)
    alert_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    message = db.Column(db.Text)
    threshold_value = db.Column(db.Float)
    actual_value = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    triggered_at = db.Column(db.DateTime, nullable=False)
    resolved_at = db.Column(db.DateTime)
    notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
