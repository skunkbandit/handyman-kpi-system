# Docker Deployment Guide

This guide covers deploying the Handyman KPI System using Docker and Docker Compose, which is the recommended method for production deployments.

## Prerequisites

Before you begin, ensure you have:

- A server or VM with at least:
  - 2 CPU cores
  - 4GB RAM
  - 20GB free disk space
- Docker Engine (version 19.03 or later)
- Docker Compose (version 1.27 or later)
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/skunkbandit/handyman-kpi-system.git
cd handyman-kpi-system
```

### 2. Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
cp .env.example .env
```

Edit the `.env` file to set your environment-specific configuration:

```bash
# Security Settings
SECRET_KEY=generate_a_secure_random_key_here
ADMIN_PASSWORD=your_secure_admin_password

# Database Configuration
DATABASE_URI=sqlite:///instance/database/kpi.db
BACKUP_RETENTION_DAYS=14

# Application Settings
FLASK_ENV=production
LOG_LEVEL=INFO
TIMEZONE=UTC

# System Customization
COMPANY_NAME=Your Handyman Business
SYSTEM_TITLE=Craftsman KPI System
```

Important: Generate a strong random key for `SECRET_KEY` and set a secure `ADMIN_PASSWORD`.

### 3. SSL/TLS Certificate Setup

For production deployment, SSL/TLS is required. Place your certificates in the `nginx/ssl` directory:

```bash
mkdir -p nginx/ssl
# Copy your certificates or generate self-signed ones
# Example for self-signed (NOT recommended for production):
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/server.key -out nginx/ssl/server.crt
```

For production, use certificates from a trusted certificate authority.

### 4. Build and Start the Containers

```bash
docker-compose build
docker-compose up -d
```

This will:
- Build the application container
- Start all services (app, nginx, redis, backup-service)
- Create necessary volumes for persistent data
- Configure networking between containers

### 5. Initialize the Database

Once the containers are running, you need to initialize the database:

```bash
docker-compose exec kpi-app python -m scripts.migrate_database
docker-compose exec kpi-app python -m scripts.seed_database
```

### 6. Verify Deployment

Check that all containers are running:

```bash
docker-compose ps
```

All services should show a status of "Up".

Access the application at `https://your-server-ip` or your configured domain name.

## Container Structure

The Docker Compose deployment includes:

- **kpi-app**: Main application container running Flask with Gunicorn
- **redis**: Redis container for caching and session management
- **backup-service**: Container for scheduled database backups
- **nginx**: NGINX container for serving static files and as a reverse proxy

## Data Persistence

Docker volumes are used for data persistence:

- **kpi-data**: Contains database files, backups, logs, and temporary files
- **redis-data**: Contains Redis data

These volumes persist even if containers are removed or recreated.

## Configuration Options

### Scaling the Application

To increase the number of application instances:

```bash
docker-compose up -d --scale kpi-app=3
```

Note: When scaling, ensure your server has sufficient resources.

### Customizing Resource Limits

Edit the `docker-compose.yml` file to adjust resource limits:

```yaml
services:
  kpi-app:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Environment-Specific Configuration

For different environments (development, testing, production), use different environment files:

```bash
# Development
docker-compose --env-file environments/.env.development up -d

# Testing
docker-compose --env-file environments/.env.testing up -d

# Production
docker-compose --env-file environments/.env.production up -d
```

## Maintenance Operations

### Viewing Logs

```bash
# All containers
docker-compose logs

# Specific container
docker-compose logs kpi-app

# Follow logs
docker-compose logs -f
```

### Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart containers
docker-compose down
docker-compose build
docker-compose up -d

# Migrate database if needed
docker-compose exec kpi-app python -m scripts.migrate_database
```

### Database Backup and Restore

The backup-service container automatically creates daily backups.

**Manual backup:**

```bash
docker-compose exec kpi-app python -m scripts.backup_database
```

**Restore from backup:**

```bash
docker-compose exec kpi-app python -m scripts.restore_database --file=kpi_backup_20250321_123456.db
```

### Monitoring

Check container health:

```bash
docker-compose ps
docker stats
```

The application exposes a health endpoint at `/health` that returns status information.

## Troubleshooting

### Container Startup Issues

If containers fail to start:

```bash
# Check for errors
docker-compose logs

# Start in foreground mode
docker-compose up
```

### Database Issues

If you encounter database problems:

```bash
# Check database integrity
docker-compose exec kpi-app python -m scripts.check_database

# Repair database if needed
docker-compose exec kpi-app python -m scripts.repair_database
```

### Application Access Issues

If you can't access the application:

1. Verify all containers are running: `docker-compose ps`
2. Check NGINX logs: `docker-compose logs nginx`
3. Ensure ports are correctly mapped in docker-compose.yml
4. Verify SSL certificates are correctly configured

## Uninstallation

To completely remove the application:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [NGINX Documentation](https://nginx.org/en/docs/)
