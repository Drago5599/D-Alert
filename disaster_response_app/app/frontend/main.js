const API_URL = "https://d-alert.onrender.com";
let map, markers = [];

const notification = document.getElementById('notification');
const notificationMessage = document.getElementById('notification-message');
const notificationClose = document.getElementById('notification-close');

// Initialize Map
function initMap() {
    map = L.map('map').setView([18.0179, -76.8099], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
}

// Show Notification
function showNotification(message, type = 'danger') {
    notificationMessage.textContent = message;
    notification.className = 'notification'; // Reset classes
    notification.classList.add(type);

    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 5000);
}

notificationClose.addEventListener('click', () => {
    notification.classList.add('hidden');
});

// Fetch and Update Data
async function updateDashboard() {
    try {
        const [alerts, priorities, clusters] = await Promise.all([
            fetch(`${API_URL}/alerts`).then(res => res.json()),
            fetch(`${API_URL}/priorities`).then(res => res.json()),
            fetch(`${API_URL}/clusters`).then(res => res.json())
        ]);

        updateMetrics(alerts, priorities, clusters);
        updateMap(alerts);
        updatePriorityList(priorities);
        updateLiveFeed(alerts);
        document.getElementById('backend-status').textContent = 'Backend: Online';
        document.getElementById('backend-status').style.background = '#059669';
    } catch (error) {
        console.error('Error updating dashboard:', error);
        document.getElementById('backend-status').textContent = 'Backend: Offline';
        document.getElementById('backend-status').style.background = '#dc2626';
    }
}

function updateMetrics(alerts, priorities, clusters) {
    const activeCount = alerts.filter(a => a.status !== 'resolved').length;
    document.getElementById('metric-active').textContent = activeCount;
    document.getElementById('metric-priority').textContent = priorities.length;
    document.getElementById('metric-clusters').textContent = clusters.length;
}

function updateMap(alerts) {
    // Clear existing markers
    markers.forEach(m => map.removeLayer(m));
    markers = [];

    alerts.forEach(a => {
        if (a.lat && a.lon && a.status !== 'resolved') {
            const color = a.risk_score > 4 ? 'red' : a.risk_score > 2 ? 'orange' : 'blue';
            const marker = L.circleMarker([a.lat, a.lon], {
                radius: 8,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);

            marker.bindPopup(`
                <strong>${a.disaster_type.toUpperCase()}</strong><br>
                Risk: ${a.risk_score}<br>
                <em>${a.raw_text}</em>
            `);
            markers.push(marker);
        }
    });
}

function updatePriorityList(priorities) {
    const container = document.getElementById('priority-items');
    container.innerHTML = '';

    priorities.slice(0, 5).forEach(p => {
        const div = document.createElement('div');
        div.className = 'priority-item';
        div.innerHTML = `
            <span class="risk-badge">Risk: ${p.risk_score}</span>
            <h4>${p.disaster_type}</h4>
            <div class="location">${p.location_name} • ${p.source}</div>
            <div class="raw-text">"${p.raw_text}"</div>
            <div class="action">👉 ${p.suggested_action}</div>
            <div class="action-buttons">
                <button class="btn-small btn-ack" onclick="handleAction('${p.id}', 'ack')">Acknowledge</button>
                <button class="btn-small btn-resolve" onclick="handleAction('${p.id}', 'resolve')">Resolve</button>
            </div>
        `;
        container.appendChild(div);
    });
}

function updateLiveFeed(alerts) {
    const body = document.getElementById('alerts-body');
    body.innerHTML = '';

    alerts.slice(0, 20).forEach(a => {
        const row = document.createElement('tr');
        const time = new Date(a.timestamp_utc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const statusClass = a.status === 'new' ? 'badge-new' : a.status === 'acknowledged' ? 'badge-ack' : 'badge-res';
        
        row.innerHTML = `
            <td>${time}</td>
            <td>${a.disaster_type}</td>
            <td>${a.location_name || 'Unknown'}</td>
            <td><span class="badge ${statusClass}">${a.status}</span></td>
            <td><strong>${a.risk_score}</strong></td>
        `;
        body.appendChild(row);
    });
}

async function handleAction(id, action) {
    try {
        await fetch(`${API_URL}/alerts/${id}/${action}`, { method: 'POST' });
        updateDashboard();
    } catch (error) {
        console.error(`Error performing ${action}:`, error);
    }
}

// Handle Form Submission
document.getElementById('incident-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = document.getElementById('text').value;
    const location_name = document.getElementById('location').value;

    try {
        const res = await fetch(`${API_URL}/ingest/social`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, location_name })
        });

        if (res.ok) {
            document.getElementById('incident-form').reset();
            updateDashboard();
            showNotification('Report submitted successfully!', 'success');
        } else if (res.status === 429) {
            showNotification("You have exceeded the limit and can't report until an hour's time.", 'danger');
        } else {
            showNotification('Failed to submit report.', 'danger');
        }
    } catch (error) {
        console.error('Error submitting report:', error);
        showNotification('Failed to submit report.', 'danger');
    }
});

// Init
initMap();
updateDashboard();
setInterval(updateDashboard, 10000); // Auto-refresh every 10s
