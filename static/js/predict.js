// Prediction Page JavaScript

let currentPrediction = null;

// Cost concern slider
document.getElementById('costConcern').addEventListener('input', function() {
    document.getElementById('costConcernValue').textContent = this.value;
});

// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('prescriptionFile');

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#0d6efd';
    uploadArea.style.backgroundColor = '#e7f1ff';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = '#dee2e6';
    uploadArea.style.backgroundColor = '#f8f9fa';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#dee2e6';
    uploadArea.style.backgroundColor = '#f8f9fa';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload_prescription', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('fileName').textContent = `✓ ${file.name}`;
            document.getElementById('uploadedFile').style.display = 'block';
            
            // Auto-fill form if data extracted
            if (data.data) {
                if (data.data.medication_count) {
                    document.getElementById('medicationCount').value = data.data.medication_count;
                }
                if (data.data.dosage_frequency) {
                    document.getElementById('dosageFrequency').value = data.data.dosage_frequency;
                }
            }
            
            showNotification('Prescription uploaded successfully!', 'success');
        } else {
            showNotification('Error uploading prescription: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Error uploading prescription: ' + error.message, 'danger');
    }
}

function clearFile() {
    document.getElementById('uploadedFile').style.display = 'none';
    fileInput.value = '';
}

// Form submission
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        medication_count: document.getElementById('medicationCount').value,
        dosage_frequency: document.getElementById('dosageFrequency').value,
        reminder_enabled: document.getElementById('reminderEnabled').checked,
        missed_doses_last_month: document.getElementById('missedDoses').value,
        comorbidities: document.getElementById('comorbidities').value,
        side_effects: document.getElementById('sideEffects').checked,
        cost_concern: document.getElementById('costConcern').value
    };
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentPrediction = data;
            displayResults(data);
        } else {
            showNotification('Error making prediction: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Error making prediction: ' + error.message, 'danger');
    }
});

function displayResults(data) {
    // Show results card
    const resultsCard = document.getElementById('resultsCard');
    resultsCard.style.display = 'block';
    
    // Hide info card
    document.getElementById('infoCard').style.display = 'none';
    
    // Update adherence score
    document.getElementById('adherenceScore').textContent = data.adherence_score + '%';
    
    // Update risk badge
    const riskBadge = document.getElementById('riskBadge');
    riskBadge.textContent = data.risk_level + ' Risk';
    riskBadge.className = `badge bg-${getRiskColor(data.risk_level)} fs-5`;
    
    // Update results header color
    const resultsHeader = document.getElementById('resultsHeader');
    resultsHeader.className = `card-header text-white bg-${getRiskColor(data.risk_level)}`;
    
    // Update confidence bar
    const confidenceBar = document.getElementById('confidenceBar');
    confidenceBar.style.width = data.confidence + '%';
    confidenceBar.className = `progress-bar bg-${getRiskColor(data.risk_level)}`;
    document.getElementById('confidenceText').textContent = data.confidence + '%';
    
    // Update recommendations
    const recommendationsDiv = document.getElementById('recommendations');
    if (data.recommendations && data.recommendations.length > 0) {
        recommendationsDiv.innerHTML = data.recommendations.map(rec => `
            <div class="alert alert-${getPriorityColor(rec.priority)} mb-2 p-2">
                <strong>${rec.title}</strong><br>
                <small>${rec.description}</small>
            </div>
        `).join('');
    } else {
        recommendationsDiv.innerHTML = '<p class="text-success">No specific recommendations. Continue current treatment plan.</p>';
    }
    
    // Scroll to results
    resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    
    showNotification('Prediction completed successfully!', 'success');
}

function getRiskColor(riskLevel) {
    switch(riskLevel) {
        case 'Low': return 'success';
        case 'Medium': return 'warning';
        case 'High': return 'danger';
        default: return 'secondary';
    }
}

function getPriorityColor(priority) {
    switch(priority) {
        case 'high': return 'danger';
        case 'medium': return 'warning';
        case 'low': return 'info';
        default: return 'secondary';
    }
}

async function savePatient() {
    if (!currentPrediction) {
        showNotification('Please make a prediction first', 'warning');
        return;
    }
    
    const patientName = prompt('Enter patient name:');
    if (!patientName) return;
    
    const patientData = {
        name: patientName,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        medication_count: document.getElementById('medicationCount').value,
        dosage_frequency: document.getElementById('dosageFrequency').value,
        reminder_enabled: document.getElementById('reminderEnabled').checked,
        missed_doses_last_month: document.getElementById('missedDoses').value,
        comorbidities: document.getElementById('comorbidities').value,
        side_effects: document.getElementById('sideEffects').checked,
        cost_concern: document.getElementById('costConcern').value,
        adherence_score: currentPrediction.adherence_score,
        risk_level: currentPrediction.risk_level,
        recommendations: currentPrediction.recommendations
    };
    
    try {
        const response = await fetch('/api/patients', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(patientData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Patient record saved successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/patients';
            }, 1500);
        } else {
            showNotification('Error saving patient: ' + data.error, 'danger');
        }
    } catch (error) {
        showNotification('Error saving patient: ' + error.message, 'danger');
    }
}

function resetForm() {
    document.getElementById('predictionForm').reset();
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('infoCard').style.display = 'block';
    document.getElementById('uploadedFile').style.display = 'none';
    document.getElementById('costConcernValue').textContent = '3';
    currentPrediction = null;
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
