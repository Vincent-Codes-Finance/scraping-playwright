import logging
import time
from pathlib import Path

import pandas as pd

import requests
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import (
    TimeoutError,
    sync_playwright,
)

url = "https://www.nasdaq.com/market-activity/quotes/nasdaq-ndx-index"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:127.0) Gecko/20100101 Firefox/127.0"


def scrape_url_pw(
    url: str,
    output_path: Path,
    wait_for_load: int = 2000,
    screenshot_path: Path | None = None,
) -> None:
    """Scrape the content of a URL using playwright."""
    try:
        with sync_playwright() as p:
            # This browser, context, and page can be reused for multiple URLs
            browser = p.firefox.launch()
            context = browser.new_context(user_agent=USER_AGENT)
            page = context.new_page()

            page.goto(url, timeout=5000)

            if wait_for_load > 0:
                page.wait_for_timeout(wait_for_load)
            if screenshot_path is not None:
                page.screenshot(path=screenshot_path, full_page=True)

            with open(output_path, "w", encoding="utf-8") as file:
                file.write(page.content())
    except (PlaywrightError, TimeoutError) as e:
        logging.error(f"Error scraping {url}: {e}")


def scrape_url_req(url: str, output_path: Path) -> None:
    """Scrape the content of a URL using requests."""
    response = requests.get(url, headers={"User-Agent": USER_AGENT})
    if response.status_code != 200:
        logging.error(f"Error {response.status_code}")
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(response.text)


output_req_path = Path("requests.html")
output_pw_path = Path("playwright.html")
screenshot_path = Path("screenshot.png")

logging.basicConfig(level=logging.INFO)
logging.info(f"Scraping {url} using requests")

scrape_url_req(url, output_req_path)

time.sleep(2)
logging.info(f"Scraping {url} using playwright, wait for load")

scrape_url_pw(url, output_pw_path, screenshot_path=screenshot_path)

csv_path = Path("table.csv")

df = pd.read_html(output_pw_path)[0]
df.to_csv(csv_path, index=False)
