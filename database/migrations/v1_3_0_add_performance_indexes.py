"""
Migration script v1.3.0 - Add performance indexes to improve query speed
"""

def upgrade(connection):
    """
    Add performance indexes for commonly queried tables
    """
    cursor = connection.cursor()
    
    # Create indexes for evaluations table to speed up dashboard queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_evaluations_employee_id 
        ON evaluations(employee_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_evaluations_date 
        ON evaluations(evaluation_date);
    ''')
    
    # Create indexes for skill evaluations
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_eval_skills_evaluation_id 
        ON eval_skills(evaluation_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_eval_skills_skill_id 
        ON eval_skills(skill_id);
    ''')
    
    # Create indexes for tool evaluations
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_eval_tools_evaluation_id 
        ON eval_tools(evaluation_id);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_eval_tools_tool_id 
        ON eval_tools(tool_id);
    ''')
    
    # Create indexes for report generation
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_employees_tier 
        ON employees(tier);
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_special_skills_employee_id 
        ON special_skills(employee_id);
    ''')
    
    # Create index for users
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_users_role 
        ON users(role);
    ''')
    
    # Update schema version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.3.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True


def downgrade(connection):
    """
    Remove the indexes created in this migration
    """
    cursor = connection.cursor()
    
    # Drop all indexes created in this migration
    cursor.execute('DROP INDEX IF EXISTS idx_evaluations_employee_id;')
    cursor.execute('DROP INDEX IF EXISTS idx_evaluations_date;')
    cursor.execute('DROP INDEX IF EXISTS idx_eval_skills_evaluation_id;')
    cursor.execute('DROP INDEX IF EXISTS idx_eval_skills_skill_id;')
    cursor.execute('DROP INDEX IF EXISTS idx_eval_tools_evaluation_id;')
    cursor.execute('DROP INDEX IF EXISTS idx_eval_tools_tool_id;')
    cursor.execute('DROP INDEX IF EXISTS idx_employees_tier;')
    cursor.execute('DROP INDEX IF EXISTS idx_special_skills_employee_id;')
    cursor.execute('DROP INDEX IF EXISTS idx_users_role;')
    
    # Update schema version back to previous version
    cursor.execute('''
        INSERT OR REPLACE INTO schema_version (version, updated_at)
        VALUES ('1.2.0', datetime('now'));
    ''')
    
    connection.commit()
    
    return True
