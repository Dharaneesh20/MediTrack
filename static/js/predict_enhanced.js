// Enhanced Predict.js with Voice Input and Medicine Search

let currentResults = null;
let selectedMedicines = [];
let recognition = null;

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
        document.getElementById('voiceStatus').style.display = 'block';
        document.getElementById('voiceStatusText').textContent = 'Listening... Speak now';
        document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-stop"></i>';
    };
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('medicineSearch').value = transcript;
        searchMedicine(transcript);
    };
    
    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        document.getElementById('voiceStatusText').textContent = 'Error: ' + event.error;
        setTimeout(() => {
            document.getElementById('voiceStatus').style.display = 'none';
        }, 3000);
    };
    
    recognition.onend = () => {
        document.getElementById('voiceStatus').style.display = 'none';
        document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone"></i>';
    };
}

// Voice button click handler
document.addEventListener('DOMContentLoaded', () => {
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            if (recognition) {
                recognition.start();
            } else {
                alert('Voice recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            }
        });
    }
    
    // Medicine search input
    const medicineSearch = document.getElementById('medicineSearch');
    if (medicineSearch) {
        let searchTimeout;
        medicineSearch.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => searchMedicine(query), 300);
            } else {
                document.getElementById('medicineAutocomplete').style.display = 'none';
            }
        });
    }
});

// Search medicine in database
async function searchMedicine(query) {
    try {
        const response = await fetch(`/api/search_medicine?q=${encodeURIComponent(query)}&limit=10`);
        const data = await response.json();
        
        if (data.success && data.results.length > 0) {
            displayAutocomplete(data.results);
        } else {
            document.getElementById('medicineAutocomplete').style.display = 'none';
        }
    } catch (error) {
        console.error('Error searching medicine:', error);
    }
}

// Display autocomplete results
function displayAutocomplete(results) {
    const dropdown = document.getElementById('medicineAutocomplete');
    dropdown.innerHTML = results.map(medicine => 
        `<div class="autocomplete-item" onclick="selectMedicine('${medicine}')">${medicine}</div>`
    ).join('');
    dropdown.style.display = 'block';
}

// Select medicine from autocomplete
function selectMedicine(medicine) {
    document.getElementById('medicineSearch').value = medicine;
    document.getElementById('medicineAutocomplete').style.display = 'none';
}

// Add medicine to list
async function addMedicine() {
    const searchInput = document.getElementById('medicineSearch');
    const medicineName = searchInput.value.trim();
    
    if (!medicineName) {
        alert('Please enter a medicine name');
        return;
    }
    
    if (selectedMedicines.includes(medicineName.toLowerCase())) {
        alert('Medicine already added');
        return;
    }
    
    selectedMedicines.push(medicineName.toLowerCase());
    
    // Update UI
    updateMedicineChips();
    
    // Check interactions
    if (selectedMedicines.length >= 2) {
        await checkInteractions();
    }
    
    // Clear search
    searchInput.value = '';
    document.getElementById('medicineAutocomplete').style.display = 'none';
}

// Update medicine chips display
function updateMedicineChips() {
    const chipsContainer = document.getElementById('medicineChips');
    
    if (selectedMedicines.length === 0) {
        chipsContainer.innerHTML = '<span class="text-muted">No medicines added yet</span>';
        document.getElementById('medicationCount').value = 0;
        return;
    }
    
    chipsContainer.innerHTML = selectedMedicines.map(medicine => `
        <span class="badge bg-primary medicine-chip">
            ${medicine}
            <i class="fas fa-times ms-2" onclick="removeMedicine('${medicine}')" style="cursor: pointer;"></i>
        </span>
    `).join('');
    
    // Update medication count
    document.getElementById('medicationCount').value = selectedMedicines.length;
}

// Remove medicine from list
async function removeMedicine(medicine) {
    selectedMedicines = selectedMedicines.filter(m => m !== medicine);
    updateMedicineChips();
    
    if (selectedMedicines.length >= 2) {
        await checkInteractions();
    } else {
        document.getElementById('interactionWarnings').style.display = 'none';
    }
}

// Check drug interactions
async function checkInteractions() {
    try {
        const response = await fetch('/api/check_interactions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ medications: selectedMedicines })
        });
        
        const data = await response.json();
        
        if (data.success && data.summary.total > 0) {
            displayInteractions(data.summary);
        } else {
            document.getElementById('interactionWarnings').style.display = 'none';
        }
    } catch (error) {
        console.error('Error checking interactions:', error);
    }
}

// Display interaction warnings
function displayInteractions(summary) {
    const warningsDiv = document.getElementById('interactionWarnings');
    const listDiv = document.getElementById('interactionList');
    
    let html = `<p><strong>Found ${summary.total} interaction(s):</strong></p><ul class="mb-0">`;
    
    summary.interactions.forEach(interaction => {
        const severityIcon = {
            'high': '<i class="fas fa-exclamation-circle text-danger"></i>',
            'medium': '<i class="fas fa-exclamation-triangle text-warning"></i>',
            'low': '<i class="fas fa-info-circle text-info"></i>'
        }[interaction.severity];
        
        html += `
            <li class="mb-2">
                ${severityIcon} 
                <strong>${interaction.drug1}</strong> + <strong>${interaction.drug2}</strong>: 
                ${interaction.description}
                <span class="badge bg-${interaction.severity === 'high' ? 'danger' : interaction.severity === 'medium' ? 'warning' : 'info'}">${interaction.severity.toUpperCase()}</span>
            </li>
        `;
    });
    
    html += '</ul>';
    listDiv.innerHTML = html;
    warningsDiv.style.display = 'block';
}

// File upload handling
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('prescriptionFile');

uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
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
    
    // Show processing indicator
    document.getElementById('ocrProcessing').style.display = 'block';
    document.getElementById('ocrResults').style.display = 'none';
    
    try {
        const response = await fetch('/api/ocr/extract', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Hide processing indicator
        document.getElementById('ocrProcessing').style.display = 'none';
        
        if (data.success) {
            document.getElementById('fileName').textContent = file.name;
            document.getElementById('uploadedFile').style.display = 'block';
            
            // Show OCR results
            document.getElementById('ocrResults').style.display = 'block';
            const extractedText = data.editable_text || data.cleaned_text || data.raw_text || '';
            document.getElementById('ocrText').value = extractedText;
            
            // Show quality indicator
            if (data.quality) {
                showQualityIndicator(data.quality, extractedText);
            }
            
            // Show detected medicines if any
            if (data.medicines && data.medicines.length > 0) {
                document.getElementById('ocrMedicines').style.display = 'block';
                displayDetectedMedicines(data.medicines);
            } else if (extractedText.length > 20) {
                // If text extracted but no medicines found
                document.getElementById('ocrMedicines').innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> No medicine names detected automatically. 
                        You can manually add medicines using the search above.
                    </div>
                `;
                document.getElementById('ocrMedicines').style.display = 'block';
            }
            
            // Show suggestions if any
            if (data.suggestions && data.suggestions.length > 0) {
                showOCRSuggestions(data.suggestions);
            }
        } else {
            alert('Error processing image: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        document.getElementById('ocrProcessing').style.display = 'none';
        alert('Error uploading file. Please try again.');
    }
}

function showQualityIndicator(quality, text) {
    const ocrResults = document.getElementById('ocrResults');
    const existingIndicator = document.getElementById('qualityIndicator');
    if (existingIndicator) {
        existingIndicator.remove();
    }
    
    let badgeClass = 'bg-success';
    let icon = 'fa-check-circle';
    let message = 'Good quality';
    
    if (quality === 'poor') {
        badgeClass = 'bg-danger';
        icon = 'fa-exclamation-triangle';
        message = 'Poor quality - review carefully';
    } else if (quality === 'moderate') {
        badgeClass = 'bg-warning';
        icon = 'fa-exclamation-circle';
        message = 'Moderate quality - check text';
    }
    
    // Check if text is too short or garbled
    if (text.length < 20 || (text.match(/[a-zA-Z]/g) || []).length < text.length * 0.4) {
        badgeClass = 'bg-danger';
        icon = 'fa-times-circle';
        message = 'Low quality extraction - try another image';
    }
    
    const indicator = document.createElement('div');
    indicator.id = 'qualityIndicator';
    indicator.className = `badge ${badgeClass} mb-2`;
    indicator.style.fontSize = '0.9rem';
    indicator.innerHTML = `<i class="fas ${icon}"></i> OCR Quality: ${message}`;
    
    ocrResults.insertBefore(indicator, ocrResults.firstChild);
}

function displayDetectedMedicines(medicines) {
    const container = document.getElementById('detectedMedicinesList');
    container.innerHTML = medicines.map(med => `
        <div class="d-flex align-items-center justify-content-between mb-2 p-2 border rounded">
            <span class="fw-bold">${med}</span>
            <button class="btn btn-sm btn-success" onclick="addDetectedMedicine('${med}')">
                <i class="fas fa-plus"></i> Add to List
            </button>
        </div>
    `).join('');
}

function addDetectedMedicine(medicineName) {
    // Add to medicine search and trigger add
    document.getElementById('medicineSearch').value = medicineName;
    addMedicine();
}

function showOCRSuggestions(suggestions) {
    const suggestionsHtml = suggestions.map(s => 
        `<li class="small text-muted">${s}</li>`
    ).join('');
    
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-warning mt-2';
    alertDiv.innerHTML = `
        <strong><i class="fas fa-exclamation-triangle me-2"></i>OCR Tips:</strong>
        <ul class="mb-0 mt-2">${suggestionsHtml}</ul>
    `;
    
    document.getElementById('ocrResults').appendChild(alertDiv);
}

function clearFile() {
    fileInput.value = '';
    document.getElementById('uploadedFile').style.display = 'none';
    document.getElementById('ocrResults').style.display = 'none';
    document.getElementById('ocrText').value = '';
}

// Cost concern slider
const costConcern = document.getElementById('costConcern');
const costConcernValue = document.getElementById('costConcernValue');

costConcern.addEventListener('input', (e) => {
    costConcernValue.textContent = e.target.value;
});

// Form submission
document.getElementById('predictionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const patientData = {
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        medication_count: parseInt(document.getElementById('medicationCount').value),
        dosage_frequency: parseInt(document.getElementById('dosageFrequency').value),
        reminder_enabled: document.getElementById('reminderEnabled').checked ? 1 : 0,
        missed_doses_last_month: parseInt(document.getElementById('missedDoses').value),
        comorbidities: parseInt(document.getElementById('comorbidities').value),
        side_effects: document.getElementById('sideEffects').checked ? 1 : 0,
        cost_concern: parseInt(document.getElementById('costConcern').value),
        medicines: selectedMedicines
    };
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(patientData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentResults = data;
            displayResults(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error making prediction. Please try again.');
    }
});

function displayResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const infoCard = document.getElementById('infoCard');
    const resultsHeader = document.getElementById('resultsHeader');
    
    // Update header color based on risk
    const headerColors = {
        'Low': 'bg-success',
        'Medium': 'bg-warning',
        'High': 'bg-danger'
    };
    
    resultsHeader.className = 'card-header text-white ' + headerColors[data.risk_level];
    
    // Update score
    document.getElementById('adherenceScore').textContent = Math.round(data.adherence_score) + '%';
    
    // Update risk badge
    const riskBadge = document.getElementById('riskBadge');
    riskBadge.textContent = data.risk_level + ' Risk';
    riskBadge.className = 'badge badge-' + (data.risk_level === 'Low' ? 'success' : data.risk_level === 'Medium' ? 'warning' : 'danger') + ' fs-5';
    
    // Update confidence bar
    const confidence = Math.round(data.confidence);
    const confidenceBar = document.getElementById('confidenceBar');
    confidenceBar.style.width = confidence + '%';
    confidenceBar.className = 'progress-bar ' + (confidence >= 80 ? 'bg-success' : confidence >= 60 ? 'bg-warning' : 'bg-danger');
    document.getElementById('confidenceText').textContent = confidence + '%';
    
    // Show medicine factors if available
    if (data.medicine_factors && data.medicine_factors.length > 0) {
        const factorsHtml = `
            <div class="alert alert-info mt-3">
                <strong><i class="fas fa-pills"></i> Medicine Impact Factors:</strong>
                <ul class="mb-0 mt-2">
                    ${data.medicine_factors.map(factor => `<li><small>${factor}</small></li>`).join('')}
                </ul>
            </div>
        `;
        
        // Insert factors before recommendations
        const recommendationsDiv = document.getElementById('recommendations');
        const existingFactors = document.getElementById('medicineFactors');
        if (existingFactors) existingFactors.remove();
        
        const factorsDiv = document.createElement('div');
        factorsDiv.id = 'medicineFactors';
        factorsDiv.innerHTML = factorsHtml;
        recommendationsDiv.parentNode.insertBefore(factorsDiv, recommendationsDiv);
    }
    
    // Update recommendations
    const recommendationsDiv = document.getElementById('recommendations');
    if (data.recommendations && data.recommendations.length > 0) {
        recommendationsDiv.innerHTML = data.recommendations.map(rec => {
            // Handle both object format {title, description, priority} and simple string format
            if (typeof rec === 'string') {
                return `<div class="alert alert-info alert-sm mb-2"><small>${rec}</small></div>`;
            } else {
                return `
                    <div class="alert alert-${rec.priority === 'high' ? 'danger' : rec.priority === 'medium' ? 'warning' : 'info'} alert-sm mb-2">
                        <strong>${rec.title || ''}</strong><br>
                        <small>${rec.description || rec}</small>
                    </div>
                `;
            }
        }).join('');
    } else {
        recommendationsDiv.innerHTML = '<p class="text-success">No specific recommendations. Continue current adherence practices.</p>';
    }
    
    // Show results, hide info
    resultsCard.style.display = 'block';
    infoCard.style.display = 'none';
    
    // Scroll to results on mobile
    if (window.innerWidth < 992) {
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function savePatient() {
    const name = prompt('Enter patient name:');
    if (!name) return;
    
    const patientData = {
        name: name,
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        medication_count: parseInt(document.getElementById('medicationCount').value),
        dosage_frequency: parseInt(document.getElementById('dosageFrequency').value),
        missed_doses_last_month: parseInt(document.getElementById('missedDoses').value),
        comorbidities: parseInt(document.getElementById('comorbidities').value),
        adherence_score: currentResults.adherence_score,
        risk_level: currentResults.risk_level,
        timestamp: new Date().toISOString(),
        medicines: selectedMedicines
    };
    
    fetch('/api/patients', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(patientData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Patient record saved successfully!');
        } else {
            alert('Error saving patient record: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving patient record: ' + error.message);
    });
}

function resetForm() {
    document.getElementById('predictionForm').reset();
    document.getElementById('costConcernValue').textContent = '3';
    document.getElementById('resultsCard').style.display = 'none';
    document.getElementById('infoCard').style.display = 'block';
    clearFile();
    selectedMedicines = [];
    updateMedicineChips();
    document.getElementById('interactionWarnings').style.display = 'none';
    currentResults = null;
}
