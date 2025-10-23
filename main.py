from playwright.sync_api import sync_playwright
import time

LOGIN_URL = "https://example.com/login"
USERNAME = "your_username"
PASSWORD = "your_password"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(LOGIN_URL)
    page.fill('input[name="username"]', USERNAME)
    page.fill('input[name="password"]', PASSWORD)
    page.click('button[type="submit"]')

    page.wait_for_load_state("networkidle")

    page.goto("https://example.com/report/download")
    with page.expect_download() as download_info:
        page.click('text=Download Report')
    download = download_info.value
    download.save_as("report.xlsx")

    print("✅ Download completed: report.xlsx")
    browser.close()
