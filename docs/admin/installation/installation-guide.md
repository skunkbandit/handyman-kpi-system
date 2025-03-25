# Handyman KPI System - Installation Guide

This comprehensive guide covers the installation of the Handyman KPI System in different deployment scenarios. Please choose the appropriate installation method for your environment.

## Table of Contents

- [System Requirements](#system-requirements)
- [Deployment Options](#deployment-options)
  - [Docker Deployment](#docker-deployment)
  - [Traditional Deployment](#traditional-deployment)
- [Database Setup](#database-setup)
- [Initial Configuration](#initial-configuration)
- [Verifying the Installation](#verifying-the-installation)
- [Troubleshooting](#troubleshooting)

## System Requirements

### Docker Deployment
- Docker Engine 20.10.x or higher
- Docker Compose 2.x or higher
- Minimum 2GB RAM allocated to Docker
- 10GB free disk space
- Internet connection for pulling images

### Traditional Deployment
- Python 3.9 or higher
- SQLite 3.30.0 or higher (or PostgreSQL/MySQL for production)
- NGINX or Apache web server
- 2GB RAM minimum
- 5GB free disk space
- pip package manager
- virtualenv (recommended)

## Deployment Options

### Docker Deployment

Docker deployment is the recommended method for all environments, as it ensures consistency across development, testing, and production.

#### Quick Start with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/skunkbandit/handyman-kpi-system.git
   cd handyman-kpi-system
   ```

2. Create environment file from template:
   ```bash
   cp environments/.env.production .env
   ```

3. Edit the `.env` file to customize your settings:
   ```bash
   # Generate a secure secret key
   FLASK_SECRET_KEY=your-secure-key-here
   
   # Configure database (use SQLite by default)
   DATABASE_URL=sqlite:///database/kpi.db
   
   # Configure email settings (if using email notifications)
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USERNAME=your-email@example.com
   MAIL_PASSWORD=your-email-password
   MAIL_USE_TLS=true
   ```

4. Start the containers:
   ```bash
   docker-compose up -d
   ```

5. Initialize the database:
   ```bash
   docker-compose exec web python scripts/init_database.py
   ```

6. Import skills and tools from the Excel template:
   ```bash
   docker-compose exec web python scripts/import_excel_data.py --file "Craftman Developement Score Card.xlsx"
   ```

7. Create the admin user:
   ```bash
   docker-compose exec web python scripts/create_admin.py
   ```

8. Access the system at http://localhost:8080

### Traditional Deployment

For environments where Docker is not available, follow these steps for a traditional deployment.

#### Installing on Linux/macOS

1. Clone the repository:
   ```bash
   git clone https://github.com/skunkbandit/handyman-kpi-system.git
   cd handyman-kpi-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment file from template:
   ```bash
   cp environments/.env.production .env
   ```

5. Edit the `.env` file to customize your settings

6. Initialize the database:
   ```bash
   python scripts/init_database.py
   ```

7. Import skills and tools from the Excel template:
   ```bash
   python scripts/import_excel_data.py --file "Craftman Developement Score Card.xlsx"
   ```

8. Create the admin user:
   ```bash
   python scripts/create_admin.py
   ```

9. Run the application:
   ```bash
   python wsgi.py
   ```

10. For production, set up a web server (NGINX or Apache) and uWSGI/Gunicorn. Example NGINX configuration is provided in the `nginx/conf.d/default.conf` file.

## Database Setup

The system supports multiple database backends, with SQLite as the default for simplicity.

### SQLite (Default)

SQLite requires minimal setup and is suitable for small deployments:

```bash
# The database will be created automatically when running init_database.py
python scripts/init_database.py
```

### PostgreSQL (Recommended for Production)

For larger deployments, PostgreSQL is recommended:

1. Install PostgreSQL:
   ```bash
   # On Ubuntu/Debian
   sudo apt install postgresql postgresql-contrib
   
   # On RHEL/CentOS
   sudo yum install postgresql-server postgresql-contrib
   sudo postgresql-setup initdb
   sudo systemctl start postgresql
   ```

2. Create a database and user:
   ```bash
   sudo -u postgres psql
   postgres=# CREATE DATABASE kpi_system;
   postgres=# CREATE USER kpi_user WITH PASSWORD 'your_password';
   postgres=# GRANT ALL PRIVILEGES ON DATABASE kpi_system TO kpi_user;
   postgres=# \q
   ```

3. Update your `.env` file:
   ```bash
   DATABASE_URL=postgresql://kpi_user:your_password@localhost/kpi_system
   ```

4. Initialize the database:
   ```bash
   python scripts/init_database.py
   ```

### MySQL/MariaDB

The system also supports MySQL/MariaDB:

1. Install MySQL/MariaDB:
   ```bash
   # On Ubuntu/Debian
   sudo apt install mysql-server
   
   # On RHEL/CentOS
   sudo yum install mariadb-server
   sudo systemctl start mariadb
   ```

2. Create a database and user:
   ```bash
   sudo mysql
   mysql> CREATE DATABASE kpi_system;
   mysql> CREATE USER 'kpi_user'@'localhost' IDENTIFIED BY 'your_password';
   mysql> GRANT ALL PRIVILEGES ON kpi_system.* TO 'kpi_user'@'localhost';
   mysql> FLUSH PRIVILEGES;
   mysql> EXIT;
   ```

3. Update your `.env` file:
   ```bash
   DATABASE_URL=mysql://kpi_user:your_password@localhost/kpi_system
   ```

4. Initialize the database:
   ```bash
   python scripts/init_database.py
   ```

## Initial Configuration

After installation, you'll need to configure the system for your specific environment.

### Basic Configuration

1. Log in with the admin account created during installation
2. Navigate to Admin → System Settings
3. Configure the following settings:
   - Company name and contact information
   - Email notification settings
   - Password policy
   - Session timeout settings
   - Backup schedule
   - Default tier levels

### Importing Initial Data

Import your employee data and existing evaluations (if any):

```bash
# For Docker deployment
docker-compose exec web python scripts/import_employees.py --file "your_employee_data.csv"

# For traditional deployment
python scripts/import_employees.py --file "your_employee_data.csv"
```

### Setting Up Authentication

By default, the system uses internal authentication. If you want to use LDAP or another authentication method:

1. Navigate to Admin → Authentication Settings
2. Select your preferred authentication method
3. Configure the required parameters
4. Test the authentication

## Verifying the Installation

Perform these checks to verify your installation:

1. Log in with the admin account
2. Create a test employee record
3. Create a test evaluation
4. Generate a test report
5. Create a database backup
6. Verify that all system features are functioning properly

### Health Check

The system includes a health check endpoint that can be used to monitor the application:

```bash
curl http://your-server/health-check
```

This will return a JSON response with the status of various system components.

## Troubleshooting

### Common Issues

#### Database Connection Issues

- Verify database credentials in your `.env` file
- Check that the database server is running
- Ensure network connectivity between the application and database server
- Check database permissions

#### Import Data Failures

- Verify that your Excel or CSV files match the expected format
- Check for special characters or encoding issues
- Ensure file permissions allow the application to read the files

#### Email Notification Issues

- Verify SMTP server settings
- Check for network restrictions or firewall settings
- Test email connectivity using the admin interface

#### Performance Issues

- For larger deployments, consider scaling with multiple containers
- Optimize database indexes
- Consider using Redis for caching (configured in docker-compose.yml)

### Logs

Check the application logs for more detailed error information:

```bash
# For Docker deployment
docker-compose logs web

# For traditional deployment
cat logs/application.log
```

### Getting Help

If you encounter issues not covered in this guide, please:
1. Check the GitHub repository issues section
2. Review the troubleshooting section in the developer documentation
3. Contact system support

## Next Steps

After installation:
- Review the [Administrator Guide](../README.md) for day-to-day administration tasks
- Set up [backup and restore procedures](../maintenance/backup-restore.md)
- Configure [monitoring and alerts](../maintenance/monitoring.md)
- Review [security best practices](../maintenance/security.md)
