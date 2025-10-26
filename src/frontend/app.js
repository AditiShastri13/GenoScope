// Base API URL - change this if your backend runs on a different port or host
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const uploadForm = document.getElementById('upload-form');
const sequenceForm = document.getElementById('sequence-form');
const fileInput = document.getElementById('file-input');
const fileName = document.getElementById('file-name');
const sequenceInput = document.getElementById('sequence-input');
const sequenceLength = document.getElementById('sequence-length');
const resultsContainer = document.getElementById('results-container');
const closeResultsBtn = document.getElementById('close-results');
const resultStatus = document.getElementById('result-status');
const resultDetails = document.getElementById('result-details');
const refreshModelsBtn = document.getElementById('refresh-models-btn');
const trainModelsBtn = document.getElementById('train-models-btn');
const sickleModelsContainer = document.getElementById('sickle-cell-models');
const breastCancerModelsContainer = document.getElementById('breast-cancer-models');
const versionSelect = document.getElementById('version-select');
const diseaseSelect = document.getElementById('disease-select');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Load model info on page load
    loadModelInfo();
    
    // Tab switching
    tabBtns.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
    
    // File input change
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
        } else {
            fileName.textContent = 'No file selected';
        }
    });
    
    // Sequence input change
    sequenceInput.addEventListener('input', updateSequenceStats);
    
    // Form submissions
    uploadForm.addEventListener('submit', handleFileUpload);
    sequenceForm.addEventListener('submit', handleDirectSequence);
    
    // Close results
    closeResultsBtn.addEventListener('click', () => {
        resultsContainer.classList.add('hidden');
    });
    
    // Model info controls
    refreshModelsBtn.addEventListener('click', loadModelInfo);
    trainModelsBtn.addEventListener('click', trainModels);
    
    // Change disease to populate version select
    diseaseSelect.addEventListener('change', updateVersionOptions);
});

// Tab Switching
function switchTab(tabId) {
    tabBtns.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    tabContents.forEach(content => {
        if (content.id === tabId) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// Update sequence statistics
function updateSequenceStats() {
    const sequence = sequenceInput.value.trim().toUpperCase();
    const length = sequence.length;
    sequenceLength.textContent = `Length: ${length} bases`;
    
    // Basic validation - highlight if invalid characters
    const validBases = new Set('ATGC');
    let isValid = true;
    
    for (const base of sequence) {
        if (!validBases.has(base)) {
            isValid = false;
            break;
        }
    }
    
    if (!isValid && length > 0) {
        sequenceLength.innerHTML += ' <span style="color: red;">(Invalid characters detected)</span>';
    }
}

// Handle file upload form submission
async function handleFileUpload(e) {
    e.preventDefault();
    
    const file = fileInput.files[0];
    if (!file) {
        alert('Please select a file to analyze');
        return;
    }
    
    // Show results container with loading state
    showLoadingResults();
    
    const formData = new FormData();
    formData.append('file', file);
    
    const diseaseType = diseaseSelect.value;
    const version = versionSelect.value;
    
    try {
        let response;
        
        if (version === 'latest') {
            // Use standard endpoint without version
            response = await fetch(`${API_BASE_URL}/predict/?analysis_type=${diseaseType}`, {
                method: 'POST',
                body: formData
            });
        } else {
            // Use versioned endpoint
            response = await fetch(`${API_BASE_URL}/predict/${diseaseType}/${version}/`, {
                method: 'POST',
                body: formData
            });
        }
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        displayResults(result);
    } catch (error) {
        displayError(error);
    }
}

// Handle direct sequence form submission
async function handleDirectSequence(e) {
    e.preventDefault();
    
    const sequence = sequenceInput.value.trim();
    if (sequence.length < 50) {
        alert('Sequence must be at least 50 characters long');
        return;
    }
    
    // Show results container with loading state
    showLoadingResults();
    
    const diseaseType = document.getElementById('direct-disease-select').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze-sequence/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sequence: sequence,
                patient_id: 'direct-analysis',
                analysis_type: diseaseType
            })
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        displayResults(result);
    } catch (error) {
        displayError(error);
    }
}

// Show loading state in results container
function showLoadingResults() {
    resultsContainer.classList.remove('hidden');
    resultStatus.classList.remove('hidden');
    resultDetails.classList.add('hidden');
}

// Display analysis results
function displayResults(result) {
    resultStatus.classList.add('hidden');
    resultDetails.classList.remove('hidden');
    
    const summary = document.querySelector('.result-summary');
    const metrics = document.querySelector('.result-metrics');
    
    let summaryHTML = '';
    let metricsHTML = '<h4>Sequence Details</h4>';
    
    // Summary based on has_mutation
    if (result.has_mutation) {
        summaryHTML = `
            <h3 class="positive-result"><i class="fas fa-exclamation-triangle"></i> Mutation Detected</h3>
            <p><strong>Disease:</strong> ${result.disease}</p>
            <p><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</p>
            <p>${result.message}</p>
        `;
    } else {
        summaryHTML = `
            <h3 class="negative-result"><i class="fas fa-check-circle"></i> No Mutation Detected</h3>
            <p>${result.message}</p>
        `;
    }
    
    // Metrics display
    if (result.details) {
        Object.entries(result.details).forEach(([key, value]) => {
            if (typeof value === 'object') {
                metricsHTML += `<div class="metric-row">
                    <span class="metric-name">${formatKey(key)}</span>
                    <span class="metric-value">${JSON.stringify(value)}</span>
                </div>`;
            } else {
                metricsHTML += `<div class="metric-row">
                    <span class="metric-name">${formatKey(key)}</span>
                    <span class="metric-value">${value}</span>
                </div>`;
            }
        });
    }
    
    summary.innerHTML = summaryHTML;
    metrics.innerHTML = metricsHTML;
}

// Display error in results
function displayError(error) {
    resultStatus.classList.add('hidden');
    resultDetails.classList.remove('hidden');
    
    const summary = document.querySelector('.result-summary');
    const metrics = document.querySelector('.result-metrics');
    
    summary.innerHTML = `
        <h3 class="warning-result"><i class="fas fa-exclamation-circle"></i> Error</h3>
        <p>There was an error analyzing the sequence:</p>
        <p>${error.message}</p>
    `;
    
    metrics.innerHTML = `
        <p>Please check your input and try again. Make sure:</p>
        <ul>
            <li>The backend server is running at ${API_BASE_URL}</li>
            <li>The file format is supported (FASTA or CSV)</li>
            <li>The sequence contains valid DNA nucleotides (A, T, G, C)</li>
            <li>The sequence is at least 50 characters long</li>
        </ul>
    `;
}

// Format key names for display
function formatKey(key) {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Load model information
async function loadModelInfo() {
    try {
        sickleModelsContainer.innerHTML = '<div class="loader"></div>';
        breastCancerModelsContainer.innerHTML = '<div class="loader"></div>';
        
        const response = await fetch(`${API_BASE_URL}/models/info/`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Display sickle cell models
        displayModelInfo(data.sickle_cell, sickleModelsContainer, 'sickle_cell');
        
        // Display breast cancer models
        displayModelInfo(data.breast_cancer, breastCancerModelsContainer, 'breast_cancer');
        
        // Update version select options
        updateVersionOptions();
    } catch (error) {
        sickleModelsContainer.innerHTML = `<p class="error-message">Error loading model information: ${error.message}</p>`;
        breastCancerModelsContainer.innerHTML = `<p class="error-message">Error loading model information: ${error.message}</p>`;
    }
}

// Display model information
function displayModelInfo(modelData, container, modelType) {
    if (!modelData || Object.keys(modelData).length === 0) {
        container.innerHTML = '<p>No model information available</p>';
        return;
    }
    
    let html = '';
    
    if (modelData.version) {
        html += `
            <div class="model-version">
                <h4>Current Model: ${modelData.version}</h4>
                <div class="model-metrics">
                    <p><strong>Type:</strong> ${modelData.type || 'Unknown'}</p>
                    <p><strong>Accuracy:</strong> ${modelData.accuracy ? (modelData.accuracy * 100).toFixed(1) + '%' : 'Unknown'}</p>
                    <p><strong>Training Date:</strong> ${formatDate(modelData.training_date)}</p>
                </div>
            </div>
        `;
    }
    
    // Store model versions for the version selector
    if (!window.modelVersions) {
        window.modelVersions = {};
    }
    
    // Store available versions
    if (modelData.available_versions) {
        const versions = modelData.available_versions.map(v => v.version);
        window.modelVersions[modelType] = versions;
    }
    
    container.innerHTML = html;
}

// Update version options in select element
function updateVersionOptions() {
    const selectedDisease = diseaseSelect.value;
    versionSelect.innerHTML = '<option value="latest">Latest Version</option>';
    
    if (window.modelVersions && window.modelVersions[selectedDisease]) {
        window.modelVersions[selectedDisease].forEach(version => {
            const option = document.createElement('option');
            option.value = version;
            option.textContent = `Version ${version}`;
            versionSelect.appendChild(option);
        });
    }
}

// Train new models
async function trainModels() {
    trainModelsBtn.disabled = true;
    trainModelsBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/train-demo/`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        alert(`Models trained successfully: ${result.message}`);
        
        // Reload model info
        await loadModelInfo();
    } catch (error) {
        alert(`Error training models: ${error.message}`);
    } finally {
        trainModelsBtn.disabled = false;
        trainModelsBtn.innerHTML = '<i class="fas fa-cogs"></i> Train Demo Models';
    }
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString();
    } catch (e) {
        return dateString;
    }
}