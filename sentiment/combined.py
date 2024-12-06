# combined.py

import asyncio
import logging
from playwright.async_api import async_playwright
from login import XComLoginScraper
from scrape import XComScraper
from helpers import create_screenshot_folder
from config import SCREENSHOTS_DIR

async def main():
    # Initialize logging
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG for detailed logs
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("scraper.log"),
            logging.StreamHandler()
        ]
    )

    # Initialize screenshot folder
    folder_path = create_screenshot_folder(SCREENSHOTS_DIR)

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Perform login
            login_scraper = XComLoginScraper(page)
            login_scraper.folder_path = folder_path  # Set the folder path for screenshots
            await login_scraper.perform_login()

            # Perform scraping
            scraper = XComScraper(page)
            scraper.folder_path = folder_path  # Set the folder path for screenshots
            await scraper.perform_scraping()
        except Exception as e:
            logging.error(f"An error occurred in the main process: {e}")
        finally:
            # Close browser
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
