# MingSec Django Setup

This guide walks you through setting up the Django project which allows you to control MingSec remotely.

>**Important:** Be sure to set up your local files ([Local System Setup](../Local/README.md)) before setting up Django

## Prerequisites

- Python 3.8 or higher
- (Recommended) [GitBash](https://git-scm.com/downloads) (Some bash commands will look different if you are not using GitBash)

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

### 3. Configure Environment Variables
Generate a `.env` file by running the following command:

```bash
winpty python dot_env_generator.py
```

Open the .env file and replace the placeholder values with your own credentials (the credentials can be found in the `.env` file you created in the `local` folder):

- API_KEY - Your API Key
- DROPBOX_APP_KEY_RW - Your Dropbox app key
- DROPBOX_APP_SECRET_RW - Your Dropbox app secret
- DROPBOX_REFRESH_TOKEN_RW - Your Dropbox refresh token

### 4. Database Setup
Run the following commands to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Django Super User
Run the following command:

```bash
python manage.py createsuperuser
```

Django will prompt you to enter the following information for the superuser:

- Username: The username you'll use to log in to the Django admin interface (e.g., admin).
- Email address: The email associated with the superuser account.
- Password: The password for the superuser account (you'll need to confirm the password by entering it twice).

### 6. Run the Django Development Server
Once your environment is set up and all credentials are configured:

```bash
python manage.py runserver
```

This will start the Django development server. You can now visit http://127.0.0.1:8000 in your browser to see the app in action.

### 7. Deploy to [pythonanywhere](https://www.pythonanywhere.com/)
To deploy your project to PythonAnywhere, follow these steps:

Create an account or log in to [pythonanywhere](https://www.pythonanywhere.com/).
Follow their detailed instructions on how to deploy an existing Django project: [PythonAnywhere Django Deployment Guide](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)

> Feel free to deploy to any platform that suits your needs, but I personally prefer [pythonanywhere](https://www.pythonanywhere.com/) due to its ease of use.

### 8. Update `.env` file in the `local` folder

Now, go back to the `.env` file in the `local` folder and replace `http://localhost:8000` with your pythonanywhere URL (i.e. `https://mypage.pythonanywhere.com`):

- CAM_REQUEST_ENDPOINT=http://localhost:8000/api/requests/get/
- ALARM_REPORT_ENDPOINT=http://localhost:8000/api/alarms/add/
- STATUS_REPORT_ENDPOINT=http://localhost:8000/api/status/add/

> You can use `http://localhost:8000` for testing, but it will not work remotely