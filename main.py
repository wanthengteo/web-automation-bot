from playwright.sync_api import sync_playwright
import time
import os

LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"

DOWNLOAD_DIR = "."  # ✅ add this line

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
    )
    page = browser.new_page()

    # === LOGIN ===
    page.goto(LOGIN_URL)
    page.fill('input[name="ctl00$MainContent$txtEmpID"]', USERNAME)
    page.fill('input[name="ctl00$MainContent$txtPassword"]', PASSWORD)
    page.click('input[name="ctl00$MainContent$btnSignIn"]')
    page.wait_for_load_state("networkidle")

    # === NAVIGATE TO LEAVE HISTORY PAGE ===
    page.goto("http://103.230.126.114/eportal/admin/processor/lvhistoryepe.aspx")
    page.wait_for_load_state("networkidle")

    # === ENTER DATE RANGE ===
    page.fill('input[name="ctl00$MainContent$txtFromDate"]', "01/01/2025")
    page.fill('input[name="ctl00$MainContent$txtToDate"]', "31/12/2026")
    page.click('input[name="ctl00$MainContent$btnSearch"]')

    print("⏳ Waiting for results to load and scrolling...")
    page.wait_for_timeout(7000)  # allow time for backend processing
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # scroll to bottom

    # === ENSURE SAVE TO EXCEL IS VISIBLE ===
    page.wait_for_selector("input[value='Save to Excel']", timeout=30000)
    page.evaluate("document.querySelector('input[value=\"Save to Excel\"]').scrollIntoView()")
    page.wait_for_timeout(1000)

    # === DOWNLOAD FILE ===
    print("💾 Clicking Save to Excel...")
    with page.expect_download() as download_info:
        page.click("input[value='Save to Excel']")
    download = download_info.value
    
    # Save into local Downloads folder
    output_path = os.path.join(DOWNLOAD_DIR, "leave_history.xls")
    download.save_as(output_path)

    print(f"✅ Download completed: {output_path}")

    browser.close()
