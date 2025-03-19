# Administrator Guide

This guide provides detailed information for system administrators of the Handyman KPI System.

## Administrator Responsibilities

As a system administrator, you are responsible for:

1. User management
2. System configuration
3. Database maintenance
4. Backup and recovery
5. System monitoring and troubleshooting

## User Management

### Creating Users

1. Navigate to Admin > User Management
2. Click "Add New User"
3. Fill in the required information:
   - Username
   - Email address
   - Initial password
   - User role (Admin, Manager, Employee)
4. Click "Create User"

The user will receive an email with instructions to set their password.

### User Roles

The system includes three user roles:

- **Admin**: Full access to all system features, including user management and system configuration
- **Manager**: Access to all employee records, evaluations, and reports
- **Employee**: Limited access to their own profile and evaluations assigned to them

### Resetting Passwords

1. Navigate to Admin > User Management
2. Find the user in the list
3. Click "Reset Password"
4. The user will receive an email with instructions to set a new password

## System Configuration

### System Settings

1. Navigate to Admin > Settings
2. Modify system-wide settings:
   - Company name and logo
   - Email settings
   - Session timeout
   - Password policy
   - Date and time format
3. Click "Save Settings"

### Email Configuration

To configure email notifications:

1. Navigate to Admin > Settings > Email
2. Configure SMTP settings:
   - SMTP server address
   - Port
   - Username
   - Password
   - Encryption type (TLS/SSL)
3. Test the configuration
4. Save settings

## Database Maintenance

### Backup and Restore

#### Creating Backups

1. Navigate to Admin > Maintenance > Backups
2. Click "Create Backup"
3. Enter a description for the backup
4. Click "Create"

Backups are stored in the `instance/backups` directory.

#### Scheduling Automatic Backups

1. Navigate to Admin > Maintenance > Backups
2. Click "Schedule Backups"
3. Configure the backup schedule:
   - Frequency (Daily, Weekly, Monthly)
   - Time of day
   - Retention policy
4. Click "Save Schedule"

#### Restoring from Backup

1. Navigate to Admin > Maintenance > Backups
2. Find the backup to restore
3. Click "Restore"
4. Confirm the restoration

> **Warning**: Restoring from backup will overwrite the current database. This action cannot be undone.

### Database Optimization

1. Navigate to Admin > Maintenance > Optimization
2. Click "Optimize Database"
3. The system will perform:
   - VACUUM: Reclaim unused space
   - ANALYZE: Update statistics
   - Integrity check

### Data Import and Export

#### Importing Data from Excel

1. Navigate to Admin > Maintenance > Import/Export
2. Click "Import from Excel"
3. Upload the Excel file
4. Map the columns to database fields
5. Click "Import"

#### Exporting Data

1. Navigate to Admin > Maintenance > Import/Export
2. Select the data to export:
   - Employees
   - Evaluations
   - Skills and tools
3. Choose the export format (Excel, CSV, SQL)
4. Click "Export"

## System Monitoring

### System Health

The System Health dashboard provides:

- Database statistics
- Storage usage
- User activity metrics
- Application performance

### System Logs

1. Navigate to Admin > Logs
2. View and filter logs by:
   - Log level (INFO, WARNING, ERROR)
   - Date range
   - User
   - Action type
3. Download logs for offline analysis

## Troubleshooting

### Common Issues

#### Authentication Problems

If users cannot log in:
1. Verify the user account exists and is active
2. Check if the password has expired
3. Ensure the user is using the correct credentials
4. Verify email settings if password reset is not working

#### Performance Issues

If the system is slow:
1. Run database optimization
2. Check server resources (CPU, memory, disk)
3. Review recent database growth
4. Consider database indexes for commonly queried data

#### Data Import Failures

If data import fails:
1. Verify the Excel file format
2. Check for required columns
3. Look for data type mismatches
4. Review error logs for specific issues

### Getting Support

For issues that cannot be resolved using this guide, please contact:
- Technical support: support@handymankpi.com
- Development team: dev@handymankpi.com

## Security Considerations

### Access Control

- Regularly review user accounts and permissions
- Remove access for departed employees promptly
- Use strong passwords and change them regularly
- Consider implementing two-factor authentication

### Data Protection

- Regularly backup the database
- Test restoration procedures
- Store backups securely
- Consider encryption for sensitive data

### Audit Trail

The system maintains an audit trail of important actions:
- User login/logout
- Record creation and modification
- Configuration changes
- Admin actions

Review the audit trail regularly to identify unusual activity.
