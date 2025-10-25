// Analytics Page JavaScript

let trendsChart, riskDistChart, ageGroupChart, medicationChart;

document.addEventListener('DOMContentLoaded', function() {
    loadAnalyticsData();
    initializeCharts();
});

async function loadAnalyticsData() {
    try {
        const response = await fetch('/api/analytics/overview');
        const data = await response.json();
        
        if (data.success) {
            // Update key metrics
            document.getElementById('avgAdherence').textContent = data.average_adherence + '%';
            document.getElementById('totalPatientsAnalytics').textContent = data.total_patients;
            document.getElementById('highRiskAnalytics').textContent = data.high_risk;
            
            // Update charts with real data
            updateChartsWithData(data);
        }
    } catch (error) {
        console.error('Error loading analytics data:', error);
    }
}

function initializeCharts() {
    // Adherence Trends Over Time
    const ctx1 = document.getElementById('trendsChart');
    if (ctx1) {
        trendsChart = new Chart(ctx1, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
                datasets: [{
                    label: 'Average Adherence',
                    data: [68, 70, 72, 71, 74, 76, 75, 77, 79, 80],
                    borderColor: 'rgb(13, 110, 253)',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Target Adherence',
                    data: [80, 80, 80, 80, 80, 80, 80, 80, 80, 80],
                    borderColor: 'rgb(25, 135, 84)',
                    borderDash: [5, 5],
                    tension: 0,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Adherence Score (%)'
                        }
                    }
                }
            }
        });
    }
    
    // Risk Distribution
    const ctx2 = document.getElementById('riskDistChart');
    if (ctx2) {
        riskDistChart = new Chart(ctx2, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                datasets: [{
                    data: [55, 30, 15],
                    backgroundColor: [
                        'rgb(25, 135, 84)',
                        'rgb(255, 193, 7)',
                        'rgb(220, 53, 69)'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
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
    
    // Age Group Analysis
    const ctx3 = document.getElementById('ageGroupChart');
    if (ctx3) {
        ageGroupChart = new Chart(ctx3, {
            type: 'bar',
            data: {
                labels: ['18-30', '31-45', '46-60', '61-75', '76+'],
                datasets: [{
                    label: 'Average Adherence',
                    data: [72, 75, 78, 70, 65],
                    backgroundColor: 'rgba(13, 202, 240, 0.7)',
                    borderColor: 'rgb(13, 202, 240)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Adherence Score (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Age Group'
                        }
                    }
                }
            }
        });
    }
    
    // Medication Complexity Impact
    const ctx4 = document.getElementById('medicationChart');
    if (ctx4) {
        medicationChart = new Chart(ctx4, {
            type: 'bar',
            data: {
                labels: ['1-2 Meds', '3-4 Meds', '5-6 Meds', '7+ Meds'],
                datasets: [{
                    label: 'With Reminders',
                    data: [85, 78, 72, 65],
                    backgroundColor: 'rgba(25, 135, 84, 0.7)',
                    borderColor: 'rgb(25, 135, 84)',
                    borderWidth: 2
                }, {
                    label: 'Without Reminders',
                    data: [70, 62, 55, 48],
                    backgroundColor: 'rgba(220, 53, 69, 0.7)',
                    borderColor: 'rgb(220, 53, 69)',
                    borderWidth: 2
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
                            text: 'Adherence Score (%)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Medication Count'
                        }
                    }
                }
            }
        });
    }
}

function updateChartsWithData(data) {
    // Update risk distribution chart with real data
    if (riskDistChart && data) {
        riskDistChart.data.datasets[0].data = [
            data.low_risk || 0,
            data.medium_risk || 0,
            data.high_risk || 0
        ];
        riskDistChart.update();
    }
}

// Export analytics report
function exportReport() {
    showNotification('Analytics report export feature coming soon!', 'info');
}

// Refresh analytics data
async function refreshAnalytics() {
    await loadAnalyticsData();
    showNotification('Analytics data refreshed successfully!', 'success');
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
