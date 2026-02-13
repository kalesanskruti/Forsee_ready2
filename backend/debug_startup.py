import sys
try:
    from app.main import app
    print("App imported successfully")
except Exception as e:
    print(f"Failed to import app: {e}")
    import traceback
    traceback.print_exc()
