# Backup and Restore Guide

This guide covers how to back up and restore the Handyman KPI System to ensure data safety and business continuity.

## Table of Contents

- [Backup Overview](#backup-overview)
- [Automated Backup Configuration](#automated-backup-configuration)
- [Manual Backup Procedures](#manual-backup-procedures)
- [Backup Storage Best Practices](#backup-storage-best-practices)
- [Restoring from Backup](#restoring-from-backup)
- [Disaster Recovery](#disaster-recovery)
- [Backup Verification](#backup-verification)

## Backup Overview

The Handyman KPI System includes comprehensive backup functionality for:

- Database contents (employees, evaluations, skills, tools)
- System configuration settings
- User accounts and permissions
- Custom reports and templates
- Document attachments (if enabled)

All backups are timestamped and include metadata about the system version and content.

## Automated Backup Configuration

The system can perform scheduled automatic backups at configured intervals.

### Configuring via Web Interface

1. Log in with admin credentials
2. Navigate to Admin → System Settings → Backup
3. Configure the following settings:
   - Backup frequency (daily, weekly, monthly)
   - Backup time (when backups should run)
   - Number of backups to retain
   - Backup location (local or remote)
   - Notification settings

### Configuring via Environment Variables

For Docker deployments, you can configure backups in your environment file:

```
# Backup Settings
BACKUP_ENABLED=true
BACKUP_FREQUENCY=daily   # daily, weekly, monthly
BACKUP_TIME=03:00        # 24-hour format
BACKUP_RETENTION=14      # Number of backups to keep
BACKUP_PATH=/app/backups
BACKUP_NOTIFY=true
```

### Remote Backup Configuration

For production environments, it's recommended to store backups on a separate system:

#### AWS S3 Configuration

1. Create an AWS S3 bucket for backups
2. Configure AWS credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=your_region
   BACKUP_S3_BUCKET=your_bucket_name
   BACKUP_S3_PREFIX=kpi-system/backups/
   ```

#### SFTP/SSH Configuration

1. Generate SSH keys for the backup process
2. Configure SSH settings:
   ```
   BACKUP_REMOTE_TYPE=sftp
   BACKUP_REMOTE_HOST=backup-server.example.com
   BACKUP_REMOTE_USER=backup-user
   BACKUP_REMOTE_PATH=/path/to/backups
   BACKUP_SSH_KEY_PATH=/path/to/private_key
   ```

## Manual Backup Procedures

### Using the Web Interface

1. Log in with admin credentials
2. Navigate to Admin → System Maintenance → Backup
3. Click "Create New Backup"
4. Enter a description for the backup
5. Click "Start Backup"
6. Wait for the backup to complete
7. Download the backup file for offline storage

### Using Command Line

For Docker deployment:
```bash
# Create a backup with automatic naming
docker-compose exec web python scripts/backup_database.py

# Create a backup with custom name
docker-compose exec web python scripts/backup_database.py --name "pre_upgrade_backup"
```

For traditional deployment:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create a backup
python scripts/backup_database.py --name "monthly_backup"
```

## Backup Storage Best Practices

To ensure data safety:

1. Follow the 3-2-1 backup strategy:
   - 3 copies of your data
   - 2 different storage types
   - 1 copy stored offsite

2. Secure backup files:
   - Enable encryption for backup files
   - Use secure transfer methods (SFTP, encrypted S3)
   - Regularly rotate access credentials

3. Test backups regularly:
   - Verify backup integrity monthly
   - Perform test restores quarterly
   - Document the restore process

4. Retention policy:
   - Daily backups: keep for 2 weeks
   - Weekly backups: keep for 3 months
   - Monthly backups: keep for 1 year
   - Annual backups: keep for 7 years (or as required by regulations)

## Restoring from Backup

### Using the Web Interface

1. Log in with admin credentials
2. Navigate to Admin → System Maintenance → Backup
3. View the list of available backups
4. Select the backup to restore
5. Click "Restore from Backup"
6. Confirm the restore operation
7. Wait for the restore to complete
8. The system will automatically restart after restore

### Using Command Line

For Docker deployment:
```bash
# List available backups
docker-compose exec web python scripts/list_backups.py

# Restore from a specific backup
docker-compose exec web python scripts/restore_backup.py --file "backup_2025-03-15_03-00-01.zip"
```

For traditional deployment:
```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# List available backups
python scripts/list_backups.py

# Restore from a specific backup
python scripts/restore_backup.py --file "backup_2025-03-15_03-00-01.zip"
```

### Restoring to a Different Environment

To migrate data to a new environment:

1. Create a backup of the source system
2. Install the same version of the KPI system on the target environment
3. Copy the backup file to the target environment
4. Restore using the command line method
5. Verify the data after restore
6. Update any environment-specific settings

## Disaster Recovery

In case of complete system failure:

1. Set up a new instance of the Handyman KPI System
2. Follow the installation guide for your deployment method
3. Before initialization, restore from your most recent backup
4. Verify system functionality
5. Update DNS or access methods to point to the new instance

### Recovery Time Objectives

The system is designed for rapid recovery:

- Database restore: typically less than 5 minutes
- Full system recovery: 15-30 minutes (depending on data size)
- Complete disaster recovery: 1-2 hours (including system reinstallation)

## Backup Verification

Regularly verify your backups:

### Automated Verification

The system automatically verifies backups when created:
- Checks file integrity and size
- Validates database schema
- Tests sample data retrieval

### Manual Verification

Quarterly, perform a full test restore:
1. Create a separate test environment
2. Restore a recent backup
3. Verify application functionality
4. Verify data integrity
5. Document the results

### Backup Reporting

Enable backup reports to receive regular updates:
1. Navigate to Admin → System Settings → Notifications
2. Enable "Backup Status Reports"
3. Configure recipients and frequency
4. Reports include backup success/failure and integrity status

## Troubleshooting Backup Issues

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Backup fails due to disk space | Free up disk space or configure a different backup location |
| Database locked during backup | Increase backup timeout settings or schedule during low-usage period |
| Remote backup connection failure | Check network connectivity and credentials |
| Corrupt backup file | Use an earlier backup; verify storage system integrity |
| Slow backup performance | Optimize database before backup; increase resource allocation |

### Backup Logs

Review backup logs for detailed error information:

```bash
# For Docker deployment
docker-compose exec web cat logs/backup.log

# For traditional deployment
cat logs/backup.log
```

## Appendix: Backup File Structure

Understanding the backup file structure:

```
backup_YYYY-MM-DD_HH-MM-SS.zip
├── metadata.json           # Backup metadata and version info
├── database.sql            # Complete database dump
├── config/                 # System configuration files
│   ├── system_settings.json
│   ├── email_templates/
│   └── report_templates/
├── attachments/            # Document attachments (if any)
└── README.txt              # Information about the backup
```
