# combined.py

import os
import asyncio
import json
import csv
import logging
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve login credentials from environment variables
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
X_EMAIL = os.getenv("X_EMAIL")  # Optional: May not always be required

# Validate that essential credentials are provided
if not X_USERNAME or not X_PASSWORD:
    logging.error("Please set X_USERNAME and X_PASSWORD in the .env file.")
    exit(1)

# Define selectors based on provided HTML snippets and attributes
SELECTORS = {
    "username_input": 'input[autocomplete="username"]',
    "username_next_button": 'button:has-text("Next")',
    "email_input": 'input[data-testid="ocfEnterTextTextInput"]',
    "email_next_button": 'button[data-testid="ocfEnterTextNextButton"]',
    "password_input": 'input[autocomplete="current-password"]',
    "password_reveal_button": 'button[aria-label="Reveal password"]',  # Optional
    "login_button": 'button[data-testid="LoginForm_Login_Button"]',
    "trend_container": 'div[data-testid="trend"]',
    "trend_category": 'span:nth-of-type(1)',
    "trend_topic": 'span:nth-of-type(2)',
    "trend_posts": 'span:nth-of-type(3)'
}

# Define file paths
COOKIES_PATH = "cookies.json"
SCREENSHOTS_DIR = "screenshots"
LOG_FILE = "scraper.log"

# Configure logging to output to both console and a log file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

async def take_screenshot(page, step_name: str, folder_path: str):
    """
    Take a screenshot and save it to the specified folder with a descriptive name.
    Ensures that the screenshot captures the full page content.
    """
    try:
        filename = os.path.join(folder_path, f"{step_name}.png")
        await page.screenshot(path=filename, full_page=True)
        logging.info(f"Screenshot saved: {filename}")
    except Exception as e:
        logging.error(f"Failed to take screenshot for '{step_name}': {e}")

def create_screenshot_folder(screenshots_dir: str) -> str:
    """
    Create a new folder within the screenshots directory named with the current timestamp.
    Returns the path to the newly created folder.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"screenshot_{timestamp}"
    folder_path = os.path.join(screenshots_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    logging.info(f"Created screenshot folder: '{folder_path}/'")
    return folder_path

async def perform_combined_task():
    """
    Perform login and scraping in a single browser session to verify cookie functionality.
    """
    folder_path = create_screenshot_folder(SCREENSHOTS_DIR)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Step 1: Navigate to login page
        page = await context.new_page()
        logging.info("Navigating to login page...")
        try:
            await page.goto("https://x.com/i/flow/login", wait_until="networkidle")
            await take_screenshot(page, "login_page", folder_path)
        except Exception as e:
            logging.error(f"Failed to navigate to login page: {e}")
            await take_screenshot(page, "login_page_error", folder_path)
            await browser.close()
            return

        # Step 2: Enter username
        logging.info("Entering username...")
        try:
            await page.wait_for_selector(SELECTORS["username_input"], timeout=15000)
            await page.fill(SELECTORS["username_input"], X_USERNAME)
            await take_screenshot(page, "username_entered", folder_path)

            # Verify username entry
            entered_username = await page.input_value(SELECTORS["username_input"])
            if entered_username != X_USERNAME:
                logging.error("Username was not entered correctly.")
                await take_screenshot(page, "username_verification_failed", folder_path)
                await browser.close()
                return
        except PlaywrightTimeoutError:
            logging.error(f"Username input field '{SELECTORS['username_input']}' not found.")
            await take_screenshot(page, "username_input_not_found", folder_path)
            await browser.close()
            return
        except Exception as e:
            logging.error(f"Error entering username: {e}")
            await take_screenshot(page, "username_entry_error", folder_path)
            await browser.close()
            return

        # Step 3: Click 'Next' after username
        logging.info("Clicking 'Next' button after username...")
        try:
            await page.wait_for_selector(SELECTORS["username_next_button"], timeout=15000)
            await page.click(SELECTORS["username_next_button"])
            await page.wait_for_timeout(3000)  # Wait for transition
            await take_screenshot(page, "after_username_next_click", folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"'Next' button '{SELECTORS['username_next_button']}' not found or not clickable after username.")
            await take_screenshot(page, "next_button_after_username_not_found", folder_path)
            await browser.close()
            return
        except Exception as e:
            logging.error(f"Error clicking 'Next' button after username: {e}")
            await take_screenshot(page, "next_button_after_username_click_error", folder_path)
            await browser.close()
            return

        # Step 4: Determine if email authentication is required
        logging.info("Determining if email authentication is required...")
        try:
            email_input = await page.query_selector(SELECTORS["email_input"])
            if email_input:
                logging.info("Email authentication is required.")

                # Enter email
                logging.info("Entering email...")
                try:
                    await page.fill(SELECTORS["email_input"], X_EMAIL)
                    await take_screenshot(page, "email_entered", folder_path)

                    # Verify email entry
                    entered_email = await page.input_value(SELECTORS["email_input"])
                    if entered_email != X_EMAIL:
                        logging.error("Email was not entered correctly.")
                        await take_screenshot(page, "email_verification_failed", folder_path)
                        await browser.close()
                        return
                except PlaywrightTimeoutError:
                    logging.error(f"Email input field '{SELECTORS['email_input']}' not found.")
                    await take_screenshot(page, "email_input_not_found", folder_path)
                    await browser.close()
                    return
                except Exception as e:
                    logging.error(f"Error entering email: {e}")
                    await take_screenshot(page, "email_entry_error", folder_path)
                    await browser.close()
                    return

                # Click 'Next' after email
                logging.info("Clicking 'Next' button after email...")
                try:
                    await page.wait_for_selector(SELECTORS["email_next_button"], timeout=15000)
                    await page.click(SELECTORS["email_next_button"])
                    await page.wait_for_timeout(3000)  # Wait for transition
                    await take_screenshot(page, "after_email_next_click", folder_path)
                except PlaywrightTimeoutError:
                    logging.error(f"'Next' button '{SELECTORS['email_next_button']}' not found or not clickable after email.")
                    await take_screenshot(page, "next_button_after_email_not_found", folder_path)
                    await browser.close()
                    return
                except Exception as e:
                    logging.error(f"Error clicking 'Next' button after email: {e}")
                    await take_screenshot(page, "next_button_after_email_click_error", folder_path)
                    await browser.close()
                    return
            else:
                logging.info("Email authentication is not required.")
        except Exception as e:
            logging.error(f"Error determining authentication flow: {e}")
            await take_screenshot(page, "authentication_flow_error", folder_path)
            await browser.close()
            return

        # Step 5: Enter password
        logging.info("Entering password...")
        try:
            await page.wait_for_selector(SELECTORS["password_input"], timeout=15000)
            await page.fill(SELECTORS["password_input"], X_PASSWORD)
            await take_screenshot(page, "password_entered", folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"Password input field '{SELECTORS['password_input']}' not found.")
            await take_screenshot(page, "password_input_not_found", folder_path)
            await browser.close()
            return
        except Exception as e:
            logging.error(f"Error entering password: {e}")
            await take_screenshot(page, "password_entry_error", folder_path)
            await browser.close()
            return

        # Step 6: Ensure 'Log in' button is enabled
        logging.info("Ensuring 'Log in' button is enabled...")
        try:
            await page.wait_for_selector(SELECTORS["login_button"], timeout=15000)
            is_enabled = await page.is_enabled(SELECTORS["login_button"])
            if not is_enabled:
                logging.error("'Log in' button is disabled. Password may be incorrect or not properly entered.")
                await take_screenshot(page, "login_button_disabled", folder_path)
                await browser.close()
                return
            else:
                logging.info("'Log in' button is enabled.")
        except PlaywrightTimeoutError:
            logging.error(f"'Log in' button '{SELECTORS['login_button']}' not found.")
            await take_screenshot(page, "login_button_not_found", folder_path)
            await browser.close()
            return
        except Exception as e:
            logging.error(f"Error checking 'Log in' button state: {e}")
            await take_screenshot(page, "login_button_state_error", folder_path)
            await browser.close()
            return

        # Step 7: Click 'Log in' button
        logging.info("Clicking 'Log in' button...")
        try:
            await page.click(SELECTORS["login_button"])
            await page.wait_for_load_state("networkidle")
            await take_screenshot(page, "after_login_click", folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"'Log in' button '{SELECTORS['login_button']}' not found or not clickable.")
            await take_screenshot(page, "login_button_not_clickable", folder_path)
            await browser.close()
            return
        except Exception as e:
            logging.error(f"Error clicking 'Log in' button: {e}")
            await take_screenshot(page, "login_button_click_error", folder_path)
            await browser.close()
            return

        # Step 8: Save cookies post-login
        logging.info("Saving cookies after successful login...")
        try:
            cookies = await context.cookies()
            # Convert cookies to a serializable format
            cookies_serializable = [{
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie["domain"],
                "path": cookie.get("path", "/"),
                "expires": cookie.get("expires"),
                "httpOnly": cookie.get("httpOnly", False),
                "secure": cookie.get("secure", False),
                "sameSite": cookie.get("sameSite", "Lax")
            } for cookie in cookies]
            with open(COOKIES_PATH, "w") as f:
                json.dump(cookies_serializable, f, indent=4)
            logging.info("Login successful. Cookies saved.")
            await take_screenshot(page, "logged_in_successfully", folder_path)
        except Exception as e:
            logging.error(f"Failed to save cookies: {e}")
            await take_screenshot(page, "save_cookies_error", folder_path)

        # Step 9: Navigate to news page to verify authentication
        logging.info("Navigating to news page to verify authentication...")
        try:
            await page.goto("https://x.com/explore/tabs/news", wait_until="networkidle")
            await take_screenshot(page, "news_page_after_login", folder_path)

            # Check for an authenticated element
            AUTH_SELECTOR = 'img[alt="User Avatar"]'  # Adjust based on actual site
            if await page.query_selector(AUTH_SELECTOR):
                logging.info("Authenticated session confirmed via cookies.")
            else:
                logging.warning("Authenticated session not confirmed. Cookies may be invalid or expired.")
        except Exception as e:
            logging.error(f"Error navigating to news page after login: {e}")

        # Step 10: Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(perform_combined_task())
