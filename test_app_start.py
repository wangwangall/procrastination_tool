import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    # Import the app
    from app import app, init_db
    
    print("App imported successfully!")
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    
    print("App configuration:")
    print(f"  SECRET_KEY: {app.config['SECRET_KEY']}")
    print(f"  DATABASE: {app.config['DATABASE']}")
    
    # Test the routes
    print("\nApp routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()