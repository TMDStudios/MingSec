import dropbox
from dropbox.exceptions import AuthError

class DropboxHandler:
    def __init__(self, app_key, app_secret, refresh_token, logger, log_handler=False):
        self.app_key = app_key
        self.app_secret = app_secret
        self.refresh_token = refresh_token
        self.logger = logger
        self.connected = False
        self.log_handler = log_handler
        self.dbx = self.connect()

    def connect(self):
        try:
            dbx = dropbox.Dropbox(
                app_key=self.app_key,
                app_secret=self.app_secret,
                oauth2_refresh_token=self.refresh_token
            )
            dbx.users_get_current_account() # Confirm connection
            self.connected = True
            if self.log_handler:
                self.logger.info("Successfully connected to Dropbox Log Handler.")
            else:
                self.logger.info("Successfully connected to Dropbox.")
            return dbx
        except AuthError as e:
            self.logger.error(f'Error connecting to Dropbox with access token: {e}')
            self.connected = False
            return None
        except Exception as e:
            self.logger.error(f'An unexpected error occurred: {e}')
            self.connected = False
            return None

    def upload_file(self, local_path, dropbox_path):
        try:
            with open(local_path, "rb") as f:
                self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
                self.logger.info(f"File uploaded to {dropbox_path}")

                return "OK"
        except Exception as e:
            self.logger.error(f'Error uploading file to Dropbox: {e}')

    # Log file testing
    def get_file(self, dropbox_path):
        try:
            with open('local_file.txt', 'wb') as f:
                metadata, res = self.dbx.files_download(path=dropbox_path)
                f.write(res.content)

                return "OK"
        except Exception as e:
            self.logger.error(f'Error uploading file to Dropbox: {e}')