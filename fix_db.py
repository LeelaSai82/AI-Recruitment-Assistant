import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the base directory (where your application is located)
basedir = os.path.abspath(os.path.dirname(__file__))

# Create instance directory if it doesn't exist
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)

# Update the DATABASE_URL environment variable
os.environ['DATABASE_URL'] = f"sqlite:///{os.path.join(instance_path, 'recruitment.db')}"

print(f"Database path set to: {os.environ['DATABASE_URL']}")
print(f"Instance directory created at: {instance_path}")