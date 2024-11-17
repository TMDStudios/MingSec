import os
from base64 import urlsafe_b64encode

# Path to the .env file
env_file_path = ".env"

# Check if the .env file already exists
if os.path.exists(env_file_path):
    print(f"The .env file already exists at {env_file_path}. No changes made.")
    exit(0)

# Generate a random 256-bit secret key
secret_key = urlsafe_b64encode(os.urandom(32)).decode('utf-8')
print(f"Generated unique Secret Key: {secret_key}")

# Define the content of the .env file
env_contents = f"""
# Copy the generated API Key from the .env file in the 'local' folder
API_KEY = YOUR_API_KEY

SECRET_KEY = {secret_key}
DEBUG = False
ALLOWED_HOSTS=localhost,127.0.0.1

# Dropbox App Credentials - If you are using one Dropbox app, you may use your DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN keys here
DROPBOX_APP_KEY_RW = YOUR_APP_KEY
DROPBOX_APP_SECRET_RW = YOUR_APP_SECRET
DROPBOX_REFRESH_TOKEN_RW = YOUR_REFRESH_TOKEN
"""

# Write the content to the .env file
with open(env_file_path, "w") as file:
    file.write(env_contents.strip())

# Set restrictive file permissions on the .env file
os.chmod(env_file_path, 0o600)

print(f"New .env file created at {env_file_path}. Please update the placeholders as needed.")