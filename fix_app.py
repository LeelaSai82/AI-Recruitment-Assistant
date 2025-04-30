import os
import sqlite3

# Print current working directory
print(f"Current directory: {os.getcwd()}")

# Create required directories
instance_dir = os.path.join(os.getcwd(), 'instance')
uploads_dir = os.path.join(os.getcwd(), 'uploads')

print(f"Creating instance directory: {instance_dir}")
os.makedirs(instance_dir, exist_ok=True)

print(f"Creating uploads directory: {uploads_dir}")
os.makedirs(uploads_dir, exist_ok=True)

# Try to create a test database to verify permissions
db_path = os.path.join(instance_dir, 'test.db')
print(f"Testing database creation at: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)')
    conn.commit()
    cursor.close()
    conn.close()
    print("Database test successful!")
except Exception as e:
    print(f"Database test failed: {str(e)}")

print("\nNow update app.py with this database path...")
print(f"DATABASE_URL = 'sqlite:///{os.path.join(instance_dir, 'recruitment.db')}'")