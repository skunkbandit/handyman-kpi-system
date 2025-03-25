# API Reference Documentation

The Handyman KPI System provides a comprehensive REST API for integrating with other systems and developing custom extensions.

## Table of Contents

- [API Overview](#api-overview)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Versioning](#versioning)
- [Endpoints](#endpoints)
- [Examples](#examples)

## API Overview

The API follows RESTful principles and uses HTTP methods and status codes as defined in the HTTP specification:

- `GET`: Retrieve resources
- `POST`: Create new resources
- `PUT`: Update existing resources (full replacement)
- `PATCH`: Partially update existing resources
- `DELETE`: Remove resources

All requests and responses use JSON for data formatting.

## Authentication

API requests must be authenticated using one of these methods:

### API Key Authentication

For system-to-system integrations:

1. Generate an API key in Admin → API Management → API Keys
2. Include the key in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

### JWT Authentication

For user-context operations:

1. Authenticate with username/password to obtain a JWT token:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

2. Include the token in the `Authorization` header:

```
Authorization: Bearer your-jwt-token-here
```

JWTs expire after 60 minutes and will need to be refreshed:

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "your-refresh-token-here"
}
```

## Response Format

All API responses follow this structure:

```json
{
  "status": "success",
  "message": "Optional message",
  "data": {
    // Resource data or null
  },
  "metadata": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

For error responses:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful request with no response body
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication failure
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

Common error codes include:

- `INVALID_PARAMETERS`: Request parameters are invalid
- `VALIDATION_ERROR`: Data validation failed
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `PERMISSION_DENIED`: User lacks required permissions
- `AUTHENTICATION_FAILED`: Invalid credentials
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Unexpected server error

## Rate Limiting

API requests are rate-limited to prevent abuse:

- 100 requests per minute for authenticated users
- 20 requests per minute for anonymous requests

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1616000000
```

When the rate limit is exceeded, a `429 Too Many Requests` status is returned.

## Versioning

The API uses URL versioning:

```
/api/v1/employees
```

Major version changes may introduce breaking changes. Minor updates are backward-compatible.

## Endpoints

The API is organized into these resource groups:

- [Authentication](authentication.md): User authentication and token management
- [Employees](employees.md): Employee data management
- [Evaluations](evaluations.md): Evaluation creation and retrieval
- [Skills](skills.md): Skill categories and individual skills
- [Tools](tools.md): Tool categories and individual tools
- [Reports](reports.md): Report generation and management
- [Admin](admin.md): Administrative operations (admin-only)

## Examples

### Listing Employees

Request:
```http
GET /api/v1/employees?tier_level=3
Authorization: Bearer your-jwt-token-here
```

Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Smith",
      "tier_level": 3,
      "hire_date": "2023-05-15",
      "active": true
    },
    {
      "id": 2,
      "first_name": "Jane",
      "last_name": "Doe",
      "tier_level": 3,
      "hire_date": "2023-07-20",
      "active": true
    }
  ],
  "metadata": {
    "page": 1,
    "per_page": 20,
    "total": 2
  }
}
```

### Creating an Evaluation

Request:
```http
POST /api/v1/evaluations
Content-Type: application/json
Authorization: Bearer your-jwt-token-here

{
  "employee_id": 1,
  "evaluation_date": "2025-03-15",
  "evaluation_type": "manager",
  "skills": [
    {"skill_id": 101, "rating": 4, "notes": "Good progress"},
    {"skill_id": 102, "rating": 5, "notes": "Excellent work"}
  ],
  "tools": [
    {"tool_id": 201, "can_operate": true, "truck_stock": true},
    {"tool_id": 202, "can_operate": true, "truck_stock": false}
  ],
  "notes": "Overall excellent performance"
}
```

Response:
```json
{
  "status": "success",
  "message": "Evaluation created successfully",
  "data": {
    "id": 123,
    "employee_id": 1,
    "evaluation_date": "2025-03-15",
    "evaluation_type": "manager",
    "created_at": "2025-03-15T14:30:00Z"
  }
}
```

### Error Example

Request:
```http
GET /api/v1/employees/999
Authorization: Bearer your-jwt-token-here
```

Response:
```json
{
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Employee with ID 999 not found",
    "details": {
      "resource_type": "Employee",
      "resource_id": "999"
    }
  }
}
```

## API Client Libraries

Official client libraries for common languages:

- [Python Client](https://github.com/skunkbandit/handyman-kpi-python-client)
- [JavaScript Client](https://github.com/skunkbandit/handyman-kpi-js-client)

## Webhooks

The system can send event notifications to configured webhook endpoints:

1. Configure webhooks in Admin → API Management → Webhooks
2. Select events to trigger webhooks
3. Specify the destination URL and authentication

Events include:
- `employee.created`
- `employee.updated`
- `evaluation.submitted`
- `user.created`

Webhook payloads follow the same format as API responses.
