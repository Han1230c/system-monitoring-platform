/**
 * Charts JavaScript
 * Handles data visualization with Chart.js
 */

class MetricsCharts {
    constructor() {
        this.charts = {};
        this.colors = {
            cpu: 'rgb(59, 130, 246)',      // Blue
            memory: 'rgb(16, 185, 129)',   // Green
            disk: 'rgb(245, 158, 11)'      // Orange
        };
    }

    async loadHistoricalData(agentId, hours = 24) {
        try {
            const response = await fetch(`/api/v1/metrics/${agentId}?hours=${hours}`);
            const data = await response.json();
            return data.metrics;
        } catch (error) {
            console.error('Error loading historical data:', error);
            return [];
        }
    }

    createChart(canvasId, agentId, metricType, label) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: label,
                    data: [],
                    borderColor: this.colors[metricType],
                    backgroundColor: this.colors[metricType] + '20',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    },
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    async updateChart(canvasId, agentId, metricType, hours = 24) {
        const metrics = await this.loadHistoricalData(agentId, hours);
        
        if (!metrics || metrics.length === 0) {
            console.log('No metrics data available');
            return;
        }

        const chart = this.charts[canvasId];
        if (!chart) return;

        // Prepare data
        const labels = metrics.map(m => {
            const date = new Date(m.timestamp);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        });

        let data;
        if (metricType === 'cpu') {
            data = metrics.map(m => m.cpu_percent);
        } else if (metricType === 'memory') {
            data = metrics.map(m => m.memory_percent);
        } else if (metricType === 'disk') {
            data = metrics.map(m => m.disk_percent);
        }

        // Update chart
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }
}

// Global instance
const metricsCharts = new MetricsCharts();
