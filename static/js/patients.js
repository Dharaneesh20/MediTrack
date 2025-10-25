// Patients Page JavaScript

let allPatients = [];

document.addEventListener('DOMContentLoaded', function() {
    loadPatients();
});

async function loadPatients() {
    try {
        const response = await fetch('/api/patients');
        const data = await response.json();
        
        if (data.success) {
            allPatients = data.patients;
            displayPatients(allPatients);
        }
    } catch (error) {
        console.error('Error loading patients:', error);
        showNotification('Error loading patients: ' + error.message, 'danger');
    }
}

function displayPatients(patients) {
    const tbody = document.getElementById('patientsTableBody');
    
    if (patients.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-5">
                    <i class="fas fa-user-slash fa-3x text-muted mb-3"></i>
                    <p class="text-muted">No patients found. Add your first patient to get started.</p>
                    <a href="/predict" class="btn btn-primary">
                        <i class="fas fa-user-plus me-2"></i>Add Patient
                    </a>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = '';
    
    patients.forEach((patient, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${patient.id || (index + 1)}</td>
            <td><strong>${patient.name || 'N/A'}</strong></td>
            <td>${patient.age}</td>
            <td>${patient.gender}</td>
            <td>${patient.medication_count}</td>
            <td>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-${getScoreColor(patient.adherence_score)}" 
                         role="progressbar" 
                         style="width: ${patient.adherence_score}%"
                         aria-valuenow="${patient.adherence_score}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                        ${patient.adherence_score}%
                    </div>
                </div>
            </td>
            <td>
                <span class="badge bg-${getRiskColor(patient.risk_level)}">
                    ${patient.risk_level}
                </span>
            </td>
            <td>${formatDate(patient.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="viewPatientDetails(${index})" 
                        data-bs-toggle="modal" data-bs-target="#patientModal">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deletePatient(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function viewPatientDetails(index) {
    const patient = allPatients[index];
    const detailsDiv = document.getElementById('patientDetails');
    
    detailsDiv.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-muted">Personal Information</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Name:</strong></td>
                        <td>${patient.name || 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Age:</strong></td>
                        <td>${patient.age}</td>
                    </tr>
                    <tr>
                        <td><strong>Gender:</strong></td>
                        <td>${patient.gender}</td>
                    </tr>
                    <tr>
                        <td><strong>Patient ID:</strong></td>
                        <td>${patient.id}</td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-muted">Medication Details</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Medications:</strong></td>
                        <td>${patient.medication_count}</td>
                    </tr>
                    <tr>
                        <td><strong>Dosage Frequency:</strong></td>
                        <td>${patient.dosage_frequency}x daily</td>
                    </tr>
                    <tr>
                        <td><strong>Reminder Enabled:</strong></td>
                        <td>${patient.reminder_enabled ? '✓ Yes' : '✗ No'}</td>
                    </tr>
                    <tr>
                        <td><strong>Missed Doses:</strong></td>
                        <td>${patient.missed_doses_last_month}</td>
                    </tr>
                </table>
            </div>
        </div>
        
        <hr>
        
        <div class="row">
            <div class="col-md-6">
                <h6 class="text-muted">Health Status</h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>Comorbidities:</strong></td>
                        <td>${patient.comorbidities}</td>
                    </tr>
                    <tr>
                        <td><strong>Side Effects:</strong></td>
                        <td>${patient.side_effects ? '✓ Yes' : '✗ No'}</td>
                    </tr>
                    <tr>
                        <td><strong>Cost Concern:</strong></td>
                        <td>${patient.cost_concern}/5</td>
                    </tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6 class="text-muted">Adherence Analysis</h6>
                <div class="text-center mb-3">
                    <div class="adherence-score-circle mx-auto" style="width: 120px; height: 120px;">
                        <h2 style="font-size: 2rem;">${patient.adherence_score}%</h2>
                        <p style="font-size: 0.7rem;">Adherence</p>
                    </div>
                </div>
                <div class="text-center">
                    <span class="badge bg-${getRiskColor(patient.risk_level)} fs-6">
                        ${patient.risk_level} Risk
                    </span>
                </div>
            </div>
        </div>
        
        <hr>
        
        <div class="row">
            <div class="col-12">
                <h6 class="text-muted">Recommendations</h6>
                ${patient.recommendations && patient.recommendations.length > 0 ? 
                    patient.recommendations.map(rec => `
                        <div class="alert alert-${getPriorityColor(rec.priority)} mb-2">
                            <strong>${rec.title}</strong><br>
                            <small>${rec.description}</small>
                        </div>
                    `).join('') :
                    '<p class="text-muted">No specific recommendations available.</p>'
                }
            </div>
        </div>
    `;
}

function filterPatients() {
    const searchTerm = document.getElementById('searchPatient').value.toLowerCase();
    const riskFilter = document.getElementById('filterRisk').value;
    
    let filteredPatients = allPatients;
    
    if (searchTerm) {
        filteredPatients = filteredPatients.filter(patient => 
            (patient.name || '').toLowerCase().includes(searchTerm)
        );
    }
    
    if (riskFilter) {
        filteredPatients = filteredPatients.filter(patient => 
            patient.risk_level === riskFilter
        );
    }
    
    displayPatients(filteredPatients);
}

// Add event listeners for search and filter
document.getElementById('searchPatient').addEventListener('input', filterPatients);
document.getElementById('filterRisk').addEventListener('change', filterPatients);

function deletePatient(index) {
    if (confirm('Are you sure you want to delete this patient record?')) {
        // In a real application, this would make an API call to delete the patient
        allPatients.splice(index, 1);
        displayPatients(allPatients);
        showNotification('Patient record deleted', 'success');
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

function getScoreColor(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

function getPriorityColor(priority) {
    switch(priority) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'secondary';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
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
    }, 3000);
}
