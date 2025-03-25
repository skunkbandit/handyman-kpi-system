# Deployment Checklist

Use this checklist to ensure successful deployment of the Handyman KPI System in a production environment.

## Pre-Deployment Preparation

### System Requirements
- [ ] Verify server meets minimum requirements:
  - [ ] 2+ CPU cores
  - [ ] 4GB+ RAM
  - [ ] 20GB+ free disk space
  - [ ] Linux-based OS (Ubuntu 20.04+ recommended)

### Software Prerequisites
- [ ] Install Docker and Docker Compose:
  ```bash
  sudo apt update
  sudo apt install docker.io docker-compose
  ```
- [ ] Install required system packages:
  ```bash
  sudo apt install git python3-pip nginx openssl
  ```
- [ ] Enable and start Docker service:
  ```bash
  sudo systemctl enable docker
  sudo systemctl start docker
  ```

### SSL/TLS Certificates
- [ ] Obtain SSL certificates for production domain:
  - [ ] Use Let's Encrypt certificates (recommended) or
  - [ ] Purchase commercial certificates or
  - [ ] Generate self-signed certificates (for testing only)
- [ ] Prepare certificate files in PEM format

### Network Configuration
- [ ] Configure firewall to allow required ports:
  - [ ] Port 80 (HTTP)
  - [ ] Port 443 (HTTPS)
- [ ] Set up DNS records for your domain
- [ ] Test network connectivity to/from the server

## Deployment Process

### Repository Setup
- [ ] Clone the repository:
  ```bash
  git clone https://github.com/skunkbandit/handyman-kpi-system.git
  cd handyman-kpi-system
  ```
- [ ] Checkout the stable release tag:
  ```bash
  git checkout v1.0.0
  ```

### Environment Configuration
- [ ] Copy example environment file:
  ```bash
  cp .env.example .env
  ```
- [ ] Configure environment variables:
  - [ ] Generate secure SECRET_KEY
  - [ ] Set strong ADMIN_PASSWORD
  - [ ] Configure DATABASE_URI
  - [ ] Set BACKUP_RETENTION_DAYS (14+ recommended)
  - [ ] Configure COMPANY_NAME and SYSTEM_TITLE
  - [ ] Set appropriate LOG_LEVEL (INFO recommended)
  - [ ] Configure email settings if using notifications

### SSL Certificate Installation
- [ ] Create nginx/ssl directory:
  ```bash
  mkdir -p nginx/ssl
  ```
- [ ] Install SSL certificates:
  ```bash
  cp /path/to/your/certificate.crt nginx/ssl/server.crt
  cp /path/to/your/private.key nginx/ssl/server.key
  ```
- [ ] Set proper permissions:
  ```bash
  chmod 600 nginx/ssl/server.key
  ```

### Docker Configuration
- [ ] Review and customize docker-compose.yml if needed:
  - [ ] Adjust port mappings if required
  - [ ] Configure volume mounts
  - [ ] Set resource limits for containers
- [ ] Build Docker images:
  ```bash
  docker-compose build
  ```

### Database Initialization
- [ ] Start the application:
  ```bash
  docker-compose up -d
  ```
- [ ] Run database migrations:
  ```bash
  docker-compose exec kpi-app python -m scripts.migrate_database
  ```
- [ ] Seed the database:
  ```bash
  docker-compose exec kpi-app python -m scripts.seed_database
  ```

### Initial Verification
- [ ] Check container status:
  ```bash
  docker-compose ps
  ```
- [ ] Verify all containers are running (kpi-app, nginx, redis, backup-service)
- [ ] Check application logs for errors:
  ```bash
  docker-compose logs kpi-app
  ```
- [ ] Access the application via HTTPS
- [ ] Log in with admin credentials
- [ ] Verify dashboard and basic functionality works

## Post-Deployment Configuration

### Security Hardening
- [ ] Change default admin password
- [ ] Configure a strong password policy
- [ ] Enable two-factor authentication if required
- [ ] Review nginx security headers
- [ ] Run a security scan (e.g., OWASP ZAP, Qualys SSL)
- [ ] Implement IP-based access restrictions if needed

### Backup Configuration
- [ ] Verify automatic backups are running:
  ```bash
  docker-compose logs backup-service
  ```
- [ ] Test manual backup creation:
  ```bash
  docker-compose exec kpi-app python -m scripts.backup_database
  ```
- [ ] Set up external backup storage for offsite backups
- [ ] Test the backup restoration process

### Monitoring Setup
- [ ] Configure system monitoring:
  - [ ] Set up container health checks
  - [ ] Configure resource monitoring (CPU, memory, disk)
  - [ ] Set up log aggregation
- [ ] Configure alerting:
  - [ ] Error rate thresholds
  - [ ] Resource usage alerts
  - [ ] SSL certificate expiration reminders
  - [ ] Backup success/failure notifications

### User Onboarding
- [ ] Create initial user accounts:
  - [ ] Admin accounts
  - [ ] Manager accounts
  - [ ] Employee accounts
- [ ] Set up initial data:
  - [ ] Import employee records
  - [ ] Configure skill categories
  - [ ] Set up tool categories
- [ ] Test workflows with sample evaluations

### Documentation
- [ ] Create deployment documentation:
  - [ ] Server configuration details
  - [ ] Access credentials (store securely)
  - [ ] Backup schedule and locations
  - [ ] Monitoring setup
- [ ] Document recovery procedures:
  - [ ] Backup restoration steps
  - [ ] Container restart procedures
  - [ ] Troubleshooting guides

## Maintenance Plan

### Regular Updates
- [ ] Schedule regular maintenance windows
- [ ] Document update procedure:
  ```bash
  git pull
  docker-compose down
  docker-compose build
  docker-compose up -d
  docker-compose exec kpi-app python -m scripts.migrate_database
  ```
- [ ] Plan version upgrade testing procedure

### Backup Verification
- [ ] Schedule regular backup verification:
  - [ ] Validate backup integrity
  - [ ] Test restoration process
  - [ ] Verify offsite backups
- [ ] Document restoration time requirements

### Monitoring Review
- [ ] Schedule regular monitoring review:
  - [ ] Review error patterns
  - [ ] Analyze performance metrics
  - [ ] Check resource utilization trends
- [ ] Update alert thresholds as needed

### Security Review
- [ ] Schedule regular security reviews:
  - [ ] Review access logs
  - [ ] Check for unauthorized access attempts
  - [ ] Update security patches
  - [ ] Review user account activity

## Rollback Plan

### Pre-Deployment Backup
- [ ] Create a full system backup before major updates
- [ ] Document the current system state

### Rollback Procedure
- [ ] Document step-by-step rollback procedure:
  ```bash
  docker-compose down
  git checkout <previous_version_tag>
  docker-compose build
  docker-compose up -d
  docker-compose exec kpi-app python -m scripts.restore_database --file=<backup_file>
  ```

### Failure Criteria
- [ ] Define failure criteria that trigger rollback:
  - [ ] Critical functionality unavailable
  - [ ] Data corruption or loss
  - [ ] Security breach
  - [ ] Performance degradation beyond thresholds

### Communication Plan
- [ ] Document who should be notified in case of issues
- [ ] Prepare communication templates for different scenarios
- [ ] Define escalation paths for critical issues

## Final Checklist

### Deployment Verification
- [ ] All containers running properly
- [ ] Web application accessible via HTTPS
- [ ] Login and authentication working
- [ ] Dashboard displays correctly
- [ ] Evaluations can be created and saved
- [ ] Reports can be generated
- [ ] Data is persisted after container restarts

### Documentation Review
- [ ] Administrator guide reviewed and updated
- [ ] User guide reviewed and updated
- [ ] Deployment documentation complete
- [ ] Maintenance procedures documented

### Handover
- [ ] Train system administrators on maintenance procedures
- [ ] Train managers on system usage
- [ ] Provide user documentation to all users
- [ ] Document support channels and procedures

### First Week Monitoring
- [ ] Schedule daily checks for the first week
- [ ] Monitor system logs for unexpected errors
- [ ] Watch resource utilization for any issues
- [ ] Collect user feedback and address concerns
