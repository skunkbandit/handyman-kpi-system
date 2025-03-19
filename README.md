# Handyman KPI System

A comprehensive performance tracking and evaluation system for handyman businesses with tiered employee structures.

## Overview

This application helps handyman businesses track employee performance across different skill categories and tool proficiencies. It supports the company's five-tier system:
- Apprentice
- Handyman
- Craftsman 
- Master Craftsman
- Lead Craftsman

The system allows for regular evaluations, progress tracking, skill gap analysis, and comprehensive reporting.

## Features

- **Employee Management**: Track employee information, skill levels, and career progression
- **Skill Evaluation**: Rate employee proficiency in various skill categories
- **Tool Proficiency**: Track tools employees can operate and own
- **Performance Dashboard**: Visual analytics of employee and team performance 
- **Comprehensive Reports**: Generate PDF and Excel reports for performance reviews and analysis

## Technical Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Data Visualization**: Chart.js
- **Database**: SQLite (development), MySQL/PostgreSQL (production)
- **Reporting**: WeasyPrint (PDF generation), XlsxWriter (Excel export)

## Project Structure

```
handyman-kpi-system/
├── backend/
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints and views
│   │   ├── static/         # CSS, JS, images
│   │   ├── templates/      # HTML templates
│   │   └── __init__.py     # Application initialization
│   └── run.py              # Application entry point
├── database/
│   ├── schema.sql          # Database schema
│   └── init_data.sql       # Initial data
├── docs/                   # Documentation
└── frontend/               # Front-end assets
```

## Reporting Module

The system provides four main report types:

1. **Employee Performance Report**: Individual employee evaluations for performance reviews
2. **Team Performance Report**: Comparative analysis across employees
3. **Skills Analysis Report**: Deep dive into skill distribution
4. **Tool Inventory Report**: Tool proficiency and ownership tracking

Reports can be exported as PDF documents or Excel spreadsheets for further analysis.

## Installation

### Prerequisites
- Python 3.8+
- pip
- Virtual environment tool (optional but recommended)

### Setup
1. Clone the repository
   ```
   git clone https://github.com/skunkbandit/handyman-kpi-system.git
   cd handyman-kpi-system
   ```

2. Create and activate a virtual environment (optional)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database
   ```
   python setup_db.py
   ```

5. Run the application
   ```
   python backend/run.py
   ```

6. Open a web browser and navigate to `http://localhost:5000`

## Usage

Detailed usage instructions and admin documentation are available in the [User Guide](docs/user_guide.md).

## License

[MIT License](LICENSE)

## Contact

For support or questions, please open an issue on this repository.
