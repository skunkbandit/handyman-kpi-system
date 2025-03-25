# Handyman KPI System

A comprehensive Key Performance Indicator (KPI) tracking and reporting system for handyman businesses with tiered skill progression.

## Overview

This application helps handyman businesses track employee performance, skill development, and tool proficiency across different categories. It provides a digital replacement for the paper-based evaluation process, allowing for better historical tracking and data-driven decision making.

## Features

- **Employee Management**: Track employee information, tier levels, and progression
- **Skill Evaluation**: Assess employee skills across multiple categories
- **Tool Proficiency**: Track which tools employees can operate and own
- **Performance Dashboard**: Visualize KPIs with charts and statistics
- **Historical Tracking**: Monitor skill development over time
- **Reporting**: Generate reports for performance reviews and planning

## Technology Stack

- **Backend**: Python with Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **UI Framework**: Bootstrap 5
- **Visualization**: Chart.js

## System Requirements

- Python 3.8+
- Flask and dependencies (see requirements.txt)
- Modern web browser with JavaScript enabled

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/handyman-kpi-system.git
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database:
   ```
   python scripts/init_database.py
   ```

5. Import data from Excel (optional):
   ```
   python scripts/import_excel_data.py
   ```

6. Run the application:
   ```
   cd backend
   python run.py
   ```

7. Access the application at http://127.0.0.1:5000/

## Project Structure

- `backend/`: Main application code
  - `app/`: Flask application package
    - `models/`: SQLAlchemy models
    - `routes/`: Route blueprints
    - `static/`: Static assets (CSS, JS)
    - `templates/`: HTML templates
  - `run.py`: Application entry point
- `database/`: Database files and scripts
- `scripts/`: Utility scripts
- `docs/`: Documentation
- `tests/`: Test scripts

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the evaluation system developed by [Client Name]
- Uses [List of open source libraries used]
