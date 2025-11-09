"""Quick test to see if backend can start."""
import sys
import traceback

try:
    print("=== Testing Backend Import ===")

    print("1. Importing FastAPI...")
    from fastapi import FastAPI
    print("   ✓ FastAPI imported")

    print("2. Importing backend.core.config...")
    from backend.core.config import settings
    print(f"   ✓ Config imported, DEBUG={settings.DEBUG}")

    print("3. Importing backend.core.database...")
    from backend.core.database import init_db
    print("   ✓ Database module imported")

    print("4. Initializing database...")
    init_db()
    print("   ✓ Database initialized")

    print("5. Importing backend.main...")
    from backend.main import app
    print("   ✓ Backend app created successfully!")

    print("\n=== All imports successful! ===")
    print("The backend should be able to start.")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
