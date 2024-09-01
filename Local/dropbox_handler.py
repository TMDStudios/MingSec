import dropbox
from dropbox.exceptions import AuthError

class DropboxHandler:
    def __init__(self, app_key, app_secret, refresh_token):
        self.app_key = app_key
        self.app_secret = app_secret
        self.refresh_token = refresh_token
        self.dbx = self.connect()

    def connect(self):
        try:
            return dropbox.Dropbox(
                app_key=self.app_key,
                app_secret=self.app_secret,
                oauth2_refresh_token=self.refresh_token
            )
        except AuthError as e:
            print('Error connecting to Dropbox with access token:', e)
            return None

    def upload_file(self, local_path, dropbox_path):
        try:
            with open(local_path, "rb") as f:
                meta = self.dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode("overwrite"))
                print(f"File uploaded to {dropbox_path}")
                return meta
        except Exception as e:
            print('Error uploading file to Dropbox:', e)