from playwright.sync_api import sync_playwright
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json
import time
from datetime import datetime

# === 1. Login configuration ===
LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"
DOWNLOAD_DIR = "."  # Save Excel file in repo root

# === 2. Automate login & download using Playwright ===
def download_excel():
    print("🚀 Starting browser automation...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()

        # Login
        page.goto(LOGIN_URL)
        page.fill('input[name="ctl00$MainContent$txtEmpID"]', USERNAME)
        page.fill('input[name="ctl00$MainContent$txtPassword"]', PASSWORD)
        page.click('input[name="ctl00$MainContent$btnSignIn"]')
        page.wait_for_load_state("networkidle")

        # Navigate to Leave History page
        page.goto("http://103.230.126.114/eportal/admin/processor/lvhistoryepe.aspx")
        page.wait_for_load_state("networkidle")

        # Fill date range
        page.fill('input[name="ctl00$MainContent$txtFromDate"]', "01/01/2025")
        page.fill('input[name="ctl00$MainContent$txtToDate"]', "31/12/2026")
        page.click('input[name="ctl00$MainContent$btnSearch"]')

        print("⏳ Waiting for results to load...")
        page.wait_for_timeout(7000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Wait for Save to Excel
        page.wait_for_selector("input[value='Save to Excel']", timeout=60000)

        # Download file
        print("💾 Clicking Save to Excel...")
        with page.expect_download() as download_info:
            page.click("input[value='Save to Excel']")
        download = download_info.value

        original_file_name = download.suggested_filename
        output_path = os.path.join(DOWNLOAD_DIR, original_file_name)
        download.save_as(output_path)
        browser.close()

        print(f"✅ Download completed: {output_path}")
        return output_path


# === 3. Upload file to Google Drive (to specific folder) ===
def upload_to_drive(file_path):
    print("📤 Uploading to Google Drive...")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    # Load credentials
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )

    drive_service = build("drive", "v3", credentials=creds)

    # Get folder ID from GitHub Secret
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    if not folder_id:
        raise ValueError("❌ Missing GOOGLE_DRIVE_FOLDER_ID environment variable in GitHub Secrets")

    # Upload file into specific folder
    file_name = os.path.basename(file_path)
    file_metadata = {
        "name": file_name,
        "parents": ["0APR2f6bdTxYtUk9PVA"]  # upload into target folder
    }

    media = MediaFileUpload(file_path, mimetype="application/vnd.ms-excel")
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink",
        supportsAllDrives=True  # <-- important for Shared Drive
    ).execute()

    print(f"✅ File uploaded to folder: {uploaded_file.get('webViewLink')}")


# === 4. Main execution ===
if __name__ == "__main__":
    try:
        excel_path = download_excel()
        upload_to_drive(excel_path)
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
