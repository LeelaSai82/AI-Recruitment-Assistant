/**
 * AI Recruitment Assistant - Chart Utilities
 * 
 * This file contains utility functions for rendering charts on the analytics page.
 */

/**
 * Generates a random color for chart elements
 * @returns {string} A random RGB color string
 */
function getRandomColor() {
    const r = Math.floor(Math.random() * 200) + 55; // Avoid too dark colors
    const g = Math.floor(Math.random() * 200) + 55;
    const b = Math.floor(Math.random() * 200) + 55;
    return `rgb(${r}, ${g}, ${b})`;
}

/**
 * Generates an array of colors for chart elements
 * @param {number} count - Number of colors to generate
 * @returns {Array} Array of color strings
 */
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        colors.push(getRandomColor());
    }
    return colors;
}

/**
 * Creates and renders a pie chart
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data object
 * @param {Object} options - Chart options
 */
function createPieChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Set default options if not provided
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = ((value / total) * 100).toFixed(1);
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            }
        }
    };
    
    // Merge default options with provided options
    const mergedOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'pie',
        data: data,
        options: mergedOptions
    });
}

/**
 * Creates and renders a bar chart
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data object
 * @param {Object} options - Chart options
 */
function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Set default options if not provided
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                }
            }
        },
        plugins: {
            legend: {
                position: 'top'
            }
        }
    };
    
    // Merge default options with provided options
    const mergedOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: mergedOptions
    });
}

/**
 * Creates and renders a horizontal bar chart
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data object
 * @param {Object} options - Chart options
 */
function createHorizontalBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Set default options if not provided
    const defaultOptions = {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                beginAtZero: true,
                ticks: {
                    precision: 0
                }
            }
        },
        plugins: {
            legend: {
                position: 'top'
            }
        }
    };
    
    // Merge default options with provided options
    const mergedOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: mergedOptions
    });
}

/**
 * Creates and renders a line chart
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} data - Chart data object
 * @param {Object} options - Chart options
 */
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Set default options if not provided
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };
    
    // Merge default options with provided options
    const mergedOptions = { ...defaultOptions, ...options };
    
    // Create chart
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: mergedOptions
    });
}

/**
 * Updates an existing chart with new data
 * @param {Chart} chart - Chart object to update
 * @param {Object} newData - New data for the chart
 */
function updateChart(chart, newData) {
    // Update chart datasets
    chart.data = newData;
    chart.update();
}

/**
 * Formats label for tooltip display
 * @param {Object} tooltipItem - The tooltip item context
 * @returns {string} Formatted tooltip string
 */
function formatTooltipLabel(tooltipItem) {
    const label = tooltipItem.dataset.label || '';
    const value = tooltipItem.raw || 0;
    return `${label}: ${value}`;
}

/**
 * Formats percentage for tooltip display
 * @param {Object} tooltipItem - The tooltip item context
 * @returns {string} Formatted percentage string
 */
function formatTooltipPercentage(tooltipItem) {
    const label = tooltipItem.dataset.label || '';
    const value = tooltipItem.raw || 0;
    const total = tooltipItem.dataset.data.reduce((a, b) => a + b, 0);
    const percentage = ((value / total) * 100).toFixed(1);
    return `${label}: ${percentage}%`;
}
