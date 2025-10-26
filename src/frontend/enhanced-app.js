/**
 * Genoscope Frontend Application
 * Enhanced version with additional features and better error handling
 */

// Configuration
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',
    ENDPOINTS: {
        PREDICT: '/predict/',
        ANALYZE: '/analyze-sequence/',
        MODELS: '/models/info/',
        TRAIN: '/train-demo/',
        MODEL_VERSIONS: '/models/versions/',
        MODEL_DETAILS: '/models/details/'
    }
};

// Cache DOM elements
const DOM = {
    tabs: {
        buttons: document.querySelectorAll('.tab-btn'),
        contents: document.querySelectorAll('.tab-content')
    },
    forms: {
        upload: document.getElementById('upload-form'),
        sequence: document.getElementById('sequence-form')
    },
    inputs: {
        file: document.getElementById('file-input'),
        fileName: document.getElementById('file-name'),
        sequence: document.getElementById('sequence-input'),
        sequenceStats: document.getElementById('sequence-length')
    },
    results: {
        container: document.getElementById('results-container'),
        closeBtn: document.getElementById('close-results'),
        status: document.getElementById('result-status'),
        details: document.getElementById('result-details'),
        summary: document.querySelector('.result-summary'),
        metrics: document.querySelector('.result-metrics')
    },
    models: {
        refreshBtn: document.getElementById('refresh-models-btn'),
        trainBtn: document.getElementById('train-models-btn'),
        sickleCell: document.getElementById('sickle-cell-models'),
        breastCancer: document.getElementById('breast-cancer-models')
    },
    selectors: {
        disease: document.getElementById('disease-select'),
        version: document.getElementById('version-select'),
        directDisease: document.getElementById('direct-disease-select')
    }
};

// Application state
const appState = {
    modelVersions: {},
    currentAnalysis: null,
    validationRules: {
        sequence: {
            minLength: 50,
            validBases: new Set('ATGC')
        }
    }
};

// Event listeners setup
function setupEventListeners() {
    // Tab switching
    DOM.tabs.buttons.forEach(button => {
        button.addEventListener('click', () => {
            const tabId = button.getAttribute('data-tab');
            switchTab(tabId);
        });
    });
    
    // File input change
    DOM.inputs.file.addEventListener('change', handleFileSelection);
    
    // Sequence input change
    DOM.inputs.sequence.addEventListener('input', updateSequenceStats);
    
    // Form submissions
    DOM.forms.upload.addEventListener('submit', handleFileUpload);
    DOM.forms.sequence.addEventListener('submit', handleDirectSequence);
    
    // Close results
    DOM.results.closeBtn.addEventListener('click', () => {
        DOM.results.container.classList.add('hidden');
    });
    
    // Model info controls
    DOM.models.refreshBtn.addEventListener('click', loadModelInfo);
    DOM.models.trainBtn.addEventListener('click', trainModels);
    
    // Disease selection change - update version options
    DOM.selectors.disease.addEventListener('change', updateVersionOptions);
}

// File selection handler
function handleFileSelection() {
    if (DOM.inputs.file.files.length > 0) {
        const file = DOM.inputs.file.files[0];
        DOM.inputs.fileName.textContent = file.name;
        
        // Validate file extension
        const validExtensions = ['.fasta', '.fa', '.csv'];
        const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        
        if (!validExtensions.includes(fileExt)) {
            DOM.inputs.fileName.innerHTML += ' <span style="color: red;">(Unsupported file type)</span>';
        }
    } else {
        DOM.inputs.fileName.textContent = 'No file selected';
    }
}

// Tab switching logic
function switchTab(tabId) {
    // Update tab buttons
    DOM.tabs.buttons.forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
    });
    
    // Update tab content
    DOM.tabs.contents.forEach(content => {
        content.classList.toggle('active', content.id === tabId);
    });
}

// Update sequence statistics with validation
function updateSequenceStats() {
    const sequence = DOM.inputs.sequence.value.trim().toUpperCase();
    const length = sequence.length;
    DOM.inputs.sequenceStats.textContent = `Length: ${length} bases`;
    
    if (length === 0) return;
    
    // Validate sequence
    let isValid = true;
    let invalidChars = [];
    
    for (const base of sequence) {
        if (!appState.validationRules.sequence.validBases.has(base)) {
            isValid = false;
            if (!invalidChars.includes(base)) invalidChars.push(base);
        }
    }
    
    // Display validation results
    if (!isValid) {
        DOM.inputs.sequenceStats.innerHTML += ` <span style="color: red;">(Invalid characters: ${invalidChars.join(', ')})</span>`;
    }
    
    // Length validation
    if (length < appState.validationRules.sequence.minLength) {
        DOM.inputs.sequenceStats.innerHTML += ` <span style="color: orange;">(Sequence too short, min: ${appState.validationRules.sequence.minLength})</span>`;
    }
}

// Handle file upload submission
async function handleFileUpload(e) {
    e.preventDefault();
    
    const file = DOM.inputs.file.files[0];
    if (!file) {
        showNotification('Please select a file to analyze', 'warning');
        return;
    }
    
    // Show loading state
    showLoadingResults();
    
    const formData = new FormData();
    formData.append('file', file);
    
    const diseaseType = DOM.selectors.disease.value;
    const version = DOM.selectors.version.value;
    
    try {
        let endpoint = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PREDICT}?analysis_type=${diseaseType}`;
        
        if (version !== 'latest') {
            endpoint = `${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.PREDICT}${diseaseType}/${version}/`;
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server error (${response.status}): ${errorText || response.statusText}`);
        }
        
        const result = await response.json();
        displayResults(result);
    } catch (error) {
        displayError(error);
        console.error('API Error:', error);
    }
}

// Handle direct sequence submission
async function handleDirectSequence(e) {
    e.preventDefault();
    
    const sequence = DOM.inputs.sequence.value.trim();
    if (sequence.length < appState.validationRules.sequence.minLength) {
        showNotification(`Sequence must be at least ${appState.validationRules.sequence.minLength} characters long`, 'warning');
        return;
    }
    
    // Validate sequence
    let invalidChars = [];
    for (const base of sequence.toUpperCase()) {
        if (!appState.validationRules.sequence.validBases.has(base)) {
            if (!invalidChars.includes(base)) invalidChars.push(base);
        }
    }
    
    if (invalidChars.length > 0) {
        showNotification(`Invalid characters detected: ${invalidChars.join(', ')}`, 'warning');
        return;
    }
    
    // Show loading state
    showLoadingResults();
    
    const diseaseType = DOM.selectors.directDisease.value;
    
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.ANALYZE}`, {
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
            const errorText = await response.text();
            throw new Error(`Server error (${response.status}): ${errorText || response.statusText}`);
        }
        
        const result = await response.json();
        displayResults(result);
    } catch (error) {
        displayError(error);
        console.error('API Error:', error);
    }
}

// Show loading state in results container
function showLoadingResults() {
    DOM.results.container.classList.remove('hidden');
    DOM.results.status.classList.remove('hidden');
    DOM.results.details.classList.add('hidden');
}

// Display analysis results
function displayResults(result) {
    // Store current result
    appState.currentAnalysis = result;
    
    // Update UI
    DOM.results.status.classList.add('hidden');
    DOM.results.details.classList.remove('hidden');
    
    let summaryHTML = '';
    let metricsHTML = '<h4>Sequence Details</h4>';
    
    // Summary based on prediction result
    if (result.prediction === 1 || result.has_mutation === true) {
        const confidence = result.probability || result.confidence || 0;
        summaryHTML = `
            <h3 class="positive-result"><i class="fas fa-exclamation-triangle"></i> Positive Detection</h3>
            <p><strong>Analysis:</strong> ${result.disease || result.model_name || 'Genetic Analysis'}</p>
            <p><strong>Confidence:</strong> ${(confidence * 100).toFixed(1)}%</p>
            <p>${result.message || 'Genetic markers detected indicating potential risk.'}</p>
        `;
    } else {
        summaryHTML = `
            <h3 class="negative-result"><i class="fas fa-check-circle"></i> Negative Detection</h3>
            <p><strong>Analysis:</strong> ${result.disease || result.model_name || 'Genetic Analysis'}</p>
            <p>${result.message || 'No concerning genetic markers detected in this analysis.'}</p>
        `;
    }
    
    // Add model details
    if (result.model_details || result.model_info) {
        const modelDetails = result.model_details || result.model_info || {};
        summaryHTML += '<div class="model-info-section"><h4>Model Information</h4>';
        
        for (const [key, value] of Object.entries(modelDetails)) {
            if (typeof value !== 'object') {
                summaryHTML += `<p><strong>${formatKey(key)}:</strong> ${value}</p>`;
            }
        }
        
        summaryHTML += '</div>';
    }
    
    // Metrics display - handle both older and newer API response formats
    if (result.details || result.features) {
        const details = result.details || result.features || {};
        
        for (const [key, value] of Object.entries(details)) {
            if (typeof value === 'object' && value !== null) {
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
        }
    }
    
    DOM.results.summary.innerHTML = summaryHTML;
    DOM.results.metrics.innerHTML = metricsHTML;
}

// Display error in results
function displayError(error) {
    DOM.results.status.classList.add('hidden');
    DOM.results.details.classList.remove('hidden');
    
    DOM.results.summary.innerHTML = `
        <h3 class="warning-result"><i class="fas fa-exclamation-circle"></i> Error</h3>
        <p>There was an error analyzing the sequence:</p>
        <p>${error.message}</p>
    `;
    
    DOM.results.metrics.innerHTML = `
        <p>Please check your input and try again. Make sure:</p>
        <ul>
            <li>The backend server is running at ${API_CONFIG.BASE_URL}</li>
            <li>The file format is supported (FASTA or CSV)</li>
            <li>The sequence contains valid DNA nucleotides (A, T, G, C)</li>
            <li>The sequence is at least ${appState.validationRules.sequence.minLength} characters long</li>
        </ul>
        <p><button class="btn secondary-btn" id="retry-connection">Check Server Connection</button></p>
    `;
    
    // Add event listener for retry button
    document.getElementById('retry-connection').addEventListener('click', checkServerConnection);
}

// Check server connection
async function checkServerConnection() {
    try {
        DOM.results.metrics.innerHTML = '<p>Checking server connection...</p>';
        
        const response = await fetch(`${API_CONFIG.BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            DOM.results.metrics.innerHTML = `
                <p class="success-message">✅ Server connection successful!</p>
                <p>The API is available at ${API_CONFIG.BASE_URL}</p>
                <p>You can try your analysis again.</p>
            `;
        } else {
            DOM.results.metrics.innerHTML = `
                <p class="error-message">❌ Server is responding but returned status ${response.status}</p>
                <p>The API might be running but encountered an issue.</p>
                <p>Check the terminal running the backend for errors.</p>
            `;
        }
    } catch (error) {
        DOM.results.metrics.innerHTML = `
            <p class="error-message">❌ Cannot connect to server at ${API_CONFIG.BASE_URL}</p>
            <p>Error: ${error.message}</p>
            <p>Please make sure the backend server is running:</p>
            <code>cd backend && python run_app.py</code>
        `;
    }
}

// Load model information
async function loadModelInfo() {
    try {
        DOM.models.sickleCell.innerHTML = '<div class="loader"></div>';
        DOM.models.breastCancer.innerHTML = '<div class="loader"></div>';
        
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.MODELS}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Display model info
        displayModelInfo(data.sickle_cell || data.sickle_cell_demo, DOM.models.sickleCell, 'sickle_cell');
        displayModelInfo(data.breast_cancer || data.breast_cancer_demo, DOM.models.breastCancer, 'breast_cancer');
        
        // Update version select options
        updateVersionOptions();
    } catch (error) {
        DOM.models.sickleCell.innerHTML = `<p class="error-message">Error loading model information: ${error.message}</p>`;
        DOM.models.breastCancer.innerHTML = `<p class="error-message">Error loading model information: ${error.message}</p>`;
    }
}

// Display model information
function displayModelInfo(modelData, container, modelType) {
    if (!modelData || Object.keys(modelData).length === 0) {
        container.innerHTML = '<p>No model information available</p>';
        return;
    }
    
    let html = '';
    
    // Current model info
    if (modelData.version || modelData.latest_version) {
        const version = modelData.version || modelData.latest_version;
        const accuracy = modelData.accuracy || modelData.metrics?.accuracy || 0;
        const trainingDate = modelData.training_date || modelData.created_at || 'Unknown';
        
        html += `
            <div class="model-version">
                <h4>Current Model: ${version}</h4>
                <div class="model-metrics">
                    <p><strong>Type:</strong> ${modelData.type || modelData.algorithm || 'Machine Learning Model'}</p>
                    <p><strong>Accuracy:</strong> ${(accuracy * 100).toFixed(1)}%</p>
                    <p><strong>Training Date:</strong> ${formatDate(trainingDate)}</p>
                </div>
            </div>
        `;
    }
    
    // Store model versions for the version selector
    if (modelData.available_versions || modelData.versions) {
        const versions = (modelData.available_versions || modelData.versions || []).map(v => v.version || v);
        appState.modelVersions[modelType] = versions;
    }
    
    // Display available versions
    if (appState.modelVersions[modelType] && appState.modelVersions[modelType].length > 0) {
        html += '<div class="model-versions-list">';
        html += '<h4>Available Versions</h4>';
        html += '<ul>';
        
        appState.modelVersions[modelType].forEach(version => {
            html += `<li>Version ${version}</li>`;
        });
        
        html += '</ul></div>';
    }
    
    container.innerHTML = html;
}

// Update version options in select element
function updateVersionOptions() {
    const selectedDisease = DOM.selectors.disease.value;
    DOM.selectors.version.innerHTML = '<option value="latest">Latest Version</option>';
    
    if (appState.modelVersions && appState.modelVersions[selectedDisease]) {
        appState.modelVersions[selectedDisease].forEach(version => {
            const option = document.createElement('option');
            option.value = version;
            option.textContent = `Version ${version}`;
            DOM.selectors.version.appendChild(option);
        });
    }
}

// Train new models
async function trainModels() {
    try {
        DOM.models.trainBtn.disabled = true;
        DOM.models.trainBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Training...';
        
        const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.TRAIN}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        showNotification(`Models trained successfully: ${result.message}`, 'success');
        
        // Reload model info
        await loadModelInfo();
    } catch (error) {
        showNotification(`Error training models: ${error.message}`, 'error');
    } finally {
        DOM.models.trainBtn.disabled = false;
        DOM.models.trainBtn.innerHTML = '<i class="fas fa-cogs"></i> Train Demo Models';
    }
}

// Show notification message
function showNotification(message, type = 'info') {
    // Check if notification container exists, if not create it
    let notificationContainer = document.getElementById('notification-container');
    
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '1000';
        document.body.appendChild(notificationContainer);
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Add close functionality
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        notification.classList.add('fade-out');
        setTimeout(() => notification.remove(), 300);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

// Helper: Format key names for display
function formatKey(key) {
    return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Helper: Format date
function formatDate(dateString) {
    if (!dateString || dateString === 'Unknown') return 'Unknown';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleString();
    } catch (e) {
        return dateString;
    }
}

// Export model results as JSON
function exportResults() {
    if (!appState.currentAnalysis) {
        showNotification('No analysis results to export', 'warning');
        return;
    }
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appState.currentAnalysis, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "genoscope_analysis.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
}

// Initialize application
function initApp() {
    setupEventListeners();
    loadModelInfo();
    
    // Add export button to results
    const resultHeader = document.querySelector('.result-header');
    if (resultHeader) {
        const exportButton = document.createElement('button');
        exportButton.className = 'btn export-btn';
        exportButton.innerHTML = '<i class="fas fa-download"></i> Export';
        exportButton.addEventListener('click', exportResults);
        resultHeader.appendChild(exportButton);
    }
    
    // Check server connection on startup
    fetch(`${API_CONFIG.BASE_URL}/health`)
        .then(response => {
            if (response.ok) {
                console.log('API server is available');
            }
        })
        .catch(err => {
            console.warn('API server may not be running:', err);
        });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);