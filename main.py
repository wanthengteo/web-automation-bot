from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import os

# ===== CONFIG =====
file_path = "./lvhistory.xls"  # Path to downloaded Excel
file_name = "lvhistory.xls"    # File name in Shared Drive
folder_id = "0APR2f6bdTxYtUk9PVA"  # Your Shared Drive folder ID

# ===== LOAD CREDENTIALS =====
service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
creds = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive_service = build("drive", "v3", credentials=creds)

# ===== CHECK IF FILE EXISTS =====
query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
results = drive_service.files().list(q=query, fields="files(id, name)").execute()
files = results.get("files", [])

if files:
    # File exists → update it
    file_id = files[0]["id"]
    media = MediaFileUpload(file_path, mimetype="application/vnd.ms-excel")
    updated_file = drive_service.files().update(
        fileId=file_id,
        media_body=media
    ).execute()
    print(f"✅ File updated: {updated_file.get('name')}")
else:
    # File does not exist → create new
    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(file_path, mimetype="application/vnd.ms-excel")
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        supportsAllDrives=True
    ).execute()
    print(f"✅ File uploaded: {uploaded_file.get('name')}")
