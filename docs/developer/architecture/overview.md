# System Architecture Overview

This document provides a high-level overview of the Handyman KPI System architecture, describing the major components and their interactions.

## Architectural Style

The Handyman KPI System follows a **layered architecture** with clear separation of concerns:

1. **Presentation Layer** - User interface and API endpoints
2. **Business Logic Layer** - Application services and domain logic
3. **Data Access Layer** - Database models and data storage
4. **Infrastructure Layer** - Cross-cutting concerns like security, logging, and configuration

The system is designed as a modular monolith, with components organized into distinct modules that communicate through well-defined interfaces.

## System Components

### Frontend Components

The frontend is built as a single-page application that communicates with the backend API:

- **User Interface** - HTML/CSS/JavaScript frontend with responsive design
- **Dashboard** - Interactive visualizations and KPI metrics
- **Forms** - User input forms for evaluations and data entry
- **Reports** - Report generation and visualization

### Backend Components

The backend is a Flask application with the following major components:

- **API Layer** - REST API endpoints for frontend communication
- **Authentication System** - User authentication and authorization
- **Business Logic** - Application services and domain logic
- **Data Access** - Database models and data storage
- **Report Engine** - Report generation and processing
- **Job Scheduler** - Background jobs and scheduled tasks

### Data Storage

- **SQLite Database** - Primary data store
- **Redis Cache** - Session storage and caching (optional)
- **File Storage** - Exports, reports, and backups

## Component Interaction

The following diagram illustrates the high-level component interaction:

```
+-------------------+    HTTP    +-------------------+
|                   |  Requests  |                   |
|  Frontend (SPA)   |<---------->|  Backend API      |
|                   |   JSON     |                   |
+-------------------+            +-------------------+
                                         ^
                                         |
                                         v
                               +-------------------+
                               |                   |
                               |  Business Logic   |
                               |                   |
                               +-------------------+
                                         ^
                                         |
                                         v
                               +-------------------+
                               |                   |
                               |  Data Access      |
                               |                   |
                               +-------------------+
                                         ^
                                         |
                                         v
                               +-------------------+
                               |                   |
                               |  Database         |
                               |                   |
                               +-------------------+
```

## Request Flow

A typical request flows through the system as follows:

1. User interacts with the frontend user interface
2. Frontend makes an HTTP request to the backend API
3. API layer validates the request and authenticates the user
4. Request is routed to the appropriate controller
5. Controller delegates to business logic services
6. Services perform the business logic and interact with data models
7. Data models read/write to the database
8. Results flow back up through the layers
9. API formats the response as JSON
10. Frontend receives the response and updates the UI

## Authentication and Authorization

The system uses a token-based authentication system:

1. Users authenticate with username and password
2. The system issues a secure JWT token
3. Frontend includes the token in subsequent requests
4. Backend validates the token and authorizes access based on user roles

## Data Flow Architecture

Data flows through the system following these patterns:

1. **Create/Update Operations:**
   - Frontend validation -> API validation -> Business logic validation -> Data persistence
   
2. **Read Operations:**
   - Database query -> Data transformation -> API response -> Frontend rendering

3. **Report Generation:**
   - Report request -> Data aggregation -> Report formatting -> Download/display

## Deployment Architecture

The system can be deployed in various configurations:

### Docker Deployment (Recommended)
```
+------------------+
|                  |
|  NGINX           |
|  (Reverse Proxy) |
|                  |
+------------------+
         ^
         |
         v
+------------------+     +------------------+
|                  |     |                  |
|  KPI Application |<--->|  Redis           |
|  Container       |     |  Container       |
|                  |     |                  |
+------------------+     +------------------+
         ^
         |
         v
+------------------+
|                  |
|  Backup Service  |
|  Container       |
|                  |
+------------------+
```

### Manual Deployment
```
+------------------+
|                  |
|  NGINX/Apache    |
|  (Web Server)    |
|                  |
+------------------+
         ^
         |
         v
+------------------+
|                  |
|  WSGI Application|
|  (Gunicorn/uWSGI)|
|                  |
+------------------+
         ^
         |
         v
+------------------+
|                  |
|  SQLite Database |
|                  |
+------------------+
```

## Scalability Considerations

The system is designed to scale in the following ways:

1. **Vertical Scaling** - Adding more resources to the application server
2. **Horizontal Scaling** - Running multiple application instances behind a load balancer
3. **Database Scaling** - Migration to a more robust database engine (PostgreSQL/MySQL) for larger deployments

## Security Architecture

Security is implemented at multiple levels:

1. **Network Security** - HTTPS encryption for all communications
2. **Authentication** - Secure token-based authentication
3. **Authorization** - Role-based access control
4. **Data Validation** - Input validation at all layers
5. **SQL Injection Prevention** - Parameterized queries
6. **XSS Prevention** - Content Security Policy and output escaping
7. **CSRF Protection** - Anti-CSRF tokens for state-changing operations

## Error Handling Architecture

The system uses a centralized error handling approach:

1. **Frontend Errors** - Captured and displayed in the UI
2. **API Errors** - Standardized error responses with appropriate HTTP status codes
3. **Application Errors** - Logged with contextual information
4. **Database Errors** - Captured and reported with transaction rollback
5. **Monitoring** - Error rate monitoring and alerting

## Logging and Monitoring

The system includes comprehensive logging and monitoring:

1. **Application Logs** - Detailed application activity logs
2. **Audit Logs** - Record of user actions for compliance
3. **Performance Metrics** - Response times and resource utilization
4. **Health Checks** - Endpoint for monitoring system health
5. **Error Tracking** - Centralized error collection and reporting

## Next Steps

For more detailed information about the system architecture:

- [Component Diagram](components.md) - Details of system components
- [Data Model](data-model.md) - Database schema and entity relationships
- [Technology Stack](tech-stack.md) - Technologies used in the system

For developer setup instructions, see the [Development Environment Setup Guide](../workflow/setup.md).
