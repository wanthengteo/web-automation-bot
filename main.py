from playwright.sync_api import sync_playwright
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import os
import json

# === 1. Login configuration ===
LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"
DOWNLOAD_DIR = "."  # Save Excel file in repo root
EXCEL_FILE = "lvhistory.xls"  # Fixed file name

# Get Sheet ID from environment (GitHub Secret)
GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]

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
        page.c
