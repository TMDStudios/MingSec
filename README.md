# MingSec

![GitHub Badge](https://img.shields.io/badge/deployment-GitHub-black) ![pythonanywhere Badge](https://img.shields.io/badge/deployment-railway-lightblue)

![MingSec Logo](/core/frontend/static/media/MingSec.png)

MingSec is a basic home security system designed to leverage OpenCV for motion detection. It features motion detection, image/video capture, alarm responses, offline operation, a REST API for remote management, and a Kotlin app for notifications.

## Features

- **Motion Detection**: Utilizes OpenCV to detect motion and trigger responses.
- **Image Capture**: Captures and uploads an image every ten minutes to Dropbox.
- **Alarm Response**: Captures an image and records a video if the alarm is triggered. Both are uploaded to Dropbox.
- **Offline Operation**: Logs all videos and images when the internet connection is down, and uploads them once the connection is restored.
- **REST API**: Provides endpoints for users to check the status of each camera and request images or videos.
- **Kotlin Notification App**: A companion mobile app developed in Kotlin that receives notifications each time an alarm is triggered.

## Project Structure:

- **docs/** - Contains a Single Page Application (SPA) for the project demo.
- **core/** - Includes the REST API and user interface for remote control and system management.
- **local/** - Contains the MingSec application, including configuration files and local scripts.
- **app/** - Contains the Kotlin notification app that receives alerts for triggered alarms.

## Installation Guides

- [MingSec Demo](https://tmdstudios.github.io/MingSec/): A brief demo that showcases how MingSec works.
- [Core Setup](core/README.md): Instructions for setting up the REST API and user interface.
- [Local System Setup](Local/README.md): Steps to configure and run the local MingSec application.
- [Kotlin App Setup](app/README.md): Guide for building and deploying the Kotlin notification app.

## License

- This project is licensed under the GPL-3.0 License. See [LICENSE](https://github.com/TMDStudios/MingSec/blob/main/LICENSE) for details.

## Acknowledgements

- OpenCV for motion detection capabilities.
- Dropbox for storage solutions.
- Firebase for alarm notifications.

## You May Also Like...

[Py Learning Companion](https://play.google.com/store/apps/details?id=com.tmdstudios.python 'Py Learning Companion') - Python Study App

[Study Room](https://github.com/TMDStudios/StudyRoom 'Study Room') - Open-source platform for students to improve their English vocabulary and grammar

[Game Room](https://github.com/TMDStudios/GameRoom 'Game Room') - A platform for educators to play games and/or review materials with their students

[Road to Rage Demo](https://github.com/TMDStudios/rtr 'Road to Rage Demo') - Open-source demo of Road to Rage (a vertical shmup)

[TMD Studios](https://tmdstudios.net 'TMD Studios') - A simple one-page website to showcase TMD Studios projects.