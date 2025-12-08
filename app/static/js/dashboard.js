// --- DASHBOARD LOGIC (Home Page) ---

async function fetchHabitats() {
    const container = document.getElementById('habitat-grid');
    if (!container) return; // Stop if not on home page

    try {
        const response = await fetch('/api/habitats');
        const habitats = await response.json();
        
        container.innerHTML = ''; 

        habitats.forEach(habitat => {
            const card = document.createElement('div');
            card.className = 'habitat-card';
            // Click to navigate to details
            card.onclick = () => window.location.href = `/habitat/${habitat.id}`;
            
            card.innerHTML = `
                <h3>${habitat.name}</h3>
                <div class="card-stats">
                    <p>🌡️ ${habitat.mean_temperature}°C</p>
                    <p>🦖 ${habitat.dinosaur_ids.length} Dinos</p>
                </div>
                <div class="status-indicator status-active">Active</div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error fetching habitats:', error);
    }
}

async function fetchAlertsTicker() {
    const container = document.getElementById('alerts-container');
    if (!container) return;

    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        container.innerHTML = '';
        // Filter only ALERTA lines
        const alerts = data.logs.filter(line => line.includes("ALERTA"));

        if (alerts.length === 0) {
            container.innerHTML = '<div class="alert-item" style="background:#2ecc71">No active alerts. System Normal.</div>';
            return;
        }

        // Show last 5 alerts
        alerts.slice(-5).reverse().forEach(alert => {
            const div = document.createElement('div');
            div.className = 'alert-item';
            
            if (alert.includes("critical")) div.classList.add('alert-critical');
            else if (alert.includes("high")) div.classList.add('alert-high');
            else div.classList.add('alert-low');

            // Clean timestamp for display
            div.textContent = alert.substring(20); // Skip the date part for cleaner look
            container.appendChild(div);
        });
    } catch (e) { console.error(e); }
}

// --- METRICS PAGE LOGIC ---

let chartInstance = null;

async function updateMetricsPage() {
    if (!window.isMetricsPage) return; // Only run on metrics.html

    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();

        // 1. Update Numbers
        document.getElementById('metric-uptime').innerText = data.uptime_seconds + 's';
        document.getElementById('metric-total').innerText = data.total_processed;
        document.getElementById('metric-alerts').innerText = data.total_alerts;
        document.getElementById('metric-tps').innerText = data.current_throughput_tps;

        // 2. Update Logs Viewer
        const logResponse = await fetch('/api/logs');
        const logData = await logResponse.json();
        const logViewer = document.getElementById('full-log-viewer');
        if (logViewer) {
            logViewer.innerText = logData.logs.join('');
            logViewer.scrollTop = logViewer.scrollHeight; // Auto scroll to bottom
        }

        // 3. Update Chart (Real-time Push)
        updateChart(data.current_throughput_tps);

    } catch (e) { console.error("Metrics error:", e); }
}

function initChart() {
    const ctx = document.getElementById('throughputChart');
    if (!ctx) return;

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], // Time labels
            datasets: [{
                label: 'Events per Second (Throughput)',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                tension: 0.4, // Smooth curves
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Disable animation for performance
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function updateChart(tpsValue) {
    if (!chartInstance) return;

    const now = new Date().toLocaleTimeString();

    // Add new data
    chartInstance.data.labels.push(now);
    chartInstance.data.datasets[0].data.push(tpsValue);

    // Keep only last 20 points
    if (chartInstance.data.labels.length > 20) {
        chartInstance.data.labels.shift();
        chartInstance.data.datasets[0].data.shift();
    }

    chartInstance.update();
}

// --- INITIALIZATION ---

// Initialize Chart if on metrics page
if (window.isMetricsPage) {
    initChart();
}

// Loop for updates
setInterval(() => {
    fetchHabitats();     // Home Page
    fetchAlertsTicker(); // Home Page
    updateMetricsPage(); // Metrics Page
}, 2000); // Update every 2 seconds

// Initial call
fetchHabitats();
fetchAlertsTicker();
updateMetricsPage();