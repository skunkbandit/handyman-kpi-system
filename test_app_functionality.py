"""
Basic test script to verify application functionality.
"""
import os
import sys
import importlib.util

def test_import_app():
    """Test importing the app module directly."""
    print("Testing direct app import...")
    try:
        # Add the backend directory to the path
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # Try to import app
        print(f"Looking for app module in {backend_dir}")
        
        # Check if __init__.py exists
        init_path = os.path.join(backend_dir, 'app', '__init__.py')
        if os.path.exists(init_path):
            print(f"Found app/__init__.py at {init_path}")
        else:
            print(f"ERROR: app/__init__.py not found at {init_path}")
        
        # Try to import using direct method
        spec = importlib.util.find_spec('app')
        if spec:
            print(f"Found app module at {spec.origin}")
            import app
            print("Successfully imported app module")
        else:
            print("ERROR: app module not found")
            return False
        
        # Check if create_app function exists
        if hasattr(app, 'create_app'):
            print("Found create_app function")
        else:
            print("ERROR: create_app function not found")
            return False
        
        # Try to create app instance
        app_instance = app.create_app({'TESTING': True})
        print("Successfully created app instance")
        
        # Check basic app properties
        print(f"App name: {app_instance.name}")
        print(f"Debug mode: {app_instance.debug}")
        print(f"Testing mode: {app_instance.config['TESTING']}")
        
        # Check if blueprints are registered
        print("Registered blueprints:")
        for name, blueprint in app_instance.blueprints.items():
            print(f"  - {name}")
        
        return True
    except Exception as e:
        print(f"ERROR importing app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_models():
    """Test importing database models."""
    print("\nTesting database models import...")
    try:
        # Add the backend directory to the path
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # Import models
        from app.models.user import User
        print("Successfully imported User model")
        
        from app.models.employee import Employee
        print("Successfully imported Employee model")
        
        from app.models.evaluation import Evaluation
        print("Successfully imported Evaluation model")
        
        return True
    except Exception as e:
        print(f"ERROR importing models: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_routes():
    """Test importing route blueprints."""
    print("\nTesting routes import...")
    try:
        # Add the backend directory to the path
        backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # Import route blueprints
        from app.routes.main import bp as main_bp
        print("Successfully imported main blueprint")
        
        from app.routes.auth import bp as auth_bp
        print("Successfully imported auth blueprint")
        
        from app.routes.dashboard import bp as dashboard_bp
        print("Successfully imported dashboard blueprint")
        
        from app.routes.employees import bp as employees_bp
        print("Successfully imported employees blueprint")
        
        from app.routes.evaluations import bp as evaluations_bp
        print("Successfully imported evaluations blueprint")
        
        from app.routes.reports import bp as reports_bp
        print("Successfully imported reports blueprint")
        
        return True
    except Exception as e:
        print(f"ERROR importing routes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_templates_and_static():
    """Test existence of templates and static files."""
    print("\nTesting templates and static files...")
    
    # Check templates directory
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend', 'app', 'templates')
    if os.path.exists(templates_dir) and os.path.isdir(templates_dir):
        print(f"Templates directory exists at {templates_dir}")
        
        # Check for some critical templates
        for template in ['base.html', 'index.html', 'login.html']:
            template_path = os.path.join(templates_dir, template)
            if os.path.exists(template_path):
                print(f"  - Found template: {template}")
            else:
                print(f"  - WARNING: Template not found: {template}")
    else:
        print(f"ERROR: Templates directory not found at {templates_dir}")
        return False
    
    # Check static directory
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kpi-system', 'backend', 'app', 'static')
    if os.path.exists(static_dir) and os.path.isdir(static_dir):
        print(f"Static directory exists at {static_dir}")
        
        # Check for static subdirectories
        for subdir in ['css', 'js', 'img']:
            subdir_path = os.path.join(static_dir, subdir)
            if os.path.exists(subdir_path) and os.path.isdir(subdir_path):
                print(f"  - Found static subdirectory: {subdir}")
            else:
                print(f"  - WARNING: Static subdirectory not found: {subdir}")
    else:
        print(f"ERROR: Static directory not found at {static_dir}")
        return False
    
    return True

def test_database_connection():
    """Test database connection using our simplified test that works."""
    print("\nTesting database connection...")
    try:
        # Import from the simplified db test
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from simplified_db_test import test_actual_models
        
        # Run the actual models test
        result = test_actual_models()
        return result
    except Exception as e:
        print(f"ERROR testing database connection: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and return overall status."""
    tests = [
        ("App Import", test_import_app),
        ("Database Models", test_database_models),
        ("Route Blueprints", test_routes),
        ("Templates and Static Files", test_templates_and_static),
        ("Database Connection", test_database_connection)
    ]
    
    print("=" * 50)
    print("RUNNING APPLICATION VERIFICATION TESTS")
    print("=" * 50)
    
    results = []
    for name, test_func in tests:
        print(f"\n{'-' * 50}")
        print(f"RUNNING TEST: {name}")
        print(f"{'-' * 50}")
        
        result = test_func()
        results.append((name, result))
        
        print(f"{'-' * 50}")
        print(f"TEST RESULT: {name} - {'PASSED' if result else 'FAILED'}")
        print(f"{'-' * 50}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        if not result:
            all_passed = False
        print(f"{name}: {status}")
    
    print("\nOVERALL RESULT:", "PASSED" if all_passed else "FAILED")
    print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()
