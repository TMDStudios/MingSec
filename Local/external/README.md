# MingSec for External Device

This folder contains the necessary files for running a second camera within MingSec. The entire folder is intended to be moved to a Linux-based external device. (Support for Windows and Mac will be available in future updates.)

## Instructions

1. **Copy Folder to External Device**
   - Transfer this folder to the external device running Linux.

2. **Update Environment Configuration**
   - Navigate to the `Local` folder inside this directory.
   - Update the `.env` file with the correct path to this external folder.

3. **Set Up SSH Connection**
   - Establish an SSH connection between the local and external devices.
   - Update the `.env` file with the necessary SSH variables for this connection.

4. **Create a Virtual Environment**
   - Inside the external folder, create a virtual environment with:
     ```bash
     python3 -m venv venv
     ```

5. **Activate the Virtual Environment**
   - Activate the virtual environment using:
     ```bash
     source venv/bin/activate
     ```

6. **Install Required Packages**
   - Install the required Python packages with:
     ```bash
     pip install -r requirements.txt
     ```

7. **Verify Setup**
   - Your external device should now be ready. You can test the setup by running the following commands:
     ```bash
     python cap_image.py
     python cap_video.py
     ```

## Notes

- Ensure the webcam on the external device is turned on if using a laptop.
- Check if your webcam is recognized with:
  ```bash
  v4l2-ctl --all
  ```
- Ensure that the external device has Python 3.x installed.
- Make sure to follow all SSH and configuration steps carefully to ensure proper setup.