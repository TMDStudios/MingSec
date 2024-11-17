# MingSec Local Setup

This guide walks you through setting up the local MingSec system.

>MingSec currently only runs on Windows, but it may be used on Mac/Linux with some adjustments.

## Prerequisites

- Python 3.8 or higher
- A [Dropbox account](https://www.dropbox.com/) (if you don’t already have one)
- (Recommended) [GitBash](https://git-scm.com/downloads) (Some bash commands will look different if you are not using GitBash)
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
Generate a `.env` file in the `local` folder with the following command:

```bash
winpty python dot_env_generator.py
```

Then, open the `.env` file and replace the placeholder values with your own credentials, including the Dropbox `APP_KEY`, `APP_SECRET`, and `REFRESH_TOKEN`.

---

### 5. (Optional) Copy to an External Linux Device
If you’re using a second camera connected to a Linux device, copy the `external` folder from your MingSec project directory to the target device. You can place the folder wherever is convenient, but make sure to update the `EXTERNAL_DEVICE_PATH` in your `.env` file to reflect the correct location.
If you're not using a second camera, you can skip this step.

### 6. (Optional) Setup Firebase for Kotlin Notifications
1. Create a Firebase project in the [Firebase Console](https://console.firebase.google.com/).
2. Generate the `google-services.json` file for your project.
3. Rename this file to `ming_sec_firebase.json` and save it in the `Local` folder (the same folder as `main.py`).
> You can get the `NOTIFICATION_DEVICE_TOKEN` from the Kotlin app after setting up Firebase notifications.

---

### Start MingSec
Run the following command to start MingSec:

```bash
winpty python main.py
```