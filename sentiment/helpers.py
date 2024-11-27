# helpers.py

import os
import json
import logging
from datetime import datetime

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
