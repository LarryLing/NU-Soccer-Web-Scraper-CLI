import argparse
import base64
import datetime as dt
import os
from datetime import datetime

import requests
from bs4 import Tag
from selenium import webdriver
from selenium.common import InvalidArgumentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.print_page_options import PrintOptions
from webdriver_manager.chrome import ChromeDriverManager

BOLD = '\033[1m'
NORMAL = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'


def validate_box_scores_argument(box_scores: int) -> int:
    """
    Performs validation of the box scores argument by checking if the argument is greater than 1

    Args:
        box_scores: The box score value to validate.

    Returns:
        int
    """
    if box_scores < 1:
        raise argparse.ArgumentTypeError("expected an integer greater than 1")
    return box_scores


def format_date(date_string: str) -> dt.date | None:
    """
    Attempts to format the date string with the MM/DD/YYYY format.

    Args:
        date_string: The date string to format.

    Returns:
        dt.date
    """
    try:
        formatted_date = datetime.strptime(date_string, "%m/%d/%Y").date()
        return formatted_date
    except ValueError:
        return None


def validate_articles_argument(dates: list[str]) -> list[dt.date]:
    """
    Performs validation of the articles argument by checking if the dates are of valid format and a correct number of dates were entered.

    Args:
        dates: The dates to validate.

    Returns:
        list[dt.date]
    """
    if len(dates) not in [1, 2]:
        raise argparse.ArgumentTypeError("expected one or two dates")

    formatted_dates = []
    for date in dates:
        formatted_date = format_date(date)
        if formatted_date is None:
            raise argparse.ArgumentTypeError("expected a date formatted as MM/DD/YYYY")

        formatted_dates.append(formatted_date)

    if len(formatted_dates) == 1:
        formatted_dates.append(datetime.now().date())

    return sorted(formatted_dates)


def initialize_web_driver() -> webdriver.Chrome:
    """
    Initializes a new web driver instance with robust configuration.

    Returns:
        A new web driver instance.
    """

    service = Service(
        ChromeDriverManager().install(),
        service_args=['--verbose'],
        connect_timeout=30
    )

    chrome_options = Options()

    # Essential headless arguments
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # Stability improvements
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--log-level=3")

    # Memory management
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")

    # Experimental stability flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    try:
        driver = webdriver.Chrome(
            service=service,
            options=chrome_options,
        )

        # Additional stability configurations
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(20)
        driver.implicitly_wait(10)

        return driver

    except Exception as e:
        service.stop()  # Clean up service if initialization fails
        raise RuntimeError(f"Failed to initialize WebDriver: {str(e)}")


def sanitize_html(doc: Tag | None) -> str:
    """
    Removes any embedded tweets and advertisement content from HTML string.

    Args:
        doc: BeautifulSoup Tag with the unsanitized HTML.

    Returns:
        The sanitized HTML table as a string.
    """
    if not doc:
        return ""

    for table_row in doc.find_all("tr"):
        if ("class" in table_row.attrs) and ("s-table-body__row--ad" in table_row["class"]):
            table_row.extract()

    return str(doc)


def download_pdf_to_cwd(driver: webdriver.Chrome, filename: str) -> None:
    """
    Performs Selenium's print function and saves the PDF bytes to the zip file.

    Args:
        driver: Selenium webdriver instance.
        filename: The filename of the PDF file.

    Returns:
        None
    """
    try:
        print_options = PrintOptions()
        pdf = driver.print_page(print_options)
        pdf_bytes = base64.b64decode(pdf)

        output_file = os.getcwd() + "/" + filename
        with open(output_file, 'wb') as file:
            file.write(pdf_bytes)

        print_success_message(filename)
    except InvalidArgumentException as e:
        print_failure_message(filename, e.msg)


def response_pdf_to_cwd(pdf_url: str, filename: str) -> None:
    """
    Sends an HTTP GET request for PDF bytes and writes them to a zip file.

    Args:
        pdf_url: The URL of the PDF file.
        filename: The filename of the PDF file.

    Returns:
        None
    """
    response = requests.get(pdf_url)
    if response.status_code == 404:
        print_failure_message(filename, "Found a PDF URL, but it doesn't link to an existing file")
        return

    output_file = os.getcwd() + "/" + filename
    with open(output_file, "wb") as file:
        file.write(response.content)

    print_success_message(filename)


def prompt_user_for_articles(max_index: int) -> list[int]:
    """
    Asks the user to enter the indexes of the articles they want to download. A list of indexes is returned.

    Args:
        max_index: The index of last fetched article, used to determine the range of available indexes.

    Returns:
        list[int]
    """
    article_indexes = []

    indexes = input("Enter the index of articles to download (e.g., 0 1 2): ").strip().split(" ")
    for index in indexes:
        if not index.isdigit():
            continue

        if int(index) > max_index:
            continue

        if int(index) < 0:
            continue

        article_indexes.append(int(index))

    return article_indexes


def print_failure_message(filename: str, reason: str) -> None:
    """
    Prints a message to the console, indicating a failed download.

    Args:
        filename: The filename of the PDF file.
        reason: The reason why the download failed.

    Returns:
        None
    """
    print(f"{BOLD}{RED}[ERROR]{NORMAL} Failed to download \"{filename}\" ({reason})")


def print_success_message(filename: str):
    """
    Prints a message to the console, indicating a successful download.

    Args:
        filename: The filename of the PDF file.

    Returns:
        None
    """
    print(f"{BOLD}{GREEN}[SUCCESS]{NORMAL} Downloaded \"{filename}\" to {os.getcwd()}")
