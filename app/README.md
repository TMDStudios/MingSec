# MingSec App Setup

This guide walks you through setting up the Kotlin app to receive notifications and view all alarm reports.

>**Important:** Be sure to set up your local files ([Local System Setup](../Local/README.md)) and the Django project ([Django Setup](../core/README.md)) before setting up the app.

## Prerequisites

- Java 17
- Android Studio
- (Recommended) [GitBash](https://git-scm.com/downloads) (Some bash commands will look different if you are not using GitBash)

## Installation Instructions

### 1. Create an `env` File
- Navigate to the `main` folder (`app -> src -> main`)
- Create an `assets` folder
- Create an `env` file using GitBash and the following command:

```bash
touch env
```

Paste the following into your `env` file:
```plaintext
BASE_URL=YOUR_PROJECT_URL
API_KEY=YOUR_API_KEY
```

Both values can be found in your Django `.env` file. For the BASE_URL, you do not need the API endpoint. It should look something like this: `https://yourproject.pythonanywhere.com/`

### 2. Add Google Services File to the Project
- If you did not complete step 6 in the `core` README ([Local System Setup](../Local/README.md)), you should do that now.
- Once you have set up a Firebase project, you can download the Google Services file by following ([these steps](https://support.google.com/firebase/answer/7015592?hl=en#zippy=%2Cin-this-article))
- Move the downloaded file to the `app` folder (the same folder as `build`, `libs`, `src`)

### 3. Install Application
- Open the project in Android Studio
- Connect your phone
- Run the application on your phone

### 4. Update the `.env` File in the `Local` folder
- You need to update the last field (`NOTIFICATION_DEVICE_TOKEN`) in the `.env` file. Your `FIREBASE_PROJECT_ID` should have been updated during step 2.
- Open the Kotlin app on your phone and tap the `Notification Device Token` button at the top. Copy this token to the `.env` file.