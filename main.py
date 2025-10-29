from playwright.sync_api import sync_playwright
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pandas as pd
import os
import json
from datetime import datetime

# === 1. Login configuration ===
LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"
DOWNLOAD_DIR = "."  # Save Excel file in repo root
EXCEL_FILE = "lvhistory.xls"  # Fixed file name
GOOGLE_SHEET_ID = "14O-oINGLnCYwnacAYUL7jF4M-iTDQCI5lrlXwRIF4UQ"  # The stable converted Google Sheet

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

        output_path = os.path.join(DOWNLOAD_DIR, EXCEL_FILE)
        download.save_as(output_path)
        browser.close()

        print(f"✅ Download completed: {output_path}")
        return output_path

# === 3. Overwrite the existing Google Sheet with Excel data ===
def overwrite_google_sheet(excel_path):
    print("📄 Overwriting Google Sheet with Excel data...")

    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"❌ File not found: {excel_path}")

    # Load credentials
    service_account_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT"])
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    sheets_service = build("sheets", "v4", credentials=creds)

    # Read Excel data
    df = pd.read_excel(EXCEL_FILE, engine="xlrd")
    # Columns C,F,G,H,I -> indexes 2,5,6,7,8
    data_to_write = df.iloc[:, [2,5,6,7,8]].values.tolist()

    # Overwrite the Google Sheet starting at A1
    sheets_service.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SHEET_ID,
        range="A1",
        valueInputOption="RAW",
        body={"values": data_to_write}
    ).execute()

    print(f"✅ Google Sheet {GOOGLE_SHEET_ID} overwritten successfully.")

# === 4. Main execution ===
if __name__ == "__main__":
    try:
        excel_path = download_excel()
        overwrite_google_sheet(excel_path)
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
