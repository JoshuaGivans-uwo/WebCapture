import cv2
import os
import time
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Define Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def authenticate():
    """Authenticate and return Google Drive service using a service account."""
    
    # Path to the service account JSON file
    SERVICE_ACCOUNT_FILE = "./service-account-credentials.json"
    
    # Ensure the file exists
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file '{SERVICE_ACCOUNT_FILE}' not found.")
    
    # Authenticate using the service account file
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    # Return authenticated Drive service
    return build("drive", "v3", credentials=creds)

def capture_image(filename):
    """Capture an image using OpenCV and save it."""
    cap = cv2.VideoCapture(1)  # Open web camera on port 1
    ret, frame = cap.read()  # Capture frame

    if ret:
        os.makedirs("local_store", exist_ok=True)  # Ensure folder exists
        save_path = os.path.join("local_store", filename)  # Set path
        cv2.imwrite(save_path, frame)  # Save image
        print(f"Image saved: {save_path}")
    else:
        print("Failed to capture image.")

    cap.release()
    cv2.destroyAllWindows()

def upload_to_drive(service, filename, folder_id=None):
    save_path = os.path.join("local_store", filename)  # Set path
    """Upload an image to Google Drive."""
    file_metadata = {"name": filename}
    
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(save_path, mimetype="image/jpeg")
    file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    
    print(f"File uploaded: {filename} (ID: {file.get('id')})")

def run_continuous_capture(interval, folder_id=None):
    """Continuously capture and upload images at a given time interval."""
    service = authenticate()  # Authenticate once

    try:
        while True:
            # Generate filename with timestamp
            filename = f"image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            # Capture and upload image
            capture_image(filename)
            upload_to_drive(service, filename, folder_id)

            print(f"Waiting {interval} seconds before next capture...\n")
            time.sleep(interval)

    except KeyboardInterrupt:
        print("Process stopped by user.") #Ctrl+C to stop

if __name__ == "__main__":
    MINUTES = 0.1
    INTERVAL = 60 * MINUTES  # Set the capture interval in seconds
    FOLDER_ID = "1_7AUcGa-lcrayWM1f6iixFXxsQWZuAv2"  # Set this to a specific Google Drive folder ID if needed
    run_continuous_capture(INTERVAL, FOLDER_ID)
