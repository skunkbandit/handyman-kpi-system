# User-Employee Linking Fix

## Issue Description
When creating or editing a user, there is an option to link the user to an existing employee. This functionality is broken, showing blank values in the dropdown instead of employee names, making it impossible to select an employee.

Additionally, when viewing the user management page, clicking on a linked employee produces an error due to a route parameter name mismatch.

## Root Cause
The templates (`create_user.html` and `edit_user.html`) have two issues:

1. **Field Name Mismatch**: 
   - Templates are trying to access `employee.first_name` and `employee.last_name`
   - But the Employee model only has a single `name` field

2. **Primary Key Mismatch**:
   - Templates use `value="{{ employee.id }}"` for dropdown options
   - But the Employee model uses `employee_id` as its primary key column name

The `user_management.html` template has an additional issue:

3. **URL Parameter Mismatch**:
   - Template calls `url_for('employees.view', id=user.employee_id)`
   - But the route expects `employee_id` instead of `id`, causing the error:
   ```
   werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'employees.view' with values ['id']. Did you forget to specify values ['employee_id']?
   ```

## Solution
The fix involves updating the templates to use the correct field names and URL parameters:

1. Update dropdown option text:
   - From: `{{ employee.first_name }} {{ employee.last_name }}`
   - To: `{{ employee.name }}`

2. Update dropdown option values:
   - From: `value="{{ employee.id }}"` 
   - To: `value="{{ employee.employee_id }}"`

3. Update selected comparison:
   - From: `{{ 'selected' if user.employee_id == employee.id else '' }}`
   - To: `{{ 'selected' if user.employee_id == employee.employee_id else '' }}`

4. Update URL parameter in user_management.html:
   - From: `url_for('employees.view', id=user.employee_id)`
   - To: `url_for('employees.view', employee_id=user.employee_id)`

## How to Apply the Fix

### Automatic Fix (Recommended)
1. Download `fix_user_employee_linking_direct.py` and all `fixed_*.html` files
2. Place them in your KPI system root directory
3. Run the script:
   ```
   python fix_user_employee_linking_direct.py
   ```
   or use the batch file:
   ```
   fix_user_employee_linking_direct.bat
   ```

### Manual Fix
If you prefer to make the changes manually:

1. In `kpi-system/backend/app/templates/auth/create_user.html`:
   - Change `{{ employee.first_name }} {{ employee.last_name }}` to `{{ employee.name }}`
   - Change `value="{{ employee.id }}"` to `value="{{ employee.employee_id }}"`

2. In `kpi-system/backend/app/templates/auth/edit_user.html`:
   - Change `{{ employee.first_name }} {{ employee.last_name }}` to `{{ employee.name }}`
   - Change `value="{{ employee.id }}"` to `value="{{ employee.employee_id }}"`
   - Change `{{ 'selected' if user.employee_id == employee.id else '' }}` to `{{ 'selected' if user.employee_id == employee.employee_id else '' }}`

3. In `kpi-system/backend/app/templates/auth/user_management.html`:
   - Change `url_for('employees.view', id=user.employee_id)` to `url_for('employees.view', employee_id=user.employee_id)`
   - Change `{{ user.employee.first_name }} {{ user.employee.last_name }}` to `{{ user.employee.name }}`

## Verification
After applying the fix, you should be able to:
1. See employee names in the dropdown when creating/editing users
2. Successfully link users to employees
3. Correctly display the linked employee when editing a user with an existing employee link
4. Click on linked employee names in the user management page without errors

## Files
- `fix_user_employee_linking.py` - Script that uses regex to fix the templates
- `fix_user_employee_linking_direct.py` - Script that replaces templates with fixed versions
- `fixed_create_user.html` - Fixed version of the create user template
- `fixed_edit_user.html` - Fixed version of the edit user template
- `fixed_user_management.html` - Fixed version of the user management template
