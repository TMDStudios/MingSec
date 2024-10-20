import dropbox
from dropbox.exceptions import AuthError

class DropboxHandler:
    DROPBOX_PATH =  "/MingSec/"
    def __init__(self, app_key, app_secret, refresh_token, logger):
        self.app_key = app_key
        self.app_secret = app_secret
        self.refresh_token = refresh_token
        self.logger = logger
        self.connected = False
        self.log_files = []
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
            self.logger.info("Successfully connected to Dropbox Log Handler.")
            return dbx
        except AuthError as e:
            self.logger.error(f'Error connecting to Dropbox with access token: {e}')
            self.connected = False
            return None
        except Exception as e:
            self.logger.error(f'An unexpected error occurred: {e}')
            self.connected = False
            return None

    def get_logs(self):
        self.log_files = []
        try:
            response = self.dbx.files_list_folder(path=self.DROPBOX_PATH)
            for entry in response.entries:
                self.log_files.append(entry.name)
                print(entry.name)

            self.log_files.reverse()
            return "OK"
        except Exception as e:
            self.logger.error(f'Error fetching logs from Dropbox: {e}')
    
    def view_log(self, log_file="log.txt"):
        try:
            self.logger.info(f"Fetching log data for log index: {log_file}")
            metadata, res = self.dbx.files_download(path=self.DROPBOX_PATH+log_file)
            log_data = res.content.decode('utf-8').splitlines()
            return log_data
        except Exception as e:
            self.logger.error(f'Error reading log file: {e}')