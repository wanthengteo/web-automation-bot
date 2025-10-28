from playwright.sync_api import sync_playwright
import time

LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
    )
    page = browser.new_page()

    page.goto(LOGIN_URL)
    page.fill('input[name="ctl00$MainContent$txtEmpID"]', USERNAME)
    page.fill('input[name="ctl00$MainContent$txtPassword"]', PASSWORD)
    page.click('input[name="ctl00$MainContent$btnSignIn"]')

    page.wait_for_load_state("networkidle")

    page.goto("http://103.230.126.114/eportal/admin/processor/lvhistoryepe.aspx")
    page.wait_for_load_state("networkidle")

    # === Fill in date range ===
    page.fill('input[name="ctl00$MainContent$txtFromDate"]', "")
    page.fill('input[name="ctl00$MainContent$txtToDate"]', "")
    page.fill('input[name="ctl00$MainContent$txtFromDate"]', "01/01/2025")
    page.fill('input[name="ctl00$MainContent$txtToDate"]', "31/12/2026")
    page.click('input[name="ctl00$MainContent$btnSearch"]')

    print("⏳ Waiting for results to load and scrolling...")
    page.wait_for_timeout(5000)  # wait 5s for backend processing
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")  # scroll to bottom

    # wait for Save to Excel button to appear
    page.wait_for_selector("input[value='Save to Excel']", timeout=20000)

    print("💾 Clicking Save to Excel...")
    with page.expect_download() as download_info:
        page.click("input[value='Save to Excel']")
    download = download_info.value
    download.save_as("leave_history.xls")

    # Do NOT close before this point
    browser.close()
