from playwright.sync_api import sync_playwright
import time

LOGIN_URL = "http://103.230.126.114/eportal/public/signin.aspx"
USERNAME = "HR008"
PASSWORD = "12345678"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(LOGIN_URL)
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="Sign-in"]')

    page.wait_for_load_state("networkidle")

    page.goto("http://103.230.126.114/eportal/admin/processor/lvhistoryepe.aspx")
    with page.expect_download() as download_info:
        page.click('text=Save to Excel')
    download = download_info.value
    download.save_as("report.xlsx")

    print("✅ Download completed: report.xlsx")
    browser.close()
