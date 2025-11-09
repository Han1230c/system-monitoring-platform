/**
 * Dashboard JavaScript
 * Handles real-time data updates and UI interactions
 */

class Dashboard {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.apiBase = window.location.origin;
    }

    init() {
        console.log('Dashboard initialized');
        this.loadAgents();
        this.startAutoRefresh();
    }

    async loadAgents() {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/agents`);
            const data = await response.json();
            
            console.log('Loaded agents:', data);
            
            // Update summary cards
            this.updateSummary(data.agents);
            
            // Render agent table
            this.renderAgentTable(data.agents);
            
            // Load metrics for each agent
            for (const agent of data.agents) {
                await this.loadAgentMetrics(agent.agent_id);
            }
            
            // Update last refresh time
            this.updateLastRefreshTime();
            
        } catch (error) {
            console.error('Error loading agents:', error);
            this.showError('Failed to load agents');
        }
    }

    updateSummary(agents) {
        const totalAgents = agents.length;
        const activeAgents = agents.filter(a => a.status === 'active').length;
        
        document.getElementById('total-agents').textContent = totalAgents;
        document.getElementById('active-agents').textContent = activeAgents;
    }

    renderAgentTable(agents) {
        const tbody = document.getElementById('agents-table-body');
        
        if (agents.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No agents found</td></tr>';
            return;
        }
        
        tbody.innerHTML = agents.map(agent => `
            <tr data-agent-id="${agent.agent_id}">
                <td>
                    <span class="badge ${agent.status === 'active' ? 'bg-success' : 'bg-secondary'}">
                        ${agent.status}
                    </span>
                </td>
                <td><strong>${agent.agent_name}</strong></td>
                <td id="cpu-${agent.agent_id}">--</td>
                <td id="memory-${agent.agent_id}">--</td>
                <td id="disk-${agent.agent_id}">--</td>
                <td>${this.formatTime(agent.last_seen)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary">View</button>
                </td>
            </tr>
        `).join('');
    }

    async loadAgentMetrics(agentId) {
        try {
            const response = await fetch(`${this.apiBase}/api/v1/metrics/${agentId}/latest`);
            const data = await response.json();
            
            document.getElementById(`cpu-${agentId}`).innerHTML = 
                this.formatMetric(data.cpu_percent);
            document.getElementById(`memory-${agentId}`).innerHTML = 
                this.formatMetric(data.memory_percent);
            document.getElementById(`disk-${agentId}`).innerHTML = 
                this.formatMetric(data.disk_percent);
            
        } catch (error) {
            console.error(`Error loading metrics for ${agentId}:`, error);
        }
    }

    formatMetric(value) {
        const percent = value.toFixed(1);
        let badgeClass = 'bg-success';
        
        if (value >= 90) {
            badgeClass = 'bg-danger';
        } else if (value >= 80) {
            badgeClass = 'bg-warning';
        }
        
        return `<span class="badge ${badgeClass}">${percent}%</span>`;
    }

    formatTime(timestamp) {
        if (!timestamp) return 'Never';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffSecs = Math.floor((now - date) / 1000);
        
        if (diffSecs < 60) return `${diffSecs}s ago`;
        if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
        return date.toLocaleString();
    }

    updateLastRefreshTime() {
        const now = new Date();
        document.getElementById('last-update').textContent = now.toLocaleTimeString();
    }

    startAutoRefresh() {
        setInterval(() => {
            this.loadAgents();
        }, this.updateInterval);
    }

    showError(message) {
        const tbody = document.getElementById('agents-table-body');
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">${message}</td></tr>`;
    }
}

const dashboard = new Dashboard();
document.addEventListener('DOMContentLoaded', () => {
    dashboard.init();
});
