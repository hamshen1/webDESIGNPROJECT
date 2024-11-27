# login.py

import os
import asyncio
import json
import logging
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from config import SELECTORS, X_USERNAME, X_PASSWORD, X_EMAIL, COOKIES_PATH, SCREENSHOTS_DIR
from helpers import take_screenshot, create_screenshot_folder

class XComLoginScraper:
    """
    A class to handle the login process to x.com using Playwright.
    It accommodates different authentication scenarios based on the presence of email verification.
    """

    def __init__(self, page):
        self.page = page
        self.context = self.page.context
        self.browser = self.context.browser
        self.selectors = SELECTORS
        self.cookies_path = COOKIES_PATH
        self.screenshots_dir = SCREENSHOTS_DIR
        self.folder_path = None

    async def navigate_to_login_page(self):
        """
        Navigate to the login page and capture a screenshot.
        """
        logging.info("Navigating to login page...")
        try:
            await self.page.goto("https://x.com/i/flow/login", wait_until="networkidle")
            await take_screenshot(self.page, "login_page", self.folder_path)
        except Exception as e:
            logging.error(f"Failed to navigate to login page: {e}")
            await take_screenshot(self.page, "login_page_error", self.folder_path)
            raise

    async def enter_username(self):
        """
        Enter the username into the username input field.
        """
        logging.info("Entering username...")
        try:
            await self.page.wait_for_selector(self.selectors["username_input"], timeout=15000)
            await self.page.fill(self.selectors["username_input"], X_USERNAME)
            await take_screenshot(self.page, "username_entered", self.folder_path)

            # Verify username entry
            entered_username = await self.page.input_value(self.selectors["username_input"])
            if entered_username != X_USERNAME:
                logging.error("Username was not entered correctly.")
                await take_screenshot(self.page, "username_verification_failed", self.folder_path)
                raise ValueError("Username verification failed.")
        except PlaywrightTimeoutError:
            logging.error(f"Username input field '{self.selectors['username_input']}' not found.")
            await take_screenshot(self.page, "username_input_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error entering username: {e}")
            await take_screenshot(self.page, "username_entry_error", self.folder_path)
            raise

    async def click_next_after_username(self):
        """
        Click the 'Next' button after entering the username.
        """
        logging.info("Clicking 'Next' button after username...")
        try:
            await self.page.wait_for_selector(self.selectors["username_next_button"], timeout=15000)
            await self.page.click(self.selectors["username_next_button"])
            await self.page.wait_for_timeout(3000)  # Wait for transition
            await take_screenshot(self.page, "after_username_next_click", self.folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"'Next' button '{self.selectors['username_next_button']}' not found or not clickable after username.")
            await take_screenshot(self.page, "next_button_after_username_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error clicking 'Next' button after username: {e}")
            await take_screenshot(self.page, "next_button_after_username_click_error", self.folder_path)
            raise

    async def is_email_authentication_required(self) -> bool:
        """
        Determine whether email authentication is required by checking the presence of the email input field.
        Returns True if email authentication is required, False otherwise.
        """
        logging.info("Determining if email authentication is required...")
        try:
            email_input = await self.page.query_selector(self.selectors["email_input"])
            if email_input:
                logging.info("Email authentication is required.")
                return True
            else:
                logging.info("Email authentication is not required.")
                return False
        except Exception as e:
            logging.error(f"Error determining authentication flow: {e}")
            await take_screenshot(self.page, "authentication_flow_error", self.folder_path)
            raise

    async def enter_email(self):
        """
        Enter the email into the email input field.
        """
        logging.info("Entering email...")
        if not X_EMAIL:
            logging.error("Email authentication is required, but no email provided.")
            raise ValueError("Email is required for authentication but not provided.")

        try:
            await self.page.wait_for_selector(self.selectors["email_input"], timeout=15000)
            await self.page.fill(self.selectors["email_input"], X_EMAIL)
            await take_screenshot(self.page, "email_entered", self.folder_path)

            # Verify email entry
            entered_email = await self.page.input_value(self.selectors["email_input"])
            if entered_email != X_EMAIL:
                logging.error("Email was not entered correctly.")
                await take_screenshot(self.page, "email_verification_failed", self.folder_path)
                raise ValueError("Email verification failed.")
        except PlaywrightTimeoutError:
            logging.error(f"Email input field '{self.selectors['email_input']}' not found.")
            await take_screenshot(self.page, "email_input_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error entering email: {e}")
            await take_screenshot(self.page, "email_entry_error", self.folder_path)
            raise

    async def click_next_after_email(self):
        """
        Click the 'Next' button after entering the email.
        """
        logging.info("Clicking 'Next' button after email...")
        try:
            await self.page.wait_for_selector(self.selectors["email_next_button"], timeout=15000)
            await self.page.click(self.selectors["email_next_button"])
            await self.page.wait_for_timeout(3000)  # Wait for transition
            await take_screenshot(self.page, "after_email_next_click", self.folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"'Next' button '{self.selectors['email_next_button']}' not found or not clickable after email.")
            await take_screenshot(self.page, "next_button_after_email_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error clicking 'Next' button after email: {e}")
            await take_screenshot(self.page, "next_button_after_email_click_error", self.folder_path)
            raise

    async def enter_password(self):
        """
        Enter the password into the password input field.
        """
        logging.info("Entering password...")
        try:
            await self.page.wait_for_selector(self.selectors["password_input"], timeout=15000)
            await self.page.fill(self.selectors["password_input"], X_PASSWORD)
            await take_screenshot(self.page, "password_entered", self.folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"Password input field '{self.selectors['password_input']}' not found.")
            await take_screenshot(self.page, "password_input_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error entering password: {e}")
            await take_screenshot(self.page, "password_entry_error", self.folder_path)
            raise

    async def ensure_login_button_enabled(self):
        """
        Ensure that the 'Log in' button is enabled before attempting to click it.
        """
        logging.info("Ensuring 'Log in' button is enabled...")
        try:
            await self.page.wait_for_selector(self.selectors["login_button"], timeout=15000)
            is_enabled = await self.page.is_enabled(self.selectors["login_button"])
            if not is_enabled:
                logging.error("'Log in' button is disabled. Password may be incorrect or not properly entered.")
                await take_screenshot(self.page, "login_button_disabled", self.folder_path)
                raise ValueError("'Log in' button is disabled.")
            else:
                logging.info("'Log in' button is enabled.")
        except PlaywrightTimeoutError:
            logging.error(f"'Log in' button '{self.selectors['login_button']}' not found.")
            await take_screenshot(self.page, "login_button_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error checking 'Log in' button state: {e}")
            await take_screenshot(self.page, "login_button_state_error", self.folder_path)
            raise

    async def click_login_button(self):
        """
        Click the 'Log in' button to attempt authentication.
        """
        logging.info("Clicking 'Log in' button...")
        try:
            await self.page.click(self.selectors["login_button"])
            await self.page.wait_for_load_state("networkidle")
            await take_screenshot(self.page, "after_login_click", self.folder_path)
        except PlaywrightTimeoutError:
            logging.error(f"'Log in' button '{self.selectors['login_button']}' not found or not clickable.")
            await take_screenshot(self.page, "login_button_not_clickable", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error clicking 'Log in' button: {e}")
            await take_screenshot(self.page, "login_button_click_error", self.folder_path)
            raise

    async def save_cookies(self):
        """
        Save cookies after successful login to maintain session in future runs.
        """
        logging.info("Saving cookies after successful login...")
        try:
            cookies = await self.context.cookies()
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
            with open(self.cookies_path, "w") as f:
                json.dump(cookies_serializable, f, indent=4)
            logging.info("Login successful. Cookies saved.")
            await take_screenshot(self.page, "logged_in_successfully", self.folder_path)
        except Exception as e:
            logging.error(f"Failed to save cookies: {e}")
            await take_screenshot(self.page, "save_cookies_error", self.folder_path)
            raise

    async def perform_login(self):
        """
        Execute the complete login process, handling different authentication flows.
        """
        try:
            # Initialize screenshot folder
            self.folder_path = create_screenshot_folder(self.screenshots_dir)

            # Navigate to login page
            await self.navigate_to_login_page()

            # Enter username and proceed
            await self.enter_username()
            await self.click_next_after_username()

            # Determine if email authentication is required
            email_auth_required = await self.is_email_authentication_required()

            if email_auth_required:
                await self.enter_email()
                await self.click_next_after_email()

            # Enter password
            await self.enter_password()

            # Ensure 'Log in' button is enabled
            await self.ensure_login_button_enabled()

            # Click 'Log in' button
            await self.click_login_button()

            # Save cookies post-login
            await self.save_cookies()

        except Exception as e:
            logging.error(f"Login process terminated due to an error: {e}")
