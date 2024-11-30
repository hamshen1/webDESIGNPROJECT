# scrape.py

import asyncio
import logging
import csv
from playwright.async_api import Page, TimeoutError, Error
from config import TRENDING_URL, TOPICS_CSV, SELECTORS
from helpers import take_screenshot

class XComScraper:
    def __init__(self, page: Page):
        self.page = page
        self.folder_path = None  # To be set externally
        self.topics = []

    async def navigate_to_trending(self):
        try:
            logging.info(f"Navigating to trending page: {TRENDING_URL}")
            await self.page.goto(TRENDING_URL, timeout=60000)
            await self.page.wait_for_load_state('networkidle', timeout=60000)
            await take_screenshot(self.page, "trending_page_loaded", self.folder_path)
            logging.info("Successfully navigated to the trending page")
        except TimeoutError:
            logging.error("Timeout while navigating to the trending page")
            await take_screenshot(self.page, "navigate_timeout", self.folder_path)
            raise
        except Error as e:
            logging.error(f"Unexpected error during navigation: {e}")
            await take_screenshot(self.page, "navigate_error", self.folder_path)
            raise

    async def extract_topics(self):
        try:
            logging.info("Waiting for the trend container to be visible")
            await self.page.wait_for_selector(SELECTORS["TREND_CONTAINER"], timeout=30000)
            logging.info("Trend container is visible")

            trend_elements = await self.page.query_selector_all(SELECTORS["TREND_ITEM"])
            logging.info(f"Found {len(trend_elements)} trend items")

            for idx, element in enumerate(trend_elements, start=1):
                try:
                    # Extract all span elements within the trend item
                    spans = await element.query_selector_all('span')
                    genre = None
                    name = None

                    for span in spans:
                        text = await span.inner_text()
                        if 'Trending in' in text:
                            genre = text.replace('Trending in', '').strip()
                        elif 'posts' in text:
                            continue  # We can ignore the posts count
                        else:
                            name = text.strip()

                    if genre is None or name is None:
                        logging.warning(f"Could not find genre or name for trend item {idx}")
                        await take_screenshot(self.page, f"trend_item_{idx}_missing_data", self.folder_path)
                        continue

                    # Construct search URL
                    search_query = name.replace(" ", "+")
                    search_url = f'https://x.com/search?q=%22{search_query}%22'

                    # Create topic dictionary
                    topic = {
                        "name": name,
                        "genre": genre,
                        "search_url": search_url
                    }
                    self.topics.append(topic)
                    logging.debug(f"Extracted topic {idx}: {topic}")

                    # Optionally, take a screenshot after extracting each topic
                    await take_screenshot(self.page, f"extract_topic_{idx}", self.folder_path)
                except Exception as e:
                    logging.warning(f"Failed to extract trend item {idx}: {e}")
                    await take_screenshot(self.page, f"extract_topic_{idx}_error", self.folder_path)
        except TimeoutError:
            logging.error("Timeout while waiting for the trend container")
            await take_screenshot(self.page, "trend_container_timeout", self.folder_path)
            raise
        except Error as e:
            logging.error(f"Unexpected error during extraction: {e}")
            await take_screenshot(self.page, "extraction_error", self.folder_path)
            raise

    def save_to_csv(self):
        if not self.topics:
            logging.warning("No topics extracted to save")
            return
        try:
            logging.info(f"Saving {len(self.topics)} topics to {TOPICS_CSV}")
            with open(TOPICS_CSV, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["name", "genre", "search_url"])
                writer.writeheader()
                writer.writerows(self.topics)
            logging.info("Data saved successfully to CSV")
        except Exception as e:
            logging.error(f"Failed to save data to CSV: {e}")
            raise

    async def perform_scraping(self):
        try:
            await self.navigate_to_trending()
            await self.extract_topics()
            self.save_to_csv()
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
            raise
