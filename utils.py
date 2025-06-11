import base64
import os

import requests
from bs4 import Tag
from selenium import webdriver
from selenium.common import InvalidArgumentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.print_page_options import PrintOptions
from webdriver_manager.chrome import ChromeDriverManager

from ansi import BOLD, NORMAL, GREEN, RED

def initialize_web_driver() -> webdriver.Chrome:
    """
    Initializes a new web driver instance with robust configuration.

    Returns:
        A new web driver instance.
    """

    service = Service(
        ChromeDriverManager().install(),
        service_args=['--verbose'],  # Enable verbose logging
        connect_timeout=30  # Increase connection timeout
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

        print(f"Downloading {filename}... {BOLD}{GREEN}SUCCESS{NORMAL}")
    except InvalidArgumentException as e:
        print(f"Downloading {filename}... {BOLD}{RED}FAILED{NORMAL}\nReason: {e.msg}")


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
        print(f"Downloading {filename}... {BOLD}{RED}FAILED{NORMAL}\nReason: Found a PDF URL, but it doesn't link to an existing file.")
        return

    output_file = os.getcwd() + "/" + filename
    with open(output_file, "wb") as file:
        file.write(response.content)

    print(f"Downloading {filename}... {BOLD}{GREEN}SUCCESS{NORMAL}")

