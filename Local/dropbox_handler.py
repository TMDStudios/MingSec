import dropbox
from dropbox.exceptions import AuthError

class DropboxHandler:
    def __init__(self, app_key, app_secret, refresh_token, logger):
        self.app_key = app_key
        self.app_secret = app_secret
        self.refresh_token = refresh_token
        self.logger = logger
        self.dbx = self.connect()
        self.connected = False

    def connect(self):
        try:
            dbx = dropbox.Dropbox(
                app_key=self.app_key,
                app_secret=self.app_secret,
                oauth2_refresh_token=self.refresh_token
            )
            dbx.users_get_current_account() # Confirm connection
            self.connected = True
            self.logger.info("Successfully connected to Dropbox.")
            return dbx
        except AuthError as e:
            self.logger.error('Error connecting to Dropbox with access token:', e)
            self.connected = False
            return None
        except Exception as e:
            self.logger.error('An unexpected error occurred:', e)
            self.connected = False
            return None

    def upload_file(self, local_path, dropbox_path):
        try:
            with open(local_path, "rb") as f:
                meta = self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
                self.logger.info(f"File uploaded to {dropbox_path}")
                return meta
        except Exception as e:
            self.logger.error('Error uploading file to Dropbox:', e)