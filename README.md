# MingSec

MingSec is a basic home security system designed to leverage OpenCV for motion detection. It offers features like motion detection, image capture, alarm responses, offline operation, and a REST API for remote management.

## Features

- **Motion Detection**: Utilizes OpenCV to detect motion and trigger responses.
- **Image Capture**: Captures and uploads an image every ten minutes to Dropbox.
- **Alarm Response**: Captures an image and records a video if the alarm is triggered. Both are uploaded to Dropbox.
- **Offline Operation**: Logs all videos and images when the internet connection is down, and uploads them once the connection is restored.
- **REST API**: Provides endpoints for users to check the status of each camera and request images or videos.

## Project Structure:

- **FrontEnd/** - Contains a Single Page Application (SPA) for accessing the MingSec API. This is the user interface for interacting with the security system.
- **BackEnd/** - Includes the Rest API that controls the security system remotely. This is responsible for handling requests from the SPA and managing the system's core functionalities.
- **Local/** - Contains the MingSec application, including configuration files and local scripts for running the system.

## License

- This project is licensed under the GPL-3.0 License. See [LICENSE](https://github.com/TMDStudios/MingSec/blob/main/LICENSE) for details.

## Acknowledgements

- OpenCV for motion detection capabilities.
- Dropbox for storage solutions.

## You May Also Like...

[Py Learning Companion](https://play.google.com/store/apps/details?id=com.tmdstudios.python 'Py Learning Companion') - Python Study App

[Study Room](https://github.com/TMDStudios/StudyRoom 'Study Room') - Open-source platform for students to improve their English vocabulary and grammar

[Mock Trader](https://github.com/TMDStudios/MockTrader 'Mock Trader') - Open-source Bitcoin trading game

[Crypto Ledger](https://play.google.com/store/apps/details?id=com.tmdstudios.cryptoledgerkotlin 'Crypto Ledger') - Open-source app for tracking cryptocurrency trades

[Game Room](https://github.com/TMDStudios/GameRoom 'Game Room') - A platform for educators to play games and/or review materials with their students

[TMD Studios](https://tmdstudios.net 'TMD Studios') - A simple one-page website to showcase TMD Studios projects.
