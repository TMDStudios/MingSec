import jwt, datetime, json, requests

def generate_firebase_jwt():
    try:
        # Load the Firebase service account JSON file
        with open('ming_sec_firebase.json') as f:
            service_account_info = json.load(f)

        # Extract required values from the service account JSON
        private_key = service_account_info['private_key'].replace('\\n', '\n')
        client_email = service_account_info['client_email']
        project_id = service_account_info['project_id']

        # Define JWT payload
        payload = {
            'iss': client_email,  # Issuer
            'scope': 'https://www.googleapis.com/auth/firebase.messaging',  # Scope for FCM
            'sub': client_email,  # Subject
            'aud': 'https://oauth2.googleapis.com/token',  # Audience
            'iat': datetime.datetime.now(datetime.timezone.utc),  # Issued at
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60),  # Expiration
        }

        # Generate the JWT
        jwt_token = jwt.encode(payload, private_key, algorithm='RS256')

        # Decode the byte string to a regular string
        return jwt_token

    except KeyError as e:
        return f"Error - KeyError: Missing key {e} in the service account JSON file."
    except FileNotFoundError:
        return "Error - FileNotFoundError: The 'ming_sec_firebase.json' file could not be found."
    except Exception as e:
        return f"Error - An unexpected error occurred: {str(e)}"
    
def get_access_token(jwt_token):
    url = "https://oauth2.googleapis.com/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt_token
    }
    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error retrieving access token: {response.status_code} - {response.text}")
        return None

def send_notification(jwt_token, project_id, device_token, notification_title, notification_content):
    access_token = get_access_token(jwt_token)
    if access_token is None:
        return f"Error - Failed to send notification: Invalid access token"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Define the message payload
    message = {
        "message": {
            "token": device_token,
            "notification": {
                "title": notification_title,
                "body": notification_content
            }
        }
    }

    # FCM endpoint for sending messages
    fcm_url = f'https://fcm.googleapis.com/v1/projects/{project_id}/messages:send'

    # Send the POST request
    response = requests.post(fcm_url, headers=headers, json=message)

    # Check the response
    if response.status_code == 200:
        return f"Notification sent successfully"
    else:
        return f"Error - Failed to send notification: {response.status_code}, {response.json()}"