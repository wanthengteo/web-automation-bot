from playwright.sync_api import sync_playwright
import time

LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(LOGIN_URL)
    page.fill('input[name="ct100$MainContent$txtEmpID"]', USERNAME)
    page.fill('input[name="ct100$MainContent$txtPassword"]', PASSWORD)
    page.click('input[name="ct100$MainContent$btnSignIn"]')

    page.wait_for_load_state("networkidle")

    page.goto("http://103.230.126.114/eportal/admin/processor/lvhistoryepe.aspx")
    # Wait for page to load fully
    page.wait_for_load_state("networkidle")

    # === Fill in date range ===
    # Clear existing date values and input new ones
    page.fill('input[name="ctl00$MainContent$txtFromDate"]', "")
    page.fill('input[name="ctl00$MainContent$txtToDate"]', "")
    page.fill('input[name="ctl00$MainContent$txtFromDate"]', "01/01/2025")
    page.fill('input[name="ctl00$MainContent$txtToDate"]', "31/12/2026")

    # Optional: click Search button if required before downloading
    page.click('input[name="ctl00$MainContent$btnSearch"]')
    page.wait_for_load_state("networkidle")

    # === Download Excel ===
    with page.expect_download() as download_info:
        page.click('text=Save to Excel')
    download = download_info.value
    download.save_as("lvhistory.xls")

    print("✅ Download completed: report.xls")
    browser.close()
