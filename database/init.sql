-- System Monitoring Platform Database Schema

-- Table: agents (store agent information)
CREATE TABLE IF NOT EXISTS agents (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: system_metrics (store system metrics)
CREATE TABLE IF NOT EXISTS system_metrics (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    cpu_percent FLOAT,
    memory_total BIGINT,
    memory_used BIGINT,
    memory_percent FLOAT,
    disk_total BIGINT,
    disk_used BIGINT,
    disk_percent FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- Table: network_checks (store network check results)
CREATE TABLE IF NOT EXISTS network_checks (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    target VARCHAR(500) NOT NULL,
    check_type VARCHAR(20),
    status VARCHAR(20),
    latency_ms FLOAT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- Table: alerts (store alert records)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50),
    severity VARCHAR(20),
    message TEXT,
    threshold_value FLOAT,
    actual_value FLOAT,
    status VARCHAR(20) DEFAULT 'active',
    triggered_at TIMESTAMP NOT NULL,
    resolved_at TIMESTAMP,
    notified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_system_metrics_agent_time 
    ON system_metrics(agent_id, timestamp);
    
CREATE INDEX IF NOT EXISTS idx_network_checks_agent_time 
    ON network_checks(agent_id, timestamp);
    
CREATE INDEX IF NOT EXISTS idx_alerts_agent_status 
    ON alerts(agent_id, status);

-- Insert sample data for testing (optional)
INSERT INTO agents (agent_id, agent_name, status, last_seen)
VALUES ('test-agent', 'Test Agent', 'active', CURRENT_TIMESTAMP)
ON CONFLICT (agent_id) DO NOTHING;
