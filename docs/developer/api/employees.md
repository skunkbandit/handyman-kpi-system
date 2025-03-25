# Employee API Reference

This documentation covers all API endpoints related to employee management.

## Table of Contents

- [Get All Employees](#get-all-employees)
- [Get Employee](#get-employee)
- [Create Employee](#create-employee)
- [Update Employee](#update-employee)
- [Delete Employee](#delete-employee)
- [Get Employee Evaluations](#get-employee-evaluations)
- [Get Employee Skills](#get-employee-skills)
- [Get Employee Tools](#get-employee-tools)
- [Get Employee Special Skills](#get-employee-special-skills)
- [Add Employee Special Skill](#add-employee-special-skill)
- [Update Employee Special Skill](#update-employee-special-skill)
- [Delete Employee Special Skill](#delete-employee-special-skill)

---

## Get All Employees

Retrieves a list of employees with optional filtering.

### Request

```http
GET /api/v1/employees
```

### Query Parameters

| Parameter   | Type    | Description                                     |
|-------------|---------|-------------------------------------------------|
| tier_level  | integer | Filter by tier level (1-5)                      |
| active      | boolean | Filter by active status                         |
| search      | string  | Search by name                                  |
| sort        | string  | Sort field (name, tier_level, hire_date)        |
| order       | string  | Sort order (asc, desc)                          |
| page        | integer | Page number (default: 1)                        |
| per_page    | integer | Items per page (default: 20, max: 100)          |

### Response

```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "first_name": "John",
      "last_name": "Smith",
      "phone_number": "555-123-4567",
      "tier_level": 3,
      "hire_date": "2023-05-15",
      "active": true,
      "notes": "Excellent craftsman",
      "created_at": "2023-05-15T10:30:00Z",
      "updated_at": "2024-01-10T15:45:00Z"
    },
    {
      "id": 2,
      "first_name": "Jane",
      "last_name": "Doe",
      "phone_number": "555-987-6543",
      "tier_level": 4,
      "hire_date": "2022-11-20",
      "active": true,
      "notes": "Specializes in electrical work",
      "created_at": "2022-11-20T09:15:00Z",
      "updated_at": "2024-02-05T11:20:00Z"
    }
  ],
  "metadata": {
    "page": 1,
    "per_page": 20,
    "total": 2
  }
}
```

### Permissions

- **Employees**: Can only view their own record
- **Managers**: Can view all employees
- **Admins**: Can view all employees with all fields

---

## Get Employee

Retrieves a specific employee by ID.

### Request

```http
GET /api/v1/employees/{id}
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Response

```json
{
  "status": "success",
  "data": {
    "id": 1,
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "555-123-4567",
    "tier_level": 3,
    "hire_date": "2023-05-15",
    "active": true,
    "notes": "Excellent craftsman",
    "created_at": "2023-05-15T10:30:00Z",
    "updated_at": "2024-01-10T15:45:00Z"
  }
}
```

### Permissions

- **Employees**: Can only view their own record
- **Managers**: Can view all employees
- **Admins**: Can view all employees with all fields

---

## Create Employee

Creates a new employee record.

### Request

```http
POST /api/v1/employees
Content-Type: application/json

{
  "first_name": "Robert",
  "last_name": "Johnson",
  "phone_number": "555-555-5555",
  "tier_level": 2,
  "hire_date": "2025-03-01",
  "active": true,
  "notes": "New handyman, previously worked in construction"
}
```

### Request Body Parameters

| Parameter    | Type    | Required | Description                                     |
|--------------|---------|----------|-------------------------------------------------|
| first_name   | string  | Yes      | Employee's first name                           |
| last_name    | string  | Yes      | Employee's last name                            |
| phone_number | string  | No       | Employee's phone number                         |
| tier_level   | integer | Yes      | Tier level (1-5)                                |
| hire_date    | string  | Yes      | Hire date (YYYY-MM-DD format)                   |
| active       | boolean | No       | Active status (default: true)                   |
| notes        | string  | No       | Additional notes                                |

### Response

```json
{
  "status": "success",
  "message": "Employee created successfully",
  "data": {
    "id": 3,
    "first_name": "Robert",
    "last_name": "Johnson",
    "phone_number": "555-555-5555",
    "tier_level": 2,
    "hire_date": "2025-03-01",
    "active": true,
    "notes": "New handyman, previously worked in construction",
    "created_at": "2025-03-15T11:30:00Z",
    "updated_at": "2025-03-15T11:30:00Z"
  }
}
```

### Permissions

- **Managers**: Can create employee records
- **Admins**: Can create employee records

---

## Update Employee

Updates an existing employee record.

### Request

```http
PUT /api/v1/employees/{id}
Content-Type: application/json

{
  "first_name": "Robert",
  "last_name": "Johnson",
  "phone_number": "555-666-7777",
  "tier_level": 3,
  "hire_date": "2025-03-01",
  "active": true,
  "notes": "Promoted to Craftsman level after excellent performance"
}
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Request Body Parameters

| Parameter    | Type    | Required | Description                                     |
|--------------|---------|----------|-------------------------------------------------|
| first_name   | string  | Yes      | Employee's first name                           |
| last_name    | string  | Yes      | Employee's last name                            |
| phone_number | string  | No       | Employee's phone number                         |
| tier_level   | integer | Yes      | Tier level (1-5)                                |
| hire_date    | string  | Yes      | Hire date (YYYY-MM-DD format)                   |
| active       | boolean | No       | Active status                                   |
| notes        | string  | No       | Additional notes                                |

### Response

```json
{
  "status": "success",
  "message": "Employee updated successfully",
  "data": {
    "id": 3,
    "first_name": "Robert",
    "last_name": "Johnson",
    "phone_number": "555-666-7777",
    "tier_level": 3,
    "hire_date": "2025-03-01",
    "active": true,
    "notes": "Promoted to Craftsman level after excellent performance",
    "created_at": "2025-03-15T11:30:00Z",
    "updated_at": "2025-03-15T14:45:00Z"
  }
}
```

### Permissions

- **Managers**: Can update employee records
- **Admins**: Can update employee records

---

## Delete Employee

Deactivates an employee record (soft delete).

### Request

```http
DELETE /api/v1/employees/{id}
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Response

```json
{
  "status": "success",
  "message": "Employee deactivated successfully"
}
```

### Notes

- This endpoint performs a soft delete by setting `active` to `false`
- Historical data is preserved for reporting purposes
- For permanent deletion, use `/api/v1/admin/employees/{id}/delete-permanent` (admin only)

### Permissions

- **Admins**: Can deactivate employee records

---

## Get Employee Evaluations

Retrieves all evaluations for a specific employee.

### Request

```http
GET /api/v1/employees/{id}/evaluations
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Query Parameters

| Parameter    | Type    | Description                                                 |
|--------------|---------|-------------------------------------------------------------|
| type         | string  | Filter by evaluation type (self, manager)                   |
| date_from    | string  | Filter by evaluation date (YYYY-MM-DD) - start date         |
| date_to      | string  | Filter by evaluation date (YYYY-MM-DD) - end date           |
| page         | integer | Page number (default: 1)                                    |
| per_page     | integer | Items per page (default: 20, max: 100)                      |

### Response

```json
{
  "status": "success",
  "data": [
    {
      "id": 101,
      "employee_id": 1,
      "evaluation_date": "2024-12-15",
      "evaluator_id": 5,
      "evaluation_type": "manager",
      "notes": "Annual evaluation",
      "created_at": "2024-12-15T14:30:00Z",
      "updated_at": "2024-12-15T14:30:00Z"
    },
    {
      "id": 75,
      "employee_id": 1,
      "evaluation_date": "2024-09-10",
      "evaluator_id": null,
      "evaluation_type": "self",
      "notes": "Quarterly self-assessment",
      "created_at": "2024-09-10T10:15:00Z",
      "updated_at": "2024-09-10T10:15:00Z"
    }
  ],
  "metadata": {
    "page": 1,
    "per_page": 20,
    "total": 2
  }
}
```

### Permissions

- **Employees**: Can only view their own evaluations
- **Managers**: Can view evaluations for all employees
- **Admins**: Can view all evaluations

---

## Get Employee Skills

Retrieves the current skill ratings for a specific employee.

### Request

```http
GET /api/v1/employees/{id}/skills
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Query Parameters

| Parameter    | Type    | Description                                             |
|--------------|---------|---------------------------------------------------------|
| category_id  | integer | Filter by skill category                                |
| min_rating   | integer | Filter by minimum rating (1-5)                          |
| max_rating   | integer | Filter by maximum rating (1-5)                          |

### Response

```json
{
  "status": "success",
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "Carpentry Exterior/Deck",
        "skills": [
          {
            "id": 12,
            "name": "Deck Layout & Build",
            "rating": 4,
            "last_evaluated": "2024-12-15"
          },
          {
            "id": 13,
            "name": "Install/Replace Siding",
            "rating": 3,
            "last_evaluated": "2024-12-15"
          }
        ]
      },
      {
        "id": 2,
        "name": "Bathroom/Kitchen/Plumbing",
        "skills": [
          {
            "id": 24,
            "name": "Remove/Replace Faucet Assembly",
            "rating": 5,
            "last_evaluated": "2024-12-15"
          },
          {
            "id": 25,
            "name": "Install/Replace Supply Valves",
            "rating": 4,
            "last_evaluated": "2024-12-15"
          }
        ]
      }
    ],
    "summary": {
      "average_rating": 4.2,
      "total_skills_rated": 25,
      "skills_at_expert_level": 8
    }
  }
}
```

### Permissions

- **Employees**: Can only view their own skills
- **Managers**: Can view skills for all employees
- **Admins**: Can view all employee skills

---

## Get Employee Tools

Retrieves the current tool proficiency for a specific employee.

### Request

```http
GET /api/v1/employees/{id}/tools
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Query Parameters

| Parameter    | Type    | Description                                             |
|--------------|---------|---------------------------------------------------------|
| category_id  | integer | Filter by tool category                                 |
| can_operate  | boolean | Filter by operational capability                        |
| truck_stock  | boolean | Filter by truck stock status                            |

### Response

```json
{
  "status": "success",
  "data": {
    "categories": [
      {
        "id": 1,
        "name": "Hand Tools",
        "tools": [
          {
            "id": 12,
            "name": "Framing Square",
            "can_operate": true,
            "truck_stock": true,
            "last_evaluated": "2024-12-15"
          },
          {
            "id": 13,
            "name": "Speed Square",
            "can_operate": true,
            "truck_stock": true,
            "last_evaluated": "2024-12-15"
          }
        ]
      },
      {
        "id": 2,
        "name": "Power Tools",
        "tools": [
          {
            "id": 24,
            "name": "Circular Saw",
            "can_operate": true,
            "truck_stock": false,
            "last_evaluated": "2024-12-15"
          },
          {
            "id": 25,
            "name": "Reciprocating Saw",
            "can_operate": true,
            "truck_stock": false,
            "last_evaluated": "2024-12-15"
          }
        ]
      }
    ],
    "summary": {
      "total_tools": 35,
      "can_operate_count": 28,
      "truck_stock_count": 15
    }
  }
}
```

### Permissions

- **Employees**: Can only view their own tool proficiency
- **Managers**: Can view tool proficiency for all employees
- **Admins**: Can view all employee tool data

---

## Get Employee Special Skills

Retrieves special skills for a specific employee.

### Request

```http
GET /api/v1/employees/{id}/special-skills
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Response

```json
{
  "status": "success",
  "data": [
    {
      "id": 5,
      "employee_id": 1,
      "skill_name": "Custom Cabinet Design",
      "description": "Specializes in designing and building custom cabinets with unusual dimensions",
      "acquired_date": "2024-06-10",
      "notes": "Completed specialized training course",
      "created_at": "2024-06-15T11:30:00Z",
      "updated_at": "2024-06-15T11:30:00Z"
    },
    {
      "id": 8,
      "employee_id": 1,
      "skill_name": "Historical Restoration",
      "description": "Skilled in restoration techniques for century homes",
      "acquired_date": "2023-11-20",
      "notes": "Learned through apprenticeship with master craftsman",
      "created_at": "2023-12-05T09:45:00Z",
      "updated_at": "2023-12-05T09:45:00Z"
    }
  ]
}
```

### Permissions

- **Employees**: Can only view their own special skills
- **Managers**: Can view special skills for all employees
- **Admins**: Can view all employee special skills

---

## Add Employee Special Skill

Adds a new special skill to an employee's record.

### Request

```http
POST /api/v1/employees/{id}/special-skills
Content-Type: application/json

{
  "skill_name": "Smart Home Installation",
  "description": "Installation and configuration of smart home systems",
  "acquired_date": "2025-02-15",
  "notes": "Completed certification program with manufacturer"
}
```

### Path Parameters

| Parameter | Type    | Description   |
|-----------|---------|---------------|
| id        | integer | Employee ID   |

### Request Body Parameters

| Parameter    | Type    | Required | Description                                     |
|--------------|---------|----------|-------------------------------------------------|
| skill_name   | string  | Yes      | Name of the special skill                       |
| description  | string  | No       | Detailed description of the skill               |
| acquired_date| string  | No       | Date skill was acquired (YYYY-MM-DD)            |
| notes        | string  | No       | Additional notes                                |

### Response

```json
{
  "status": "success",
  "message": "Special skill added successfully",
  "data": {
    "id": 12,
    "employee_id": 1,
    "skill_name": "Smart Home Installation",
    "description": "Installation and configuration of smart home systems",
    "acquired_date": "2025-02-15",
    "notes": "Completed certification program with manufacturer",
    "created_at": "2025-03-15T16:30:00Z",
    "updated_at": "2025-03-15T16:30:00Z"
  }
}
```

### Permissions

- **Managers**: Can add special skills to employee records
- **Admins**: Can add special skills to any employee record

---

## Update Employee Special Skill

Updates an existing special skill for an employee.

### Request

```http
PUT /api/v1/employees/{employee_id}/special-skills/{skill_id}
Content-Type: application/json

{
  "skill_name": "Smart Home Installation and Programming",
  "description": "Installation, configuration, and programming of smart home systems",
  "acquired_date": "2025-02-15",
  "notes": "Completed advanced certification program with manufacturer"
}
```

### Path Parameters

| Parameter   | Type    | Description         |
|-------------|---------|---------------------|
| employee_id | integer | Employee ID         |
| skill_id    | integer | Special skill ID    |

### Request Body Parameters

| Parameter    | Type    | Required | Description                                     |
|--------------|---------|----------|-------------------------------------------------|
| skill_name   | string  | Yes      | Name of the special skill                       |
| description  | string  | No       | Detailed description of the skill               |
| acquired_date| string  | No       | Date skill was acquired (YYYY-MM-DD)            |
| notes        | string  | No       | Additional notes                                |

### Response

```json
{
  "status": "success",
  "message": "Special skill updated successfully",
  "data": {
    "id": 12,
    "employee_id": 1,
    "skill_name": "Smart Home Installation and Programming",
    "description": "Installation, configuration, and programming of smart home systems",
    "acquired_date": "2025-02-15",
    "notes": "Completed advanced certification program with manufacturer",
    "created_at": "2025-03-15T16:30:00Z",
    "updated_at": "2025-03-15T17:15:00Z"
  }
}
```

### Permissions

- **Managers**: Can update special skills for employee records
- **Admins**: Can update special skills for any employee record

---

## Delete Employee Special Skill

Removes a special skill from an employee's record.

### Request

```http
DELETE /api/v1/employees/{employee_id}/special-skills/{skill_id}
```

### Path Parameters

| Parameter   | Type    | Description         |
|-------------|---------|---------------------|
| employee_id | integer | Employee ID         |
| skill_id    | integer | Special skill ID    |

### Response

```json
{
  "status": "success",
  "message": "Special skill deleted successfully"
}
```

### Permissions

- **Managers**: Can delete special skills from employee records
- **Admins**: Can delete special skills from any employee record
