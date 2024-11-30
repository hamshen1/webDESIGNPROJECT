# config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve login credentials from environment variables
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")
X_EMAIL = os.getenv("X_EMAIL")  # Optional: May not always be required

# Validate that essential credentials are provided
if not X_USERNAME or not X_PASSWORD:
    raise EnvironmentError("Please set X_USERNAME and X_PASSWORD in the .env file.")

# Define selectors based on provided HTML snippets and attributes
SELECTORS = {
    "username_input": 'input[autocomplete="username"]',
    "username_next_button": 'button:has-text("Next")',
    "email_input": 'input[data-testid="ocfEnterTextTextInput"]',
    "email_next_button": 'button[data-testid="ocfEnterTextNextButton"]',
    "password_input": 'input[autocomplete="current-password"]',
    "password_reveal_button": 'button[aria-label="Reveal password"]',  # Optional
    "login_button": 'button[data-testid="LoginForm_Login_Button"]',
    "TREND_CONTAINER": 'div[aria-label="Timeline: Explore"]',
    "TREND_ITEM": 'div[data-testid="trend"][role="link"]',
    "GENRE": 'div[aria-labelledby^="id__"] > div > div > div > span.css-1jxf684',  # Adjusted for genre
    "NAME": 'div[aria-labelledby^="id__"] > div > div > div > div > span.css-1jxf684:nth-child(2)',  # Adjusted for name

}

# Define file paths
COOKIES_PATH = "cookies.json"
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "screenshots")
LOG_FILE = "scraper.log"
TOPICS_CSV = os.path.join(os.getcwd(), "topics.csv")
TRENDING_URL = "https://x.com/explore/tabs/news"
