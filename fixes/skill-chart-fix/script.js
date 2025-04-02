/**
 * Handyman KPI System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert-dismissible');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Handle skill rating stars
    document.querySelectorAll('.rating-input').forEach(function(input) {
        input.addEventListener('change', function() {
            // Reset all stars in this group
            const groupName = this.name;
            const stars = document.querySelectorAll(`input[name="${groupName}"] + label i`);
            
            stars.forEach(function(star) {
                star.className = 'far fa-star';
            });
            
            // Fill stars up to selected one
            const selectedValue = parseInt(this.value);
            const starsToFill = document.querySelectorAll(`input[name="${groupName}"][value="${selectedValue}"] ~ label i`);
            
            starsToFill.forEach(function(star) {
                star.className = 'fas fa-star';
            });
        });
    });
    
    // Initialize any charts on the page
    initializeCharts();
    
    // Handle window resize to redraw charts
    window.addEventListener('resize', function() {
        // Add a small delay to ensure the layout has adjusted
        setTimeout(function() {
            initializeCharts();
        }, 250);
    });
});

/**
 * Initialize charts on the page
 */
function initializeCharts() {
    // Clear existing charts to prevent duplicates on resize
    Chart.helpers.each(Chart.instances, function(instance) {
        instance.destroy();
    });
    
    // Skill distribution chart
    const skillDistributionCtx = document.getElementById('skillDistributionChart');
    if (skillDistributionCtx) {
        // Check if the chart data is available
        if (typeof skillDistributionData !== 'undefined') {
            new Chart(skillDistributionCtx, {
                type: 'radar',
                data: {
                    labels: skillDistributionData.labels,
                    datasets: [{
                        label: 'Skill Rating',
                        data: skillDistributionData.data,
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                        pointBorderColor: '#fff',
                        pointHoverBackgroundColor: '#fff',
                        pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 1, // Square aspect ratio works best for radar charts
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 5,
                            ticks: {
                                stepSize: 1
                            },
                            pointLabels: {
                                font: {
                                    size: 12
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                padding: 10
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.formattedValue + '/5';
                                }
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Progress over time chart
    const progressChartCtx = document.getElementById('progressChart');
    if (progressChartCtx) {
        // Check if the chart data is available
        if (typeof progressData !== 'undefined') {
            new Chart(progressChartCtx, {
                type: 'line',
                data: {
                    labels: progressData.labels,
                    datasets: progressData.datasets
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    aspectRatio: 2, // Rectangle aspect ratio works well for line charts
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 5,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                padding: 10,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }
    }
}

/**
 * Format a date to a readable string
 * @param {Date} date - The date to format
 * @return {string} Formatted date string
 */
function formatDate(date) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(date).toLocaleDateString(undefined, options);
}

/**
 * Calculate average rating for skills
 * @param {Array} skills - Array of skill objects with ratings
 * @return {number} Average rating
 */
function calculateAverageRating(skills) {
    if (!skills || skills.length === 0) return 0;
    
    const sum = skills.reduce((total, skill) => total + skill.rating, 0);
    return (sum / skills.length).toFixed(1);
}

/**
 * Generate a tier badge HTML based on employee tier
 * @param {string} tier - Employee tier
 * @return {string} HTML for the tier badge
 */
function getTierBadge(tier) {
    const tierClasses = {
        'Apprentice': 'tier-apprentice',
        'Handyman': 'tier-handyman',
        'Craftsman': 'tier-craftsman',
        'Master Craftsman': 'tier-master',
        'Lead Craftsman': 'tier-lead'
    };
    
    const tierClass = tierClasses[tier] || 'tier-apprentice';
    return `<span class="tier-badge ${tierClass}">${tier}</span>`;
}