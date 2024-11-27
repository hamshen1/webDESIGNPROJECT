import os
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv
import json
import logging
from datetime import datetime

# =========================
# Configuration and Setup
# =========================

# Configure logging to output to both console and a log file
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

# Retrieve login credentials from environment variables
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
X_EMAIL = os.getenv("X_EMAIL")  # Ensure this is set in the .env file

# Validate that credentials are provided
if not X_USERNAME or not X_PASSWORD:
    logging.error("Please set X_USERNAME and X_PASSWORD in the .env file.")
    exit(1)

# EMAIL may not be required if the flow skips email authentication

# =========================
# Updated Selectors
# =========================

# Based on the provided HTML snippets, updated selectors are defined below.

# Username Input Selector
USERNAME_INPUT_SELECTOR = 'input[autocomplete="username"]'

# Username Next Button Selector
USERNAME_NEXT_BUTTON_SELECTOR = 'button:has-text("Next")'

# Email Input Selector (using data-testid)
EMAIL_INPUT_SELECTOR = 'input[data-testid="ocfEnterTextTextInput"]'

# Email Next Button Selector (using data-testid)
EMAIL_NEXT_BUTTON_SELECTOR = 'button[data-testid="ocfEnterTextNextButton"]'

# Password Input Selector
PASSWORD_INPUT_SELECTOR = 'input[autocomplete="current-password"]'

# Password Reveal Button Selector (optional, if you need to interact with it)
PASSWORD_REVEAL_BUTTON_SELECTOR = 'button[aria-label="Reveal password"]'

# Login Button Selector (using data-testid)
LOGIN_BUTTON_SELECTOR = 'button[data-testid="LoginForm_Login_Button"]'

# Define file paths
COOKIES_PATH = "cookies.json"
SCREENSHOTS_DIR = "screenshots"

# =========================
# Helper Functions
# =========================

def create_screenshot_folder():
    """
    Create a new folder within the screenshots directory named with the current timestamp.
    Returns the path to the newly created folder.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"screenshot_{timestamp}"
    folder_path = os.path.join(SCREENSHOTS_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    logging.info(f"Created screenshot folder: '{folder_path}/'")
    return folder_path

async def take_screenshot(page, step_name, folder_path):
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

# =========================
# Main Scraper Function
# =========================

async def login_to_xcom():
    try:
        async with async_playwright() as p:
            # Launch browser in headless mode suitable for non-GUI environments
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()

            # Load cookies if available to maintain session
            if os.path.exists(COOKIES_PATH):
                logging.info("Loading cookies to maintain session...")
                try:
                    with open(COOKIES_PATH, "r") as f:
                        cookies = json.load(f)
                        # Convert cookies to the format expected by Playwright
                        cookies = [{
                            "name": cookie["name"],
                            "value": cookie["value"],
                            "domain": cookie["domain"],
                            "path": cookie.get("path", "/"),
                            "expires": cookie.get("expires"),
                            "httpOnly": cookie.get("httpOnly", False),
                            "secure": cookie.get("secure", False),
                            "sameSite": cookie.get("sameSite", "Lax")
                        } for cookie in cookies]
                        await context.add_cookies(cookies)
                    logging.info("Cookies loaded successfully.")
                except Exception as e:
                    logging.error(f"Failed to load cookies: {e}")

            page = await context.new_page()

            # Create a unique folder for this run's screenshots
            folder_path = create_screenshot_folder()

            # Navigate to login page
            logging.info("Navigating to login page...")
            try:
                await page.goto("https://x.com/i/flow/login", wait_until="networkidle")
                await take_screenshot(page, "login_page", folder_path)
            except Exception as e:
                logging.error(f"Failed to navigate to login page: {e}")
                await take_screenshot(page, "login_page_error", folder_path)
                return

            # =========================
            # Step 1: Enter Username
            # =========================
            logging.info("Entering username...")
            try:
                await page.wait_for_selector(USERNAME_INPUT_SELECTOR, timeout=15000)
                await page.fill(USERNAME_INPUT_SELECTOR, X_USERNAME)
                await take_screenshot(page, "username_entered", folder_path)

                # Verify username entry
                entered_username = await page.input_value(USERNAME_INPUT_SELECTOR)
                if entered_username != X_USERNAME:
                    logging.error("Username was not entered correctly.")
                    await take_screenshot(page, "username_verification_failed", folder_path)
                    return

            except PlaywrightTimeoutError:
                logging.error(f"Username input field '{USERNAME_INPUT_SELECTOR}' not found.")
                await take_screenshot(page, "username_input_not_found", folder_path)
                return
            except Exception as e:
                logging.error(f"Error entering username: {e}")
                await take_screenshot(page, "username_entry_error", folder_path)
                return

            # =========================
            # Step 2: Click 'Next' Button After Username
            # =========================
            logging.info("Clicking 'Next' button after username...")
            try:
                await page.wait_for_selector(USERNAME_NEXT_BUTTON_SELECTOR, timeout=15000)
                await page.click(USERNAME_NEXT_BUTTON_SELECTOR)
                await page.wait_for_timeout(3000)  # Wait for transition
                await take_screenshot(page, "after_username_next_click", folder_path)
            except PlaywrightTimeoutError:
                logging.error(f"'Next' button '{USERNAME_NEXT_BUTTON_SELECTOR}' not found or not clickable after username.")
                await take_screenshot(page, "next_button_after_username_not_found", folder_path)
                return
            except Exception as e:
                logging.error(f"Error clicking 'Next' button after username: {e}")
                await take_screenshot(page, "next_button_after_username_click_error", folder_path)
                return

            # =========================
            # Step 3: Determine Flow (Email Authentication or Direct to Password)
            # =========================
            logging.info("Determining if email authentication is required...")
            try:
                # Attempt to locate the email input field with a short timeout
                email_input_present = await page.query_selector(EMAIL_INPUT_SELECTOR)
                if email_input_present:
                    logging.info("Email authentication is required. Proceeding to enter email.")
                    # =========================
                    # Step 3A: Enter Email
                    # =========================
                    try:
                        await page.wait_for_selector(EMAIL_INPUT_SELECTOR, timeout=15000)
                        await page.fill(EMAIL_INPUT_SELECTOR, X_EMAIL)
                        await take_screenshot(page, "email_entered", folder_path)

                        # Verify email entry
                        entered_email = await page.input_value(EMAIL_INPUT_SELECTOR)
                        if entered_email != X_EMAIL:
                            logging.error("Email was not entered correctly.")
                            await take_screenshot(page, "email_verification_failed", folder_path)
                            return

                    except PlaywrightTimeoutError:
                        logging.error(f"Email input field '{EMAIL_INPUT_SELECTOR}' not found.")
                        await take_screenshot(page, "email_input_not_found", folder_path)
                        return
                    except Exception as e:
                        logging.error(f"Error entering email: {e}")
                        await take_screenshot(page, "email_entry_error", folder_path)
                        return

                    # =========================
                    # Step 4A: Click 'Next' Button After Email
                    # =========================
                    logging.info("Clicking 'Next' button after email...")
                    try:
                        await page.wait_for_selector(EMAIL_NEXT_BUTTON_SELECTOR, timeout=15000)
                        await page.click(EMAIL_NEXT_BUTTON_SELECTOR)
                        await page.wait_for_timeout(3000)  # Wait for transition
                        await take_screenshot(page, "after_email_next_click", folder_path)
                    except PlaywrightTimeoutError:
                        logging.error(f"'Next' button '{EMAIL_NEXT_BUTTON_SELECTOR}' not found or not clickable after email.")
                        await take_screenshot(page, "next_button_after_email_not_found", folder_path)
                        return
                    except Exception as e:
                        logging.error(f"Error clicking 'Next' button after email: {e}")
                        await take_screenshot(page, "next_button_after_email_click_error", folder_path)
                        return

                else:
                    logging.info("Email authentication is not required. Proceeding to enter password.")
            except Exception as e:
                logging.error(f"Error determining authentication flow: {e}")
                await take_screenshot(page, "authentication_flow_error", folder_path)
                return

            # =========================
            # Step 5: Enter Password
            # =========================
            logging.info("Entering password...")
            try:
                await page.wait_for_selector(PASSWORD_INPUT_SELECTOR, timeout=15000)
                await page.fill(PASSWORD_INPUT_SELECTOR, X_PASSWORD)
                await take_screenshot(page, "password_entered", folder_path)

                # Optional: Interact with the reveal password button if needed
                # Example:
                # await page.click(PASSWORD_REVEAL_BUTTON_SELECTOR)
                # await take_screenshot(page, "password_revealed", folder_path)

            except PlaywrightTimeoutError:
                logging.error(f"Password input field '{PASSWORD_INPUT_SELECTOR}' not found.")
                await take_screenshot(page, "password_input_not_found", folder_path)
                return
            except Exception as e:
                logging.error(f"Error entering password: {e}")
                await take_screenshot(page, "password_entry_error", folder_path)
                return

            # =========================
            # Step 6: Ensure 'Log in' Button is Enabled
            # =========================
            logging.info("Ensuring 'Log in' button is enabled...")
            try:
                await page.wait_for_selector(LOGIN_BUTTON_SELECTOR, timeout=15000)
                is_enabled = await page.is_enabled(LOGIN_BUTTON_SELECTOR)
                if not is_enabled:
                    logging.error("'Log in' button is disabled. Password may be incorrect or not properly entered.")
                    await take_screenshot(page, "login_button_disabled", folder_path)
                    return
                else:
                    logging.info("'Log in' button is enabled.")
            except PlaywrightTimeoutError:
                logging.error(f"'Log in' button '{LOGIN_BUTTON_SELECTOR}' not found.")
                await take_screenshot(page, "login_button_not_found", folder_path)
                return
            except Exception as e:
                logging.error(f"Error checking 'Log in' button state: {e}")
                await take_screenshot(page, "login_button_state_error", folder_path)
                return

            # =========================
            # Step 7: Click 'Log in' Button
            # =========================
            logging.info("Clicking 'Log in' button...")
            try:
                await page.click(LOGIN_BUTTON_SELECTOR)
                await page.wait_for_load_state("networkidle")
                await take_screenshot(page, "after_login_click", folder_path)
            except PlaywrightTimeoutError:
                logging.error(f"'Log in' button '{LOGIN_BUTTON_SELECTOR}' not found or not clickable.")
                await take_screenshot(page, "login_button_not_clickable", folder_path)
                return
            except Exception as e:
                logging.error(f"Error clicking 'Log in' button: {e}")
                await take_screenshot(page, "login_button_click_error", folder_path)
                return

            # =========================
            # Step 8: Save Cookies After Successful Login
            # =========================
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

            # =========================
            # Step 9: Close Browser
            # =========================
            logging.info("Closing browser...")
            await browser.close()

    except Exception as general_e:
        logging.error(f"An unexpected error occurred: {general_e}")

# =========================
# Entry Point
# =========================

if __name__ == "__main__":
    asyncio.run(login_to_xcom())
