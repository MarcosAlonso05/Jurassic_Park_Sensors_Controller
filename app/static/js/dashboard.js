let chartInstance = null;
let bpmChartInstance = null;

async function fetchHabitats() {
    const container = document.getElementById('habitat-grid');
    if (!container) return; 

    try {
        const response = await fetch('/api/habitats');
        const habitats = await response.json();
        
        container.innerHTML = ''; 

        habitats.forEach(habitat => {
            const card = document.createElement('div');
            card.className = 'habitat-card';
            
            card.onclick = () => window.location.href = `/habitat/${habitat.id}`;
            
            card.innerHTML = `
                <button class="delete-btn" onclick="deleteHabitat('${habitat.id}', event)">✖</button>
                <h3>${habitat.name}</h3>
                <div class="card-stats">
                    <p>🌡️ ${habitat.mean_temperature}°C</p>
                    <p>🦖 ${habitat.dinosaur_ids.length} Dinos</p>
                </div>
                <div class="status-indicator status-active">● Monitoring Active</div>
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
        
        const alerts = data.logs.filter(line => line.includes("ALERT!"));

        if (alerts.length === 0) {
            container.innerHTML = '<div class="alert-item" style="background:#2ecc71; color:white"> System Normal. No active threats.</div>';
            return;
        }

        alerts.slice(-5).reverse().forEach(alert => {
            const div = document.createElement('div');
            div.className = 'alert-item';
            
            if (alert.includes("critical")) div.classList.add('alert-critical');
            else if (alert.includes("high")) div.classList.add('alert-high');
            else div.classList.add('alert-low');

            div.textContent = alert.substring(20); 
            container.appendChild(div);
        });
    } catch (e) { console.error(e); }
}

// == METRICS PAGE LOGIC ==

async function updateMetricsPage() {
    if (!window.isMetricsPage) return; 

    try {
        const response = await fetch('/api/metrics');
        const data = await response.json();

        document.getElementById('metric-uptime').innerText = data.uptime_seconds + 's';
        document.getElementById('metric-total').innerText = data.total_processed;
        document.getElementById('metric-alerts').innerText = data.total_alerts;
        document.getElementById('metric-tps').innerText = data.current_throughput_tps;

        const logResponse = await fetch('/api/logs');
        const logData = await logResponse.json();
        const logViewer = document.getElementById('full-log-viewer');
        if (logViewer) {
            logViewer.innerText = logData.logs.join('\n');
            logViewer.scrollTop = logViewer.scrollHeight; 
        }

        updateChart(data.current_throughput_tps);
        updateBpmChart(data.avg_bpm);

    } catch (e) { console.error("Metrics error:", e); }
}

function initChart() {
    const ctx = document.getElementById('throughputChart');
    if (!ctx) return;

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [], 
            datasets: [{
                label: 'Events Processed / Second (TPS)',
                data: [], 
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.2)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function updateChart(tpsValue) {
    if (!chartInstance) return;
    const now = new Date().toLocaleTimeString();

    chartInstance.data.labels.push(now);
    chartInstance.data.datasets[0].data.push(tpsValue);

    if (chartInstance.data.labels.length > 20) {
        chartInstance.data.labels.shift();
        chartInstance.data.datasets[0].data.shift();
    }
    chartInstance.update();
}

function initBpmChart() {
    const ctx = document.getElementById('bpmChart');
    if (!ctx) return;

    bpmChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Average Heart Rate (BPM)',
                data: [],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.2)',
                borderWidth: 2,
                pointRadius: 0, 
                tension: 0.4,   
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                y: { 
                    beginAtZero: false,
                    suggestedMin: 30,
                    suggestedMax: 150 
                }
            }
        }
    });
}

function updateBpmChart(bpmValue) {
    if (!bpmChartInstance) return;

    const now = new Date().toLocaleTimeString();

    bpmChartInstance.data.labels.push(now);
    bpmChartInstance.data.datasets[0].data.push(bpmValue);

    if (bpmChartInstance.data.labels.length > 30) {
        bpmChartInstance.data.labels.shift();
        bpmChartInstance.data.datasets[0].data.shift();
    }

    bpmChartInstance.update();
}

// == MANAGEMENT OF MODALS AND FORMS ==

function openModal(id) {
    document.getElementById(id).style.display = "block";
    if (id === 'dinoModal') loadHabitatsIntoSelect();
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
}

async function submitHabitat(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const payload = {
        name: formData.get('name'),
        temp: parseFloat(formData.get('temp')),
        width: parseFloat(formData.get('width')),
        length: parseFloat(formData.get('length')),
        height: parseFloat(formData.get('height'))
    };

    const res = await fetch('/api/habitats', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        closeModal('habitatModal');
        event.target.reset(); 
        fetchHabitats(); 
        alert("Habitat constructed successfully.");
    } else {
        alert("Error constructing habitat.");
    }
}

async function loadHabitatsIntoSelect() {
    const res = await fetch('/api/habitats');
    const habitats = await res.json();
    const select = document.getElementById('habitatSelect');
    
    select.innerHTML = '';
    habitats.forEach(h => {
        const option = document.createElement('option');
        option.value = h.id;
        option.textContent = h.name;
        select.appendChild(option);
    });
}

async function submitDino(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const payload = {
        name: formData.get('name'),
        species: formData.get('species'),
        category: formData.get('category'),
        heart_rate: parseInt(formData.get('heart_rate')),
        habitat_id: formData.get('habitat_id')
    };

    const res = await fetch('/api/dinosaurs', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        closeModal('dinoModal');
        event.target.reset();
        fetchHabitats(); 
        alert("Dinosaur create successfully. Sensors active.");
    } else {
        alert("Error creating dinosaur.");
    }
}

async function deleteHabitat(id, event) {
    event.stopPropagation(); 
    if(!confirm("Are you sure? This will dismantle the habitat and its sensors.")) return;

    await fetch(`/api/habitats/${id}`, { method: 'DELETE' });
    fetchHabitats();
}


if (window.isMetricsPage) {
    initChart();
    initBpmChart();
}

setInterval(() => {
    fetchHabitats();     
    fetchAlertsTicker(); 
    updateMetricsPage(); 
}, 2000);

fetchHabitats();
fetchAlertsTicker();
updateMetricsPage();