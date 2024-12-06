## READ FOR MACOS
      You must create a twitter account if you already don't have one 

      in create a .env file in sentiment
      X_USERNAME=your_username
      X_PASSWORD=your_password
      X_EMAIL=your_email
      ```

      in terminal
      python -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      playwright install

      to run it, go into the sentiment folder in terminal and type: python combined.py to run the combined file
## CUrrent State
      right now, at least for me (Anthony) it used to "work," would log into twitter, but as it tried to reach the trending page, it logged out again.
      But now, when i try to run it says "
      File "/Users/anthonygerencher/webDESIGNPROJECT/sentiment/combined.py", line 6, in <module>
         from login import XComLoginScraper
      File "/Users/anthonygerencher/webDESIGNPROJECT/sentiment/login.py", line 7, in <module>
         from config import SELECTORS, X_USERNAME, X_PASSWORD, X_EMAIL, COOKIES_PATH
      File "/Users/anthonygerencher/webDESIGNPROJECT/sentiment/config.py", line 4, in <module>
         from dotenv import load_dotenv
      ModuleNotFoundError: No module named 'dotenv'

      Good LUCK


## README.md

```markdown
# Sentiment and Scraper

None of this has to do with the website, this is all concentrated on the preperation for article generation. In the sentiment folder

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Logging](#logging)
- [Error Handling](#error-handling)

## Introduction

**Sentiment and Scraper** is an advanced Playwright-based automation tool designed to navigate and extract data from trending topics on [X.com](https://x.com) (formerly Twitter). The scraper performs sentiment analysis on extracted posts, focusing on text and emojis, and stores the results in a structured JSON format. This tool is essential for analysts, marketers, and researchers aiming to gauge public sentiment on various trending topics.

## Features

- **Automated Login**: Securely logs into X.com using provided credentials.
- **Trend Navigation**: Reads and navigates to trend URLs from a CSV file.
- **Data Extraction**: Scrapes text and emojis from posts using stable HTML selectors.
- **Sentiment Analysis**: Utilizes NLTK's VADER for comprehensive sentiment scoring.
- **Error Handling**: Implements robust error handling with detailed logging and screenshot capture.
- **Structured Output**: Saves extracted data and sentiment scores in MongoDB.

## Architecture

The project is modularized into several components to ensure maintainability and scalability:

- **`combined.py`**: Orchestrates the overall workflow, managing login and scraping processes.
- **`login.py`**: Handles the authentication process, accommodating different login flows.
- **`scrape.py`**: Contains the core scraping logic, including data extraction and sentiment analysis.
- **`helpers.py`**: Provides utility functions such as screenshot capture and directory management.
- **`config.py`**: Stores configuration constants and CSS selectors used throughout the project.
- **`requirements.txt`**: Lists all Python dependencies required for the project.

## Installation

### Prerequisites

- **Python 3.12.3**: Ensure Python is installed. Download from [python.org](https://www.python.org/downloads/).
- **Playwright 1.49.0 and dependencies**: Playwright requires browser binaries to function.
- **dotenv 1.0.1** Manages env variables (username, password, email) 
**.env FILE MUST BE IN .gitignore unless you want to commit your password and email**

### Step-by-Step Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/xcom-scraper.git
   cd xcom-scraper
   ```

2. **Create a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**

   - **Unix/Linux/MacOS**

     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Install Playwright Browsers**

   ```bash
   playwright install
   ```

## Configuration

### Environment Variables

Sensitive information such as login credentials should be managed securely using environment variables. Create a `.env` file in the project's root directory and add the following:

You must create a twitter account if you already don't have one 

```env
X_USERNAME=your_username
X_PASSWORD=your_password
X_EMAIL=your_email
```

**Important**: Ensure that the `.env` file is added to `.gitignore` to prevent sensitive data from being committed to version control.

### `config.py`

This file contains all necessary CSS selectors and configuration constants.

### `topics.csv`

Populate this CSV with the trend data you wish to scrape. Ensure it follows the structure below:

```csv
trend_index,genre,name,search_url
1,Business and finance,Arrest Bill Gates,https://x.com/search?q=%22Arrest+Bill+Gates%22
2,Business and finance,#XRPHolders,https://x.com/search?q=%22%23XRPHolders%22
3,Business and finance,$XRP,https://x.com/search?q=%22%24XRP%22
...
```

**Columns Explained**:

- **trend_index**: A unique identifier for each trend.
- **genre**: The category or genre of the trend.
- **name**: The name or label of the trend.
- **search_url**: The URL to navigate and scrape the trend data.

## Usage

### Running the Scraper

Ensure that your virtual environment is activated and all dependencies are installed.

```bash
python combined.py
```

### Workflow Overview

1. **Login Process**:  
   The scraper logs into X.com using the credentials provided via environment variables.

2. **Scraping Process**:  
   It reads trend URLs from `topics.csv`, navigates to each URL, extracts post data (text and emojis), performs sentiment analysis, and saves the results.

3. **Output Generation**:  
   The extracted data, along with sentiment scores, are saved in JSON files corresponding to each trend.

## Logging

Also in the helpers.py there are methods to take screenshots that are used throughout the process. This is because I run this headless meaning it doesn't have a visual browser that you can see. Headless mode is reccomended
The scraper employs Python's built-in `logging` module to record detailed logs of its operations. The log levels used are:

- **INFO**: General information about the scraper's progress.
- **WARNING**: Non-critical issues that do not halt the scraping process.
- **ERROR**: Critical issues that may require immediate attention.

All logs are saved in the `scraper.log` file and are also output to the console for real-time monitoring.

## Error Handling

Robust error handling mechanisms are integrated to ensure the scraper's resilience:

- **Timeouts**: The scraper waits for elements to load within specified timeframes. If elements do not appear, it logs an error and captures a screenshot for further analysis.
- **Missing Elements**: If expected elements (e.g., login fields, posts) are not found, the scraper logs warnings and continues with other tasks.
- **Exception Capture**: All exceptions are caught, logged, and associated screenshots are taken to aid in debugging.
- **Graceful Termination**: In the event of critical failures, the scraper logs the issue and terminates gracefully without leaving hanging processes.

---
```
