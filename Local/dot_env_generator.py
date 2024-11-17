import os
from base64 import urlsafe_b64encode

# Path to the .env file
env_file_path = ".env"

# Check if the .env file already exists
if os.path.exists(env_file_path):
    print(f"The .env file already exists at {env_file_path}. No changes made.")
    exit(0)

# Generate a random 256-bit API key
api_key = urlsafe_b64encode(os.urandom(32)).decode('utf-8')
print(f"Generated unique API Key: {api_key}")

# Define the content of the .env file
env_contents = f"""
# Dropbox App Credentials
DROPBOX_APP_KEY=YOUR_APP_KEY
DROPBOX_APP_SECRET=YOUR_APP_SECRET
DROPBOX_REFRESH_TOKEN=YOUR_REFRESH_TOKEN

# Optional Second Dropbox App with Read/Write permissions (used for logs). These credentials are also used in the Django project.
DROPBOX_APP_KEY_RW=YOUR_APP_KEY_RW
DROPBOX_APP_SECRET_RW=YOUR_APP_SECRET_RW
DROPBOX_REFRESH_TOKEN_RW=YOUR_REFRESH_TOKEN_RW

# MingSec API Credentials - This API Key is also used in the Django project
MINGSEC_API_KEY={api_key}

# API Endpoints
CAM_REQUEST_ENDPOINT=http://localhost:8000/api/requests/get/
ALARM_REPORT_ENDPOINT=http://localhost:8000/api/alarms/add/
STATUS_REPORT_ENDPOINT=http://localhost:8000/api/status/add/

# External Linux Device (Optional - if planning to use a second camera)
EXTERNAL_DEVICE_NAME=YOUR_EXTERNAL_DEVICE_NAME
EXTERNAL_DEVICE_PATH=~/Desktop/external

# Firebase Credentials - Firebase app help can be found in the 'app' README
FIREBASE_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID
NOTIFICATION_DEVICE_TOKEN=YOUR_NOTIFICATION_DEVICE_TOKEN
"""

# Write the content to the .env file
with open(env_file_path, "w") as file:
    file.write(env_contents.strip())

# Set restrictive file permissions on the .env file
os.chmod(env_file_path, 0o600)

print(f"New .env file created at {env_file_path}. Please update the placeholders as needed.")