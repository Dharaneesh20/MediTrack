// Dashboard JavaScript

let adherenceChart = null;
let riskChart = null;

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    initializeCharts();
});

async function loadDashboardData() {
    try {
        // Load analytics overview
        const response = await fetch('/api/analytics/overview');
        const data = await response.json();
        
        if (data.success) {
            // Update stats cards
            document.getElementById('totalPatients').textContent = data.total_patients;
            document.getElementById('highRisk').textContent = data.high_risk;
            document.getElementById('mediumRisk').textContent = data.medium_risk;
            document.getElementById('lowRisk').textContent = data.low_risk;
            
            // Update charts
            updateCharts(data);
        }
        
        // Load recent patients
        await loadRecentPatients();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

async function loadRecentPatients() {
    try {
        const response = await fetch('/api/patients');
        const data = await response.json();
        
        if (data.success && data.patients.length > 0) {
            const tbody = document.getElementById('recentPatientsBody');
            tbody.innerHTML = '';
            
            // Show only the 5 most recent patients
            const recentPatients = data.patients.slice(-5).reverse();
            
            recentPatients.forEach(patient => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${patient.name || 'N/A'}</td>
                    <td>${patient.age}</td>
                    <td><strong>${patient.adherence_score}</strong></td>
                    <td><span class="badge bg-${getRiskColor(patient.risk_level)}">${patient.risk_level}</span></td>
                    <td>${formatDate(patient.created_at)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewPatient('${patient.id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading recent patients:', error);
    }
}

function initializeCharts() {
    // Adherence Trends Chart
    const ctx1 = document.getElementById('adherenceChart');
    if (ctx1) {
        adherenceChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6'],
                datasets: [{
                    label: 'Average Adherence Score',
                    data: [65, 68, 72, 70, 75, 78],
                    borderColor: 'rgb(13, 110, 253)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Adherence Score'
                        }
                    }
                }
            }
        });
    }
    
    // Risk Distribution Chart
    const ctx2 = document.getElementById('riskChart');
    if (ctx2) {
        riskChart = new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                datasets: [{
                    data: [50, 30, 20],
                    backgroundColor: [
                        'rgb(25, 135, 84)',
                        'rgb(255, 193, 7)',
                        'rgb(220, 53, 69)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function updateCharts(data) {
    // Update risk distribution chart
    if (riskChart) {
        riskChart.data.datasets[0].data = [
            data.low_risk,
            data.medium_risk,
            data.high_risk
        ];
        riskChart.update();
    }
}

function getRiskColor(riskLevel) {
    switch(riskLevel) {
        case 'Low': return 'success';
        case 'Medium': return 'warning';
        case 'High': return 'danger';
        default: return 'secondary';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function viewPatient(patientId) {
    window.location.href = `/patients?id=${patientId}`;
}

async function refreshDashboard() {
    const button = event.target;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Refreshing...';
    button.disabled = true;
    
    await loadDashboardData();
    
    button.innerHTML = '<i class="fas fa-sync me-2"></i>Refresh Data';
    button.disabled = false;
    
    // Show success notification
    showNotification('Dashboard refreshed successfully!', 'success');
}

async function trainModel() {
    const button = event.target;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Training...';
    button.disabled = true;
    
    try {
        const response = await fetch('/api/train_model', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification('Model trained successfully! Accuracy: ' + (data.metrics.accuracy * 100).toFixed(2) + '%', 'success');
        } else {
            showNotification('Error training model: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Error training model: ' + error.message, 'danger');
    }
    
    button.innerHTML = '<i class="fas fa-brain me-2"></i>Train Model';
    button.disabled = false;
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}
