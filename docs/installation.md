# Installation Guide

This guide explains how to install and set up the Handyman KPI System.

## Prerequisites

Before installing the KPI system, ensure you have the following:

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for cloning the repository)
- Docker and Docker Compose (optional, for containerized deployment)

## Option 1: Standard Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/skunkbandit/handyman-kpi-system.git
cd handyman-kpi-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

- Windows:
  ```
  venv\Scripts\activate
  ```
- macOS/Linux:
  ```
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database

```bash
flask db init
flask db migrate
flask db upgrade
```

### 5. Run the Application

```bash
flask run
```

The application should now be running at `http://localhost:5000`.

## Option 2: Docker Installation

### 1. Clone or Download the Repository

```bash
git clone https://github.com/skunkbandit/handyman-kpi-system.git
cd handyman-kpi-system
```

### 2. Build and Start the Container

```bash
docker-compose up -d
```

The application should now be running at `http://localhost:5000`.

## Initial Setup

After installation, you'll need to create an admin user to access the system. Visit `http://localhost:5000/setup` in your browser to create the first admin account.

## Data Import

To import data from the provided Excel file:

1. Log in as an admin
2. Navigate to Admin > Maintenance
3. Select "Import Data" and upload your Excel file
4. Follow the on-screen instructions to complete the import

## Configuration Options

The application can be configured using environment variables:

- `FLASK_ENV`: Set to `development` for debug mode, `production` for production mode
- `SECRET_KEY`: Secret key for session encryption
- `DATABASE_URL`: Database connection URL (defaults to SQLite)
- `UPLOAD_FOLDER`: Path for file uploads
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

## Troubleshooting

If you encounter any issues during installation:

1. Check the logs in the `instance/logs` directory
2. Ensure all prerequisites are correctly installed
3. Verify that the correct Python version is being used
4. Check file permissions for the `instance` directory

For further assistance, please contact the system administrator.
