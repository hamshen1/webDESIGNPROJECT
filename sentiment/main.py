import os
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import csv
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

# Load environment variables from .env file
load_dotenv()

X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")

# Define updated selectors
USERNAME_INPUT_SELECTOR = 'input[autocomplete="username"]'
PASSWORD_INPUT_SELECTOR = 'input[autocomplete="current-password"]'
NEXT_BUTTON_SELECTOR = 'button:has-text("Next")'
LOGIN_BUTTON_SELECTOR = 'button[data-testid="LoginForm_Login_Button"]'
TRENDING_TOPIC_SELECTOR = 'article div[dir="ltr"] span'

# File paths
COOKIES_PATH = "cookies.json"
OUTPUT_CSV = "trending_topics.csv"
SCREENSHOTS_DIR = "screenshots"

async def take_screenshot(page, step_name):
    """Take a screenshot and save it to the screenshots directory with a timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SCREENSHOTS_DIR}/{timestamp}_{step_name}.png"
    await page.screenshot(path=filename)
    logging.info(f"Screenshot saved: {filename}")

async def scrape_trending_topics():
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()

            # Load cookies if available to maintain session
            if os.path.exists(COOKIES_PATH):
                logging.info("Loading cookies to maintain session...")
                with open(COOKIES_PATH, "r") as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)

            page = await context.new_page()

            # Navigate to trending page
            await page.goto("https://x.com/explore/tabs/news", wait_until="networkidle")
            await take_screenshot(page, "trending_page_initial")

            # Check if already logged in by looking for the trending topic selector
            if not await page.query_selector(TRENDING_TOPIC_SELECTOR):
                logging.info("Not logged in. Proceeding to login...")

                # Navigate to login page
                await page.goto("https://x.com/i/flow/login", wait_until="networkidle")
                await take_screenshot(page, "login_page")

                # Step 1: Enter Username
                logging.info("Entering username...")
                await page.wait_for_selector(USERNAME_INPUT_SELECTOR, timeout=15000)
                await page.fill(USERNAME_INPUT_SELECTOR, X_USERNAME)
                await take_screenshot(page, "username_entered")

                # Verify username entry
                entered_username = await page.input_value(USERNAME_INPUT_SELECTOR)
                if entered_username != X_USERNAME:
                    logging.error("Username was not entered correctly.")
                    await take_screenshot(page, "username_not_entered_correctly")
                    return

                # Click 'Next' button
                logging.info("Clicking 'Next' button...")
                await page.wait_for_selector(NEXT_BUTTON_SELECTOR, timeout=15000)
                await page.click(NEXT_BUTTON_SELECTOR)
                await page.wait_for_timeout(2000)  # Wait for transition
                await take_screenshot(page, "after_next_click")

                # Step 2: Enter Password
                logging.info("Entering password...")
                await page.wait_for_selector(PASSWORD_INPUT_SELECTOR, timeout=15000)
                await page.fill(PASSWORD_INPUT_SELECTOR, X_PASSWORD)
                await take_screenshot(page, "password_entered")

                # Verify password entry
                # Note: For security, avoid logging or comparing the actual password

                # Ensure 'Log in' button is enabled
                is_enabled = await page.is_enabled(LOGIN_BUTTON_SELECTOR)
                if not is_enabled:
                    logging.error("'Log in' button is disabled. Password may be incorrect or not properly entered.")
                    await take_screenshot(page, "login_button_disabled")
                    return
                else:
                    logging.info("'Log in' button is enabled.")

                # Click 'Log in' button
                logging.info("Clicking 'Log in' button...")
                await page.click(LOGIN_BUTTON_SELECTOR)
                await page.wait_for_load_state("networkidle")
                await take_screenshot(page, "after_login_click")

                # Save cookies after successful login
                cookies = await context.cookies()
                with open(COOKIES_PATH, "w") as f:
                    json.dump(cookies, f)
                logging.info("Login successful. Cookies saved.")

                # Navigate to trending page again after login
                await page.goto("https://x.com/explore/tabs/news", wait_until="networkidle")
                await take_screenshot(page, "trending_page_logged_in")

            else:
                logging.info("Already logged in.")

            # Scroll to load dynamic content if necessary
            await auto_scroll(page)
            await take_screenshot(page, "after_scrolling")

            # Wait for the trending topics to load
            await page.wait_for_selector(TRENDING_TOPIC_SELECTOR, timeout=10000)

            # Scrape trending topics
            logging.info("Scraping trending topics...")
            trending_elements = await page.query_selector_all(TRENDING_TOPIC_SELECTOR)
            trending_topics = []

            for element in trending_elements:
                try:
                    # Extract topic text
                    topic_text = await element.inner_text()
                    trending_topics.append({"Topic": topic_text.strip()})
                except Exception as e:
                    logging.warning(f"Failed to extract a topic: {e}")

            # Output the scraped data
            logging.info(f"Scraped {len(trending_topics)} trending topics.")

            # Save to CSV
            if trending_topics:
                with open(OUTPUT_CSV, "w", newline='', encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=["Topic"])
                    writer.writeheader()
                    writer.writerows(trending_topics)
                logging.info(f"Data saved to {OUTPUT_CSV}.")
            else:
                logging.info("No trending topics found to save.")

            # Close browser
            await browser.close()

    except PlaywrightTimeoutError as te:
        logging.error(f"Timeout error: {te}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

async def auto_scroll(page):
    """Automatically scrolls the page to load dynamic content."""
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let totalHeight = 0;
                const distance = 100;
                const timer = setInterval(() => {
                    window.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= document.body.scrollHeight) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 100);
            });
        }
    """)

if __name__ == "__main__":
    asyncio.run(scrape_trending_topics())
