/**
 * AI Recruitment Assistant - Main JavaScript
 * 
 * This file contains the main JavaScript functionality for the AI Recruitment Assistant
 * including form handling, file uploads, and UI interactions.
 */

document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    setupFileUpload();
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});

/**
 * Set up the file upload functionality
 */
function setupFileUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const resumeFiles = document.getElementById('resumeFiles');
    
    if (!uploadArea || !resumeFiles) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });

    // Remove highlight when item is dragged away
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    uploadArea.addEventListener('drop', handleDrop, false);
    
    // Handle file selection via the file input
    resumeFiles.addEventListener('change', handleFiles, false);
    
    // Handle click on upload area
    uploadArea.addEventListener('click', () => {
        resumeFiles.click();
    });
}

/**
 * Prevent default drag and drop behavior
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Highlight drop area
 */
function highlight() {
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) uploadArea.classList.add('border-primary', 'bg-light');
}

/**
 * Remove highlight from drop area
 */
function unhighlight() {
    const uploadArea = document.getElementById('uploadArea');
    if (uploadArea) uploadArea.classList.remove('border-primary', 'bg-light');
}

/**
 * Handle dropped files
 */
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

/**
 * Handle selected files
 */
function handleFiles(files) {
    const fileList = document.getElementById('fileList');
    const uploadForm = document.getElementById('uploadForm');
    
    if (!fileList || !files) return;
    
    // Clear file list if this is a new selection
    if (files.length > 0) {
        fileList.innerHTML = '';
    }
    
    // Display each file
    Array.from(files).forEach(file => {
        // Get file extension
        const extension = file.name.split('.').pop().toLowerCase();
        
        // Check if file type is allowed
        if (['pdf', 'docx', 'txt'].indexOf(extension) === -1) {
            showAlert('File type not supported: ' + file.name, 'danger');
            return;
        }
        
        // Create file item element
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item d-flex align-items-center p-2 mb-2 bg-light rounded';
        
        // Determine icon based on file type
        let fileIcon;
        if (extension === 'pdf') {
            fileIcon = 'fa-file-pdf text-danger';
        } else if (extension === 'docx') {
            fileIcon = 'fa-file-word text-primary';
        } else {
            fileIcon = 'fa-file-alt text-secondary';
        }
        
        fileItem.innerHTML = `
            <i class="fas ${fileIcon} me-2"></i>
            <span class="me-auto">${file.name}</span>
            <button type="button" class="btn btn-sm btn-outline-danger remove-file" aria-label="Remove file">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        fileList.appendChild(fileItem);
        
        // Add remove button functionality
        fileItem.querySelector('.remove-file').addEventListener('click', function() {
            fileItem.remove();
            
            // Check if there are any files left
            if (fileList.children.length === 0) {
                disableSubmitButton();
            }
        });
    });
    
    // Enable the submit button if files were uploaded
    if (fileList.children.length > 0) {
        enableSubmitButton();
    } else {
        disableSubmitButton();
    }
}

/**
 * Enable the submit button
 */
function enableSubmitButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) analyzeBtn.disabled = false;
}

/**
 * Disable the submit button
 */
function disableSubmitButton() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) analyzeBtn.disabled = true;
}

/**
 * Show an alert message
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show`;
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Get the container to insert the alert
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertContainer, container.firstChild);
    }
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertContainer.classList.remove('show');
        setTimeout(() => {
            alertContainer.remove();
        }, 150);
    }, 5000);
}
