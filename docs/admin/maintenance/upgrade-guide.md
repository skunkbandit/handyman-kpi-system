# System Upgrade Guide

This guide covers how to safely upgrade the Handyman KPI System to newer versions while minimizing downtime and ensuring data integrity.

## Table of Contents

- [Upgrade Overview](#upgrade-overview)
- [Pre-Upgrade Preparations](#pre-upgrade-preparations)
- [Upgrade Process](#upgrade-process)
  - [Docker Deployment Upgrade](#docker-deployment-upgrade)
  - [Traditional Deployment Upgrade](#traditional-deployment-upgrade)
- [Post-Upgrade Tasks](#post-upgrade-tasks)
- [Rolling Back an Upgrade](#rolling-back-an-upgrade)
- [Version-Specific Notes](#version-specific-notes)

## Upgrade Overview

The Handyman KPI System follows semantic versioning (MAJOR.MINOR.PATCH):

- **PATCH** upgrades (e.g., 1.2.3 to 1.2.4): Bug fixes and minor improvements
- **MINOR** upgrades (e.g., 1.2.0 to 1.3.0): New features with backward compatibility
- **MAJOR** upgrades (e.g., 1.0.0 to 2.0.0): Significant changes, may require additional steps

Recommendations:
- PATCH upgrades: Can usually be applied immediately
- MINOR upgrades: Test in a staging environment first
- MAJOR upgrades: Requires careful planning and testing

## Pre-Upgrade Preparations

Before upgrading, complete these preparations:

### 1. Review Release Notes

1. Check the latest release notes on GitHub
2. Pay attention to:
   - Breaking changes
   - Database migrations
   - New dependencies
   - Deprecated features

### 2. Create a Complete Backup

Create a full system backup:

```bash
# For Docker deployment
docker-compose exec web python scripts/backup_database.py --name "pre_upgrade_v1_3_0"

# For traditional deployment
python scripts/backup_database.py --name "pre_upgrade_v1_3_0"
```

### 3. Plan for Downtime

Most upgrades require brief downtime. Plan accordingly:
- Schedule during low-usage periods
- Notify users in advance
- Estimate downtime based on upgrade complexity
- For mission-critical deployments, consider a blue/green deployment strategy

### 4. Verify System Health

Ensure the current system is functioning properly:

1. Navigate to Admin → System Monitoring → Health Check
2. Verify all checks pass
3. Fix any issues before proceeding with the upgrade

### 5. Test in Staging

For MINOR and MAJOR upgrades, test in a staging environment:

1. Create a staging environment that mirrors production
2. Restore a recent production backup to staging
3. Perform the upgrade on staging
4. Test all critical functionality
5. Document any issues and solutions

## Upgrade Process

### Docker Deployment Upgrade

For Docker-based deployments, follow these steps:

#### 1. Stop the Current Containers

```bash
docker-compose down
```

#### 2. Back Up the Data Volume

```bash
# Create a backup directory
mkdir -p backup/$(date +%Y-%m-%d)

# Copy data volumes
cp -r ./data ./backup/$(date +%Y-%m-%d)/
cp -r ./database ./backup/$(date +%Y-%m-%d)/
cp .env ./backup/$(date +%Y-%m-%d)/
```

#### 3. Pull the Latest Version

```bash
# Update repository
git pull origin main

# Or checkout a specific version
git fetch --tags
git checkout v1.3.0
```

#### 4. Review Configuration Changes

```bash
# Compare your .env with the new template
diff -u environments/.env.production .env
```

Update your `.env` file with any new configuration parameters.

#### 5. Start the Updated System

```bash
docker-compose up -d
```

#### 6. Run Database Migrations

```bash
docker-compose exec web python scripts/migrate_database.py
```

#### 7. Verify the Upgrade

```bash
# Check the system version
docker-compose exec web python -c "from app import version; print(version)"

# Check system health
curl http://localhost:8080/health-check?details=true
```

### Traditional Deployment Upgrade

For traditional deployments, follow these steps:

#### 1. Enable Maintenance Mode

```bash
python scripts/maintenance.py --enable --message "System upgrade in progress"
```

#### 2. Back Up Current Installation

```bash
# Create a backup directory
mkdir -p backup/$(date +%Y-%m-%d)

# Back up code and data
cp -r ./ backup/$(date +%Y-%m-%d)/
```

#### 3. Update Code

```bash
# Update repository
git pull origin main

# Or checkout a specific version
git fetch --tags
git checkout v1.3.0
```

#### 4. Update Dependencies

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Update dependencies
pip install -r requirements.txt
```

#### 5. Update Configuration

```bash
# Compare your .env with the new template
diff -u environments/.env.production .env
```

Update your `.env` file with any new configuration parameters.

#### 6. Run Database Migrations

```bash
python scripts/migrate_database.py
```

#### 7. Restart Services

```bash
# For systemd deployments
sudo systemctl restart kpi-system

# For other deployments, restart the WSGI server
```

#### 8. Disable Maintenance Mode

```bash
python scripts/maintenance.py --disable
```

#### 9. Verify the Upgrade

```bash
# Check the system version
python -c "from app import version; print(version)"

# Check system health
curl http://localhost:5000/health-check?details=true
```

## Post-Upgrade Tasks

After upgrading, complete these tasks:

### 1. Verify System Functionality

1. Test critical functionality:
   - Login and authentication
   - Employee management
   - Evaluation creation and submission
   - Report generation
   - Data visualization
   - Administrative functions

2. Check for any error messages in:
   - Application logs
   - Browser console
   - Server logs

### 2. Update Documentation

If necessary, update internal documentation to reflect:
- New features
- Changed workflows
- Updated configuration options
- Modified API endpoints

### 3. Clear Caches

Clear system caches to ensure fresh data:

```bash
# For Docker deployment
docker-compose exec web python scripts/clear_caches.py

# For traditional deployment
python scripts/clear_caches.py
```

### 4. Notify Users

Inform users about:
- Completed upgrade
- New features or changes
- Any required user actions
- Known issues and workarounds

## Rolling Back an Upgrade

If issues occur during or after an upgrade, follow these rollback procedures:

### Docker Deployment Rollback

```bash
# Stop the current containers
docker-compose down

# Restore from backup
rm -rf ./data
rm -rf ./database
cp -r ./backup/YYYY-MM-DD/data ./
cp -r ./backup/YYYY-MM-DD/database ./
cp ./backup/YYYY-MM-DD/.env ./

# Checkout the previous version
git checkout v1.2.0

# Start the containers
docker-compose up -d
```

### Traditional Deployment Rollback

```bash
# Enable maintenance mode
python scripts/maintenance.py --enable --message "System restoration in progress"

# Stop services
sudo systemctl stop kpi-system

# Restore from backup
rsync -av --exclude venv --exclude .git backup/YYYY-MM-DD/ ./

# Restart services
sudo systemctl start kpi-system

# Disable maintenance mode
python scripts/maintenance.py --disable
```

## Version-Specific Notes

### Upgrading to v1.3.0

- New dashboard visualizations require additional permissions
- Redis cache now required for production deployments
- Custom report templates will need to be recreated

### Upgrading to v1.2.0

- Database schema changes for tool tracking
- New environment variables for email configuration
- Performance improvements for evaluation processing

### Upgrading to v1.1.0

- Added support for PostgreSQL and MySQL databases
- Improved authentication system
- New API endpoints for reporting

## Appendix: Upgrade Checklist

Use this checklist for all upgrades:

- [ ] Review release notes
- [ ] Create full system backup
- [ ] Verify system health
- [ ] Notify users of planned downtime
- [ ] Stop services or enable maintenance mode
- [ ] Update code/containers
- [ ] Update configuration
- [ ] Run database migrations
- [ ] Start services or disable maintenance mode
- [ ] Verify system functionality
- [ ] Clear caches
- [ ] Notify users of completed upgrade
