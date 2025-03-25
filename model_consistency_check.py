"""
Model consistency check script.
Identifies inconsistencies between database model relationships.
"""
import os
import sys
import inspect

def setup_python_path():
    """Set up Python path for imports."""
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend')
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

def check_model_relationships():
    """Check for inconsistencies in model relationships."""
    setup_python_path()
    
    print("=" * 50)
    print("CHECKING MODEL RELATIONSHIPS FOR CONSISTENCY")
    print("=" * 50)
    
    # Import models
    try:
        from app.models.user import User
        from app.models.employee import Employee
        from app.models.evaluation import Evaluation, SkillEvaluation, ToolEvaluation, SpecialSkill
        from app import db
        
        # Get all models
        models = {
            'User': User,
            'Employee': Employee,
            'Evaluation': Evaluation,
            'SkillEvaluation': SkillEvaluation,
            'ToolEvaluation': ToolEvaluation,
            'SpecialSkill': SpecialSkill
        }
        
        # Check primary keys
        print("\nPRIMARY KEYS:")
        primary_keys = {}
        for name, model in models.items():
            pk_columns = [column.name for column in model.__table__.columns if column.primary_key]
            primary_keys[name] = pk_columns
            print(f"{name}: {', '.join(pk_columns)}")
        
        # Check foreign keys
        print("\nFOREIGN KEYS:")
        inconsistencies = []
        
        for name, model in models.items():
            for column in model.__table__.columns:
                if column.foreign_keys:
                    for fk in column.foreign_keys:
                        target_table = fk.target_fullname.split('.')[0]
                        target_column = fk.target_fullname.split('.')[1]
                        print(f"{name}.{column.name} -> {target_table}.{target_column}")
                        
                        # Check if the target column exists in the target table
                        for target_model_name, target_model in models.items():
                            if target_model.__tablename__ == target_table:
                                target_columns = [col.name for col in target_model.__table__.columns]
                                if target_column not in target_columns:
                                    inconsistency = f"ERROR: {name}.{column.name} references {target_table}.{target_column}, but {target_column} doesn't exist in {target_table}"
                                    inconsistencies.append(inconsistency)
                                    print(f"  *** {inconsistency}")
        
        # Check relationships
        print("\nRELATIONSHIPS:")
        for name, model in models.items():
            rel_attrs = [attr for attr in dir(model) if not attr.startswith('_') and not attr.startswith('__') and attr != 'query']
            for attr in rel_attrs:
                if hasattr(model, attr) and isinstance(getattr(model, attr), db.relationship().__class__):
                    rel = getattr(model, attr)
                    if hasattr(rel, 'argument') and hasattr(rel, 'backref'):
                        print(f"{name}.{attr} -> {rel.argument} (backref: {rel.backref})")
                    elif hasattr(rel, 'argument') and hasattr(rel, 'back_populates'):
                        print(f"{name}.{attr} -> {rel.argument} (back_populates: {rel.back_populates})")
                    elif hasattr(rel, 'argument'):
                        print(f"{name}.{attr} -> {rel.argument}")
                    else:
                        print(f"{name}.{attr} -> Unknown relationship")
        
        # Report inconsistencies
        if inconsistencies:
            print("\n" + "=" * 50)
            print("MODEL INCONSISTENCIES FOUND:")
            print("=" * 50)
            for i, inconsistency in enumerate(inconsistencies, 1):
                print(f"{i}. {inconsistency}")
            print("\nThese inconsistencies need to be fixed for proper database operation.")
            return False
        else:
            print("\n" + "=" * 50)
            print("NO MODEL INCONSISTENCIES FOUND")
            print("=" * 50)
            return True
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_model_relationships()
