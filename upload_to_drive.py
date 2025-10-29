import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === 1. Load service account credentials from GitHub Secret ===
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive.file"]
)

# === 2. Connect to Google Drive ===
drive_service = build("drive", "v3", credentials=creds)

# === 3. Define file to upload ===
file_path = "leave_history.xls"   # Must match your main.py saved file
file_name = "leave_history.xls"

if not os.path.exists(file_path):
    raise FileNotFoundError(f"❌ File not found: {file_path}")

# === 4. Prepare file metadata ===
file_metadata = {"name": file_name}

# === 5. Upload the file ===
media = MediaFileUpload(file_path, mimetype="application/vnd.ms-excel")
uploaded_file = drive_service.files().create(
    body=file_metadata,
    media_body=media,
    fields="id, webViewLink"
).execute()

print(f"✅ File uploaded successfully: {uploaded_file.get('webViewLink')}")
