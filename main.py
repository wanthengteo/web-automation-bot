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

    # Fill in date range
    page.fill('input[name="ctl00$MainContent$txtFromDate"]', "01/01/2025")
    page.fill('input[name="ctl00$MainContent$txtToDate"]', "31/12/2026")
    page.click('input[name="ctl00$MainContent$btnSearch"]')
    page.wait_for_load_state("networkidle")
    time.sleep(5)

    # === DEBUG INFO ===
    print("\n=== FRAMES DETECTED ===")
    for f in page.frames:
        print(f.name, f.url)

    print("\n=== BUTTONS FOUND ===")
    buttons = page.query_selector_all("input[type=submit], button")
    for b in buttons:
        print("name:", b.get_attribute("name"), "| value:", b.get_attribute("value"))

    # Save HTML for inspection
    html_content = page.content()
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("\n✅ Saved current HTML as debug_page.html")

    browser.close()
