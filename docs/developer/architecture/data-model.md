# Data Model

This document describes the database schema and entity relationships for the Handyman KPI System.

## Overview

The Handyman KPI System uses a relational database (SQLite by default) with multiple tables representing:

- User accounts and authentication
- Employees and their attributes
- Skill categories and individual skills
- Tool categories and tools
- Performance evaluations
- Special skills
- System configuration and metadata

## Entity Relationship Diagram

The following diagram shows the main entities and their relationships:

```
+----------------+       +----------------+       +----------------+
|    Users       |       |   Employees    |       |  Evaluations   |
+----------------+       +----------------+       +----------------+
| id             |       | id             |       | id             |
| username       |       | first_name     |       | employee_id    |
| email          |<---+  | last_name      |<------| evaluator_id   |
| password_hash  |    |  | email          |       | evaluation_date|
| first_name     |    |  | phone          |       | notes          |
| last_name      |    |  | hire_date      |       | overall_rating |
| role           |    |  | tier           |       | created_at     |
| is_active      |    |  | address        |       +----------------+
| created_at     |    |  | city           |              ^
+----------------+    |  | state          |              |
                      |  | zip            |              |
                      |  +----------------+              |
                      |         ^                        |
                      |         |                        |
+----------------+    |  +----------------+       +----------------+
| Skill Categories|   |  | Special Skills  |       |  Eval Skills   |
+----------------+    |  +----------------+       +----------------+
| id             |    |  | id             |       | id             |
| name           |    |  | employee_id    |       | evaluation_id  |
| description    |    |  | name           |       | skill_id       |
+----------------+    |  | description    |       | rating         |
        ^             |  | created_by     |----+  | notes          |
        |             |  | created_at     |    |  +----------------+
        |             |  +----------------+    |
        |                                      |
+----------------+                      +----------------+
|    Skills      |                      |   Eval Tools   |
+----------------+                      +----------------+
| id             |                      | id             |
| category_id    |                      | evaluation_id  |
| name           |                      | tool_id        |
| description    |                      | can_operate    |
+----------------+                      | owns_tool      |
        ^                               +----------------+
        |                                      ^
        |                                      |
+----------------+                      +----------------+
| Tool Categories|                      |     Tools      |
+----------------+                      +----------------+
| id             |                      | id             |
| name           |                      | category_id    |
| description    |                      | name           |
+----------------+                      | description    |
        |                               +----------------+
        |                                      ^
        +--------------------------------------+
```

## Table Definitions

### Users

Stores user account information for system access.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| username        | TEXT      | Unique username for login                      |
| email           | TEXT      | User's email address                           |
| password_hash   | TEXT      | Hashed password                                |
| first_name      | TEXT      | User's first name                              |
| last_name       | TEXT      | User's last name                               |
| role            | TEXT      | User role (admin, manager, employee)           |
| is_active       | BOOLEAN   | Account status                                 |
| created_at      | DATETIME  | Account creation timestamp                     |
| last_login      | DATETIME  | Last login timestamp                           |
| login_count     | INTEGER   | Number of successful logins                    |

### Employees

Stores information about employees being evaluated.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| first_name      | TEXT      | Employee's first name                          |
| last_name       | TEXT      | Employee's last name                           |
| email           | TEXT      | Employee's email address                       |
| phone           | TEXT      | Contact phone number                           |
| hire_date       | DATE      | Employment start date                          |
| tier            | TEXT      | Craftsman tier level                           |
| address         | TEXT      | Street address                                 |
| city            | TEXT      | City                                           |
| state           | TEXT      | State/province                                 |
| zip             | TEXT      | Postal code                                    |
| created_at      | DATETIME  | Record creation timestamp                      |
| updated_at      | DATETIME  | Record update timestamp                        |

### Skill Categories

Categorizes skills into logical groups.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| name            | TEXT      | Category name                                  |
| description     | TEXT      | Category description                           |
| created_at      | DATETIME  | Record creation timestamp                      |

### Skills

Individual skills that can be evaluated.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| category_id     | INTEGER   | Foreign key to skill_categories                |
| name            | TEXT      | Skill name                                     |
| description     | TEXT      | Skill description                              |
| created_at      | DATETIME  | Record creation timestamp                      |

### Tool Categories

Categorizes tools into logical groups.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| name            | TEXT      | Category name                                  |
| description     | TEXT      | Category description                           |
| created_at      | DATETIME  | Record creation timestamp                      |

### Tools

Individual tools that employees may use.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| category_id     | INTEGER   | Foreign key to tool_categories                 |
| name            | TEXT      | Tool name                                      |
| description     | TEXT      | Tool description                               |
| created_at      | DATETIME  | Record creation timestamp                      |

### Evaluations

Performance evaluations of employees.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| employee_id     | INTEGER   | Foreign key to employees                       |
| evaluator_id    | INTEGER   | Foreign key to users (who performed evaluation)|
| evaluation_date | DATE      | Date of evaluation                             |
| notes           | TEXT      | General evaluation notes                       |
| overall_rating  | INTEGER   | Overall performance rating                     |
| created_at      | DATETIME  | Record creation timestamp                      |
| updated_at      | DATETIME  | Record update timestamp                        |

### Eval Skills

Skill ratings in an evaluation.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| evaluation_id   | INTEGER   | Foreign key to evaluations                     |
| skill_id        | INTEGER   | Foreign key to skills                          |
| rating          | INTEGER   | Skill proficiency rating (1-5)                 |
| notes           | TEXT      | Notes specific to this skill                   |
| created_at      | DATETIME  | Record creation timestamp                      |

### Eval Tools

Tool proficiency in an evaluation.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| evaluation_id   | INTEGER   | Foreign key to evaluations                     |
| tool_id         | INTEGER   | Foreign key to tools                           |
| can_operate     | BOOLEAN   | Whether employee can operate this tool         |
| owns_tool       | BOOLEAN   | Whether employee owns this tool                |
| created_at      | DATETIME  | Record creation timestamp                      |

### Special Skills

Skills not covered by the standard categories.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| employee_id     | INTEGER   | Foreign key to employees                       |
| name            | TEXT      | Skill name                                     |
| description     | TEXT      | Skill description                              |
| created_by      | INTEGER   | Foreign key to users (who added this skill)    |
| created_at      | DATETIME  | Record creation timestamp                      |

### Schema Version

Tracks database schema version for migrations.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| version         | TEXT      | Schema version (e.g., "1.0.0")                 |
| updated_at      | DATETIME  | Update timestamp                               |

## Additional Tables

The following tables are added in later migrations:

### Backups

Tracks database backup history.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| filename        | TEXT      | Backup filename                                |
| created_at      | DATETIME  | Backup creation timestamp                      |
| file_size       | INTEGER   | Backup file size in bytes                      |
| file_hash       | TEXT      | Backup file SHA-256 hash                       |
| is_automatic    | BOOLEAN   | Whether backup was created automatically       |
| status          | TEXT      | Backup status (success, failed)                |
| notes           | TEXT      | Additional notes                               |

### Audit Log

Records system activity for auditing.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| timestamp       | DATETIME  | Action timestamp                               |
| user_id         | INTEGER   | Foreign key to users                           |
| action          | TEXT      | Action performed                               |
| table_name      | TEXT      | Affected table                                 |
| record_id       | INTEGER   | Affected record ID                             |
| details         | TEXT      | Action details (JSON)                          |
| ip_address      | TEXT      | User's IP address                              |

### Login History

Tracks authentication activity.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| user_id         | INTEGER   | Foreign key to users                           |
| timestamp       | DATETIME  | Login timestamp                                |
| action          | TEXT      | Action type (LOGIN, LOGOUT, FAILED_LOGIN)      |
| ip_address      | TEXT      | User's IP address                              |
| user_agent      | TEXT      | Browser user agent                             |

### Report Templates

Stored report configurations.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| name            | TEXT      | Template name                                  |
| description     | TEXT      | Template description                           |
| template_type   | TEXT      | Report type                                    |
| config          | JSON      | Report configuration                           |
| is_system       | BOOLEAN   | Whether it's a system template                 |
| created_by      | INTEGER   | Foreign key to users                           |
| created_at      | DATETIME  | Creation timestamp                             |
| updated_at      | DATETIME  | Update timestamp                               |

### Notifications

System and user notifications.

| Column          | Type      | Description                                    |
|-----------------|-----------|------------------------------------------------|
| id              | INTEGER   | Primary key                                    |
| user_id         | INTEGER   | Foreign key to users                           |
| type_id         | INTEGER   | Foreign key to notification_types              |
| title           | TEXT      | Notification title                             |
| message         | TEXT      | Notification message                           |
| data            | JSON      | Additional data (JSON)                         |
| is_read         | BOOLEAN   | Whether notification has been read             |
| created_at      | DATETIME  | Creation timestamp                             |
| read_at         | DATETIME  | When notification was read                     |

## Primary and Foreign Key Relationships

The system implements the following relationships:

### One-to-Many Relationships

- A skill category has many skills
- A tool category has many tools
- An employee has many evaluations
- A user (evaluator) conducts many evaluations
- An evaluation has many skill ratings
- An evaluation has many tool proficiencies
- An employee has many special skills

### Many-to-Many Relationships

- Employees have many skills (through evaluations and eval_skills)
- Employees have many tools (through evaluations and eval_tools)

## Indexes

The database includes the following indexes for performance optimization:

- `idx_evaluations_employee_id` on evaluations(employee_id)
- `idx_evaluations_date` on evaluations(evaluation_date)
- `idx_eval_skills_evaluation_id` on eval_skills(evaluation_id)
- `idx_eval_skills_skill_id` on eval_skills(skill_id)
- `idx_eval_tools_evaluation_id` on eval_tools(evaluation_id)
- `idx_eval_tools_tool_id` on eval_tools(tool_id)
- `idx_employees_tier` on employees(tier)
- `idx_special_skills_employee_id` on special_skills(employee_id)
- `idx_users_role` on users(role)

## Data Integrity Constraints

The database enforces the following constraints:

- Foreign key constraints ensure referential integrity
- NOT NULL constraints on required fields
- Unique constraints on username and email
- Check constraint on evaluation ratings (1-5 range)

## Migrations

The database schema evolves through migrations, with each migration representing a version change. See the [migration scripts](../../backend/migrations.md) for details on each version change.

## SQLAlchemy Models

The database tables are accessed through SQLAlchemy ORM models. See the [models documentation](../../backend/models.md) for details on the Python models that interact with this schema.
