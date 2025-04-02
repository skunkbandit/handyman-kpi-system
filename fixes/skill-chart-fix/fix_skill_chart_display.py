#!/usr/bin/env python3
"""
Fix for Skill Rating Distribution Chart Display Issue

This script fixes the display issue with the Skill Rating Distribution radar chart
on the Dashboard page of the Handyman KPI System.

The fix addresses:
1. Improper chart scaling within its container
2. Lack of responsiveness on different screen sizes
3. Poor aspect ratio for the radar chart

Author: Claude
Date: April 2, 2025
"""

import os
import sys
import shutil
import logging
from datetime import datetime
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("skill_chart_fix.log")
    ]
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KPI_SYSTEM_DIR = os.path.join(BASE_DIR, "kpi-system")
BACKEND_DIR = os.path.join(KPI_SYSTEM_DIR, "backend")
APP_DIR = os.path.join(BACKEND_DIR, "app")
STATIC_DIR = os.path.join(APP_DIR, "static")
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")

CSS_FILE = os.path.join(STATIC_DIR, "css", "style.css")
JS_FILE = os.path.join(STATIC_DIR, "js", "script.js")
DASHBOARD_TEMPLATE = os.path.join(TEMPLATES_DIR, "dashboard", "index.html")

BACKUP_DIR = os.path.join(BASE_DIR, "backups", "chart-fix", datetime.now().strftime("%Y%m%d_%H%M%S"))

# CSS content to replace chart container styles
CSS_CHART_CONTAINER = """
/* Chart container */
.chart-container {
    position: relative;
    min-height: 300px;
    width: 100%;
    margin: 0 auto;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Specific styles for radar chart */
.chart-container canvas#skillDistributionChart {
    max-width: 100%;
    max-height: 100%;
}

/* Footer */
"""

# JS content for radar chart configuration
JS_RADAR_CHART_OPTIONS = """                options: {
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
                }"""

# HTML content for improved chart containers
HTML_CHART_CONTAINER = """            <div class="card-body d-flex justify-content-center">
                <div class="chart-container" id="skill-chart-container">
                    <canvas id="skillDistributionChart"></canvas>
                </div>
            </div>"""

# Additional JS script for document ready event
JS_DOCUMENT_READY = """    
    // Ensure charts resize properly when parent container size changes
    document.addEventListener('DOMContentLoaded', function() {
        // Add additional styling to the skill chart container for better sizing
        const skillChartContainer = document.getElementById('skill-chart-container');
        if (skillChartContainer) {
            skillChartContainer.style.maxWidth = '400px';
            skillChartContainer.style.maxHeight = '400px';
        }
    });
"""

def backup_files():
    """Create backups of the files to be modified"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)
    
    logger.info(f"Creating backups in {BACKUP_DIR}")
    if os.path.exists(CSS_FILE):
        shutil.copy2(CSS_FILE, os.path.join(BACKUP_DIR, "style.css.bak"))
    if os.path.exists(JS_FILE):
        shutil.copy2(JS_FILE, os.path.join(BACKUP_DIR, "script.js.bak"))
    if os.path.exists(DASHBOARD_TEMPLATE):
        shutil.copy2(DASHBOARD_TEMPLATE, os.path.join(BACKUP_DIR, "index.html.bak"))
    
    logger.info("Backups created successfully")

def fix_css():
    """Fix the CSS file to improve chart container styling"""
    try:
        if not os.path.exists(CSS_FILE):
            logger.error(f"CSS file not found: {CSS_FILE}")
            return False
        
        with open(CSS_FILE, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Find the chart container style section and replace it
        css_pattern = r'/\* Chart container \*/\s*\.chart-container\s*{[^}]*}.*?/\* Footer \*/'
        css_content_modified = re.sub(css_pattern, CSS_CHART_CONTAINER, css_content, flags=re.DOTALL)
        
        # Also add media queries if not present
        if "@media (min-width: 992px)" not in css_content_modified:
            media_query = """
@media (min-width: 992px) {
    .chart-container {
        min-height: 350px;
    }
}"""
            # Insert before the last closing brace
            css_content_modified = css_content_modified.rstrip() + media_query + "\n}"
        
        with open(CSS_FILE, 'w', encoding='utf-8') as f:
            f.write(css_content_modified)
        
        logger.info("CSS file updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating CSS file: {e}")
        return False

def fix_js():
    """Fix the JavaScript file to improve chart configuration"""
    try:
        if not os.path.exists(JS_FILE):
            logger.error(f"JavaScript file not found: {JS_FILE}")
            return False
        
        with open(JS_FILE, 'r', encoding='utf-8') as f:
            js_content = f.read()
        
        # Add window resize handler
        if "window.addEventListener('resize'" not in js_content:
            resize_handler = """    
    // Handle window resize to redraw charts
    window.addEventListener('resize', function() {
        // Add a small delay to ensure the layout has adjusted
        setTimeout(function() {
            initializeCharts();
        }, 250);
    });
"""
            # Insert after the initializeCharts() call in the DOMContentLoaded event
            js_content = js_content.replace(
                "    initializeCharts();",
                "    initializeCharts();" + resize_handler
            )
        
        # Replace radar chart options
        js_pattern = r'options:\s*{[^{]*scales:\s*{[^{]*r:\s*{[^}]*}[^}]*}[^}]*}'
        js_content = re.sub(js_pattern, JS_RADAR_CHART_OPTIONS, js_content)
        
        # Add chart destruction code
        if "Clear existing charts" not in js_content:
            init_charts_pattern = r'function initializeCharts\(\) {'
            init_charts_replacement = """function initializeCharts() {
    // Clear existing charts to prevent duplicates on resize
    Chart.helpers.each(Chart.instances, function(instance) {
        instance.destroy();
    });
    """
            js_content = re.sub(init_charts_pattern, init_charts_replacement, js_content)
        
        # Add document ready event for chart container styling
        if "// Function to get random colors for chart" in js_content:
            js_content = js_content.replace(
                "// Function to get random colors for chart",
                JS_DOCUMENT_READY + "// Function to get random colors for chart"
            )
        
        with open(JS_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        logger.info("JavaScript file updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating JavaScript file: {e}")
        return False

def fix_html():
    """Fix the HTML template for the chart container"""
    try:
        if not os.path.exists(DASHBOARD_TEMPLATE):
            logger.error(f"Dashboard template not found: {DASHBOARD_TEMPLATE}")
            return False
        
        with open(DASHBOARD_TEMPLATE, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Replace the chart container div in the Skill Rating Distribution card
        html_pattern = r'<div class="card-body">\s*<div class="chart-container">\s*<canvas id="skillDistributionChart"></canvas>\s*</div>\s*</div>'
        html_content = re.sub(html_pattern, HTML_CHART_CONTAINER, html_content)
        
        with open(DASHBOARD_TEMPLATE, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("HTML template updated successfully")
        return True
    except Exception as e:
        logger.error(f"Error updating HTML template: {e}")
        return False

def main():
    logger.info("Starting Skill Rating Distribution Chart Fix")
    
    # Verify paths
    if not os.path.exists(KPI_SYSTEM_DIR):
        logger.error(f"KPI System directory not found: {KPI_SYSTEM_DIR}")
        return 1
    
    # Create backups
    backup_files()
    
    # Apply fixes
    css_success = fix_css()
    js_success = fix_js()
    html_success = fix_html()
    
    if css_success and js_success and html_success:
        logger.info("All fixes applied successfully!")
        return 0
    else:
        logger.error("Not all fixes could be applied")
        return 1

if __name__ == "__main__":
    sys.exit(main())