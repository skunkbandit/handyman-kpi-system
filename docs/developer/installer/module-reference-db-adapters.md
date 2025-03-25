## Database Adapter Modules

### `installer.shared.database.database_base`

**Purpose**: Provides base functionality for database adapters.

**Classes**:
- `DatabaseAdapter`: Abstract base class for database adapters
  - `__init__(config)`: Initializes with database configuration
  - `connect()`: Establishes database connection
  - `disconnect()`: Closes database connection
  - `test_connection()`: Tests database connection
  - `create_database()`: Creates database if it doesn't exist
  - `create_schema()`: Creates database schema
  - `apply_migrations()`: Applies database migrations
  - `seed_data()`: Seeds initial data

**Example Usage**:
```python
from installer.shared.database.database_base import DatabaseAdapter

class MyCustomDatabaseAdapter(DatabaseAdapter):
    def connect(self):
        # Custom connection logic
        return my_custom_connection

    def create_schema(self):
        # Custom schema creation
        self.connection.execute("CREATE TABLE ...")
```

### `installer.shared.database.sqlite_adapter`

**Purpose**: Implements SQLite database adapter.

**Classes**:
- `SQLiteAdapter`: Adapter for SQLite databases
  - `__init__(config)`: Initializes with SQLite configuration
  - `connect()`: Connects to SQLite database file
  - `create_database()`: Creates SQLite database file
  - `create_schema()`: Creates tables in SQLite database
  - `backup_database()`: Creates backup of database file

**Example Usage**:
```python
from installer.shared.database.sqlite_adapter import SQLiteAdapter

config = {
    "database_file": "C:/MyApp/data/app.db",
    "create_if_missing": True
}
adapter = SQLiteAdapter(config)
adapter.connect()
adapter.create_schema()
adapter.seed_data()
adapter.disconnect()
```

### `installer.shared.database.mysql_adapter`

**Purpose**: Implements MySQL/MariaDB database adapter.

**Classes**:
- `MySQLAdapter`: Adapter for MySQL/MariaDB databases
  - `__init__(config)`: Initializes with MySQL configuration
  - `connect()`: Connects to MySQL server
  - `create_database()`: Creates database on server
  - `create_schema()`: Creates tables in database
  - `test_connection()`: Tests MySQL connection settings

**Example Usage**:
```python
from installer.shared.database.mysql_adapter import MySQLAdapter

config = {
    "host": "localhost",
    "port": 3306,
    "user": "app_user",
    "password": "secret",
    "database": "my_app_db"
}
adapter = MySQLAdapter(config)
if adapter.test_connection():
    adapter.connect()
    adapter.create_database()
    adapter.create_schema()
    adapter.disconnect()
```

### `installer.shared.database.postgres_adapter`

**Purpose**: Implements PostgreSQL database adapter.

**Classes**:
- `PostgresAdapter`: Adapter for PostgreSQL databases
  - `__init__(config)`: Initializes with PostgreSQL configuration
  - `connect()`: Connects to PostgreSQL server
  - `create_database()`: Creates database on server
  - `create_schema()`: Creates tables in database
  - `create_extensions()`: Creates required PostgreSQL extensions

**Example Usage**:
```python
from installer.shared.database.postgres_adapter import PostgresAdapter

config = {
    "host": "localhost",
    "port": 5432,
    "user": "app_user",
    "password": "secret",
    "database": "my_app_db"
}
adapter = PostgresAdapter(config)
adapter.connect()
adapter.create_database()
adapter.create_extensions(["uuid-ossp", "hstore"])
adapter.create_schema()
adapter.disconnect()
```

### `installer.shared.database.mssql_adapter`

**Purpose**: Implements Microsoft SQL Server database adapter.

**Classes**:
- `MSSQLAdapter`: Adapter for SQL Server databases
  - `__init__(config)`: Initializes with SQL Server configuration
  - `connect()`: Connects to SQL Server
  - `create_database()`: Creates database on server
  - `create_schema()`: Creates tables in database
  - `configure_authentication()`: Configures SQL authentication

**Example Usage**:
```python
from installer.shared.database.mssql_adapter import MSSQLAdapter

config = {
    "server": "localhost\\SQLEXPRESS",
    "user": "app_user",
    "password": "secret",
    "database": "my_app_db",
    "trust_connection": False
}
adapter = MSSQLAdapter(config)
adapter.connect()
adapter.create_database()
adapter.create_schema()
adapter.disconnect()
```

### `installer.shared.database.migration_manager`

**Purpose**: Manages database schema migrations.

**Classes**:
- `MigrationManager`: Handles database migrations
  - `__init__(adapter, migrations_dir)`: Initializes with database adapter
  - `get_applied_migrations()`: Gets list of applied migrations
  - `get_pending_migrations()`: Gets list of pending migrations
  - `apply_migration(migration_file)`: Applies a single migration
  - `apply_all_pending()`: Applies all pending migrations
  - `rollback(steps=1)`: Rolls back migrations

**Example Usage**:
```python
from installer.shared.database.migration_manager import MigrationManager
from installer.shared.database.sqlite_adapter import SQLiteAdapter

adapter = SQLiteAdapter({"database_file": "app.db"})
adapter.connect()

migrations = MigrationManager(adapter, "migrations")
pending = migrations.get_pending_migrations()
print(f"Found {len(pending)} pending migrations")

migrations.apply_all_pending()
print("All migrations applied successfully")
```
