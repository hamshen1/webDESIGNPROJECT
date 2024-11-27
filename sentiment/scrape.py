# scrape.py

import os
import asyncio
import csv
import json
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from config import SELECTORS, COOKIES_PATH, SCREENSHOTS_DIR
from helpers import take_screenshot, create_screenshot_folder

class XComScraper:
    """
    A class to handle scraping topics from x.com's news page.
    It uses saved cookies for authentication to maintain an authenticated session.
    """

    def __init__(self):
        self.selectors = SELECTORS
        self.cookies_path = COOKIES_PATH
        self.screenshots_dir = SCREENSHOTS_DIR
        self.folder_path = None
        self.browser = None
        self.context = None
        self.page = None

    async def setup_browser_with_cookies(self, playwright):
        """
        Initialize the Playwright browser and context, and load cookies for authentication.
        """
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                       " Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        # Load cookies to maintain session
        if os.path.exists(self.cookies_path):
            logging.info("Loading cookies for authenticated session...")
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                # Ensure cookies have the correct domain
                # Optionally, adjust domains here if necessary
                await self.context.add_cookies(cookies)
                logging.info("Cookies loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load cookies: {e}")
                raise
        else:
            logging.error(f"Cookies file '{self.cookies_path}' not found. Please run login.py first.")
            raise FileNotFoundError(f"Cookies file '{self.cookies_path}' not found.")

        self.page = await self.context.new_page()

    async def navigate_to_news_page(self):
        """
        Navigate to the news page and capture a screenshot.
        """
        news_url = "https://x.com/explore/tabs/news"
        logging.info(f"Navigating to news page: {news_url}")
        try:
            await self.page.goto(news_url, wait_until="networkidle")
            await take_screenshot(self.page, "news_page", self.folder_path)
        except Exception as e:
            logging.error(f"Failed to navigate to news page: {e}")
            await take_screenshot(self.page, "news_page_error", self.folder_path)
            raise

    async def verify_authenticated_session(self):
        """
        Verify that the session is authenticated by checking for an authenticated element.
        """
        logging.info("Verifying authenticated session...")
        try:
            # Example selector for an authenticated element
            AUTH_SELECTOR = 'img[alt="User Avatar"]'  # Adjust based on actual site
            if await self.page.query_selector(AUTH_SELECTOR):
                logging.info("Authenticated session confirmed via cookies.")
            else:
                logging.warning("Authenticated session not confirmed. Cookies may be invalid or expired.")
                raise ValueError("Authentication verification failed.")
        except Exception as e:
            logging.error(f"Error during session verification: {e}")
            await take_screenshot(self.page, "authentication_verification_error", self.folder_path)
            raise

    async def scrape_topics(self) -> list:
        """
        Scrape all the topics from the static section and return as a list of dictionaries.
        Each dictionary contains 'Category', 'Topic', and 'Number of Posts'.
        """
        logging.info("Scraping topics from the news page...")
        topics = []
        try:
            # Wait for trend containers to load
            await self.page.wait_for_selector(self.selectors["trend_container"], timeout=15000)

            # Query all trend elements
            trend_elements = await self.page.query_selector_all(self.selectors["trend_container"])

            logging.info(f"Found {len(trend_elements)} trend elements.")

            for idx, trend in enumerate(trend_elements, start=1):
                try:
                    category = await trend.query_selector_eval(
                        self.selectors["trend_category"],
                        "element => element.textContent.trim()"
                    )
                    topic = await trend.query_selector_eval(
                        self.selectors["trend_topic"],
                        "element => element.textContent.trim()"
                    )
                    posts = await trend.query_selector_eval(
                        self.selectors["trend_posts"],
                        "element => element.textContent.trim()"
                    )

                    topics.append({
                        "Category": category,
                        "Topic": topic,
                        "Number of Posts": posts
                    })

                    logging.info(f"Scraped Trend {idx}: Category='{category}', Topic='{topic}', Posts='{posts}'")

                except Exception as e:
                    logging.error(f"Error scraping trend element {idx}: {e}")
                    await take_screenshot(self.page, f"trend_{idx}_error", self.folder_path)
                    continue

            return topics

        except PlaywrightTimeoutError:
            logging.error(f"Trend containers '{self.selectors['trend_container']}' not found.")
            await take_screenshot(self.page, "trend_containers_not_found", self.folder_path)
            raise
        except Exception as e:
            logging.error(f"Error during scraping topics: {e}")
            await take_screenshot(self.page, "scraping_topics_error", self.folder_path)
            raise

    async def save_topics_to_csv(self, topics: list, csv_filename: str = "topics.csv"):
        """
        Save the scraped topics into a CSV file.
        """
        logging.info(f"Saving scraped topics to CSV file: {csv_filename}")
        try:
            with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["Category", "Topic", "Number of Posts"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for topic in topics:
                    writer.writerow(topic)

            logging.info(f"Successfully saved {len(topics)} topics to '{csv_filename}'.")
        except Exception as e:
            logging.error(f"Failed to save topics to CSV: {e}")
            raise

    async def close_browser(self):
        """
        Close the Playwright browser.
        """
        logging.info("Closing browser...")
        await self.browser.close()

    async def perform_scraping(self):
        """
        Execute the complete scraping process.
        """
        try:
            # Initialize screenshot folder
            self.folder_path = create_screenshot_folder(self.screenshots_dir)

            # Start Playwright and setup browser with cookies
            async with async_playwright() as p:
                await self.setup_browser_with_cookies(p)

                # Navigate to news page
                await self.navigate_to_news_page()

                # Verify authenticated session
                await self.verify_authenticated_session()

                # Scrape topics
                topics = await self.scrape_topics()

                # Save topics to CSV
                await self.save_topics_to_csv(topics)

        except Exception as e:
            logging.error(f"Scraping process terminated due to an error: {e}")
        finally:
            # Ensure browser is closed regardless of success or failure
            await self.close_browser()

if __name__ == "__main__":
    scraper = XComScraper()
    asyncio.run(scraper.perform_scraping())
