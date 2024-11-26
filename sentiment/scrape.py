from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    
    # Open a new page
    page = context.new_page()
    
    # Navigate to the target website
    page.goto("https://x.com/login")
    
    # Perform actions (e.g., take a screenshot)
    page.screenshot(path="example.png")
    
    # Extract page content or perform scraping as needed
    title = page.title()
    print(f"Page Title: {title}")
    
    # Close browser
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
