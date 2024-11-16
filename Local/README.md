# MingSec Local Setup

This guide walks you through setting up the local MingSec system.

>MingSec currently only runs on Windows, but it may be used on Mac/Linux with some adjustments.

## Prerequisites

- Python 3.8 or higher
- A [Dropbox account](https://www.dropbox.com/) (if you don’t already have one)
- (Optional) A Linux device for a second camera
- (Optional) Firebase account for notifications (if using the Kotlin notification app)

## Installation Instructions

### 1. Create a Virtual Environment
Create and activate a virtual environment for Python:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

### 2. Install Required Dependencies
Install the required Python packages from requirements.txt:

```bash
pip install -r requirements.txt
```

### 3. Create a Dropbox Application
1. Sign in to your [Dropbox account](https://www.dropbox.com/login).
2. Create a new Dropbox app by following the instructions [here](https://www.dropbox.com/developers/reference/getting-started).
3. Note down the following credentials:
   - `APP_KEY`
   - `APP_SECRET`
   - `REFRESH_TOKEN`
4. (Optional) If you plan to use separate credentials for read/write operations, create another app with appropriate permissions.
   - If you decide to use one application, use the same credentials for both apps in the .env file

### 4. Configure Environment Variables
Create a `.env` file in the `local` folder with the following key-value pairs:

```plaintext
# Dropbox App Credentials
DROPBOX_APP_KEY = YOUR_APP_KEY
DROPBOX_APP_SECRET = YOUR_APP_SECRET
DROPBOX_REFRESH_TOKEN = YOUR_REFRESH_TOKEN

# Optional Second Dropbox App with Read/Write permissions (used for logs). If using one app, just paste the same credentials below.
DROPBOX_APP_KEY_RW = YOUR_APP_KEY
DROPBOX_APP_SECRET_RW = YOUR_APP_SECRET
DROPBOX_REFRESH_TOKEN_RW = YOUR_REFRESH_TOKEN

# MingSec API Credentials - Deployment help can be found in the 'frontend' README
MINGSEC_API_KEY = YOUR_DJANGO_API_KEY

# API Endpoints
CAM_REQUEST_ENDPOINT = YOUR_DEPLOYED_DJANGO_URL/api/requests/get/
ALARM_REPORT_ENDPOINT = YOUR_DEPLOYED_DJANGO_URL/api/alarms/add/
STATUS_REPORT_ENDPOINT = YOUR_DEPLOYED_DJANGO_URL/api/status/add/

# External Linux Device (Optional - if planning to use a second camera)
EXTERNAL_DEVICE_NAME = YOUR_EXTERNAL_DEVICE_NAME
EXTERNAL_DEVICE_PATH = ~/Desktop/external

# Firebase Credentials - Firebase app help can be found in the 'app' README
FIREBASE_PROJECT_ID = YOUR_FIREBASE_PROJECT_ID
NOTIFICATION_DEVICE_TOKEN = YOUR_NOTIFICATION_DEVICE_TOKEN
```

---

### 5. (Optional) Copy to an External Linux Device
If you’re using a second camera connected to a Linux device, copy the `external` folder from your MingSec project directory to the target device. You can place the folder wherever is convenient, but make sure to update the `EXTERNAL_DEVICE_PATH` in your `.env` file to reflect the correct location.
If you're not using a second camera, you can skip this step.

### 6. (Optional) Setup Firebase for Kotlin Notifications
1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/).
2. Generate the `google-services.json` file for your project.
3. Rename this file to `ming_sec_firebase.json` and save it in the `Local` folder (the same folder as `main.py`).
> You can get the `NOTIFICATION_DEVICE_TOKEN` from the Kotlin app after setting up Firebase notifications.