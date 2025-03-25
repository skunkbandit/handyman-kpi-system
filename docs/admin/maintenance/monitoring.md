# System Monitoring Guide

This guide covers monitoring the Handyman KPI System to ensure optimal performance, security, and availability.

## Table of Contents

- [Monitoring Overview](#monitoring-overview)
- [Built-in Monitoring Features](#built-in-monitoring-features)
- [External Monitoring Tools](#external-monitoring-tools)
- [Key Performance Indicators](#key-performance-indicators)
- [Alert Configuration](#alert-configuration)
- [Log Management](#log-management)
- [Performance Optimization](#performance-optimization)

## Monitoring Overview

Effective monitoring of the Handyman KPI System helps:

- Ensure system availability and performance
- Identify issues before they affect users
- Track resource usage and capacity needs
- Secure the system against unauthorized access
- Plan for system growth and optimization

## Built-in Monitoring Features

The system includes several built-in monitoring features accessible through the admin interface.

### System Health Dashboard

Access the health dashboard:
1. Log in with admin credentials
2. Navigate to Admin → System Monitoring → Health Dashboard
3. View real-time metrics including:
   - System uptime
   - Database size and performance
   - Active users
   - Response time
   - Error rates
   - Disk usage

### Performance Metrics

Track system performance:
1. Navigate to Admin → System Monitoring → Performance
2. View graphs and statistics for:
   - Page load times
   - Database query performance
   - Memory usage
   - CPU utilization
   - Slowest endpoints
   - Request volume

### User Activity Monitoring

Monitor user activity:
1. Navigate to Admin → System Monitoring → User Activity
2. View:
   - Login history
   - Failed login attempts
   - Page access patterns
   - Feature usage statistics
   - Session duration

### Automated Health Checks

The system performs automated health checks:
- Database connectivity
- Disk space availability
- Cache system status
- Email system connectivity
- Background job execution

## External Monitoring Tools

For production environments, consider integrating with external monitoring tools.

### Prometheus Integration

The system provides Prometheus metrics endpoints:

1. Enable Prometheus in your environment file:
   ```
   ENABLE_PROMETHEUS_METRICS=true
   PROMETHEUS_METRICS_AUTH=true
   PROMETHEUS_METRICS_USERNAME=prometheus
   PROMETHEUS_METRICS_PASSWORD=your_secure_password
   ```

2. Access metrics at: `/metrics` (requires authentication)

3. Configure Prometheus to scrape these metrics:
   ```yaml
   - job_name: 'kpi-system'
     scrape_interval: 15s
     basic_auth:
       username: prometheus
       password: your_secure_password
     static_configs:
       - targets: ['your-kpi-system-host:5000']
   ```

### Grafana Dashboards

The repository includes Grafana dashboard templates:

1. Import the dashboard template from:
   `monitoring/grafana/kpi-system-dashboard.json`

2. Connect to your Prometheus data source

3. Customize alerting thresholds as needed

### Health Check Endpoint

The system provides a health check endpoint for uptime monitoring:

- URL: `/health-check`
- Returns: HTTP 200 OK when system is healthy
- Returns: HTTP 500 when system has issues
- Optional: Add `?details=true` for verbose output

Example integration with monitoring services:
```
# Uptime Robot configuration
URL: https://your-kpi-system.example.com/health-check
Monitoring Interval: 5 minutes
Alert When: Status != 200 OK
```

## Key Performance Indicators

Monitor these key metrics for system health:

### System Metrics

| Metric | Warning Threshold | Critical Threshold | Action |
|--------|-------------------|-------------------|--------|
| CPU Usage | >70% for 15 min | >90% for 5 min | Scale up resources |
| Memory Usage | >80% for 15 min | >90% for 5 min | Investigate memory leaks |
| Disk Usage | >80% | >90% | Clean up or add storage |
| Database Size | >5GB | >10GB | Optimize or archive data |
| Response Time | >500ms avg | >1s avg | Investigate performance issues |

### Application Metrics

| Metric | Warning Threshold | Critical Threshold | Action |
|--------|-------------------|-------------------|--------|
| Failed Logins | >5 in 10 min | >20 in 10 min | Check for attack attempts |
| Error Rate | >1% of requests | >5% of requests | Check application logs |
| Active Sessions | >100 | >200 | Check for unusual activity |
| Database Queries | >1000/min | >5000/min | Optimize queries |
| Backup Failure | Any failure | >24h without backup | Investigate backup system |

## Alert Configuration

Configure alerts to notify administrators of potential issues.

### Email Alerts

Configure email notifications:
1. Navigate to Admin → System Monitoring → Alert Settings
2. Enter email addresses for notifications
3. Configure alert thresholds
4. Test the notification system

### Webhook Integration

For integration with tools like Slack, Microsoft Teams, or PagerDuty:
1. Navigate to Admin → System Monitoring → Alert Settings → Webhooks
2. Add your webhook URL
3. Configure the payload format
4. Test the webhook

### Alert Severity Levels

Understand alert severity levels:
- **Info**: System events that don't require action
- **Warning**: Issues that may need attention soon
- **Error**: Problems that require prompt attention
- **Critical**: Severe issues that need immediate action

## Log Management

Effectively manage system logs for troubleshooting and auditing.

### Accessing Logs

View logs through the admin interface:
1. Navigate to Admin → System Monitoring → Logs
2. Filter logs by:
   - Log level (INFO, WARNING, ERROR, etc.)
   - Date range
   - Source component
   - User actions

### Log Files Location

Log files are stored in the following locations:

For Docker deployment:
- Container logs: `docker-compose logs web`
- Application logs: Inside the container at `/app/logs/`

For traditional deployment:
- Application logs: `logs/` directory in the installation folder
- Access logs: Configured in your web server (NGINX/Apache)

### Log Rotation

Logs are automatically rotated to prevent disk space issues:
- Daily rotation
- Compression of old logs
- 30-day retention by default

Customize log rotation:
1. Navigate to Admin → System Settings → Logging
2. Configure retention period and rotation settings

### External Log Integration

For centralized logging, configure integration with:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Graylog
- Splunk
- AWS CloudWatch

Configuration example for ELK in the environment file:
```
LOG_FORMAT=json
ENABLE_LOGSTASH=true
LOGSTASH_HOST=your-logstash-host
LOGSTASH_PORT=5044
```

## Performance Optimization

Regularly optimize the system for best performance.

### Database Optimization

Run database maintenance tasks:
1. Navigate to Admin → System Maintenance → Database
2. Schedule or run manual optimizations:
   - Vacuum (reclaims storage)
   - Analyze (updates statistics)
   - Reindex (improves query performance)

### Cache Management

Manage the system's cache:
1. Navigate to Admin → System Maintenance → Cache
2. View cache statistics
3. Clear specific caches if needed
4. Adjust cache settings for your environment

### Resource Scaling

For Docker deployments, scale resources as needed:
```bash
# Increase memory allocation in docker-compose.yml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

For traditional deployments:
- Increase uWSGI/Gunicorn worker count
- Add a Redis cache for session storage
- Optimize database connection pool settings

## Troubleshooting Common Issues

| Issue | Monitoring Indicator | Solution |
|-------|----------------------|----------|
| Slow performance | High response times | Check database queries, increase resources |
| Memory leaks | Steadily increasing memory usage | Restart service, update application |
| Database deadlocks | Error logs with "deadlock" messages | Optimize database access patterns |
| High CPU usage | Sustained CPU usage >90% | Identify resource-intensive operations |
| Authentication failures | Multiple failed login attempts | Check for brute force attempts, enable rate limiting |

## Appendix: Monitoring Checklist

### Daily Monitoring Tasks
- Check system health dashboard
- Review error logs
- Verify successful backups
- Monitor disk space usage
- Check for failed login attempts

### Weekly Monitoring Tasks
- Review performance trends
- Check database growth
- Analyze user activity patterns
- Verify external integrations
- Test alert system

### Monthly Monitoring Tasks
- Run database optimization tasks
- Review security logs
- Test system recovery procedures
- Update monitoring thresholds
- Review and update alert recipients
