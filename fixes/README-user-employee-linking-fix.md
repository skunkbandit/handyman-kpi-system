# User-Employee Linking Fix

## Issue Description
When creating or editing a user, there is an option to link the user to an existing employee. This functionality is broken, showing blank values in the dropdown instead of employee names, making it impossible to select an employee.

## Root Cause
The templates (`create_user.html` and `edit_user.html`) have two issues:

1. **Field Name Mismatch**: 
   - Templates are trying to access `employee.first_name` and `employee.last_name`
   - But the Employee model only has a single `name` field

2. **Primary Key Mismatch**:
   - Templates use `value="{{ employee.id }}"` for dropdown options
   - But the Employee model uses `employee_id` as its primary key column name

## Solution
The fix involves updating the templates to use the correct field names:

1. Update dropdown option text:
   - From: `{{ employee.first_name }} {{ employee.last_name }}`
   - To: `{{ employee.name }}`

2. Update dropdown option values:
   - From: `value="{{ employee.id }}"` 
   - To: `value="{{ employee.employee_id }}"`

3. Update selected comparison:
   - From: `{{ 'selected' if user.employee_id == employee.id else '' }}`
   - To: `{{ 'selected' if user.employee_id == employee.employee_id else '' }}`

## How to Apply the Fix

### Automatic Fix (Recommended)
1. Download `fix_user_employee_linking_direct.py` and `fixed_*.html` files
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

## Verification
After applying the fix, you should be able to:
1. See employee names in the dropdown when creating/editing users
2. Successfully link users to employees
3. Correctly display the linked employee when editing a user with an existing employee link

## Files
- `fix_user_employee_linking.py` - Script that uses regex to fix the templates
- `fix_user_employee_linking_direct.py` - Script that replaces templates with fixed versions
- `fixed_create_user.html` - Fixed version of the create user template
- `fixed_edit_user.html` - Fixed version of the edit user template
