import time
from io import StringIO
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium.common import WebDriverException

from utils import initialize_web_driver, sanitize_html, download_pdf_to_cwd, print_failure_message


def download_schedule(team_name: str, url: str, filename: str) -> None:
    """
    Downloads the schedule page to a PDF file.

    Args:
        team_name: Name of the team.
        url: URL of the site.
        filename: Name of the downloaded file.

    Returns:
        None
    """
    driver = initialize_web_driver()

    script = """
        let removed = document.getElementById('divSatisfiChat'); 
        if (removed) removed.parentNode.removeChild(removed);

        removed = document.getElementById('transcend-consent-manager'); 
        if (removed) removed.parentNode.removeChild(removed);

        removed = document.getElementById('termly-code-snippet-support'); 
        if (removed) removed.parentNode.removeChild(removed);
    """

    try:
        driver.get(url)
        time.sleep(1)

        driver.execute_script(script)

        scrape_schedule = [
            "Northwestern",
            "Indiana",
            "Ohio State",
            "UCLA",
            "Michigan State",
            "Michigan",
            "DePaul"
        ]

        if team_name in scrape_schedule:
            soup = BeautifulSoup(driver.page_source, "lxml")

            extracted_tables = extract_tables(soup)

            if not extracted_tables:
                raise ValueError(f"Website encountered an internal server error")

            full_html = build_html_document(soup.find("title").text, extracted_tables)

            script_dir = Path(__file__).parent.absolute()

            with open(script_dir / "temp.html", "w") as f:
                f.write(full_html)

            driver.get(f"file:///{str(script_dir / "temp.html")}")

        download_pdf_to_cwd(driver, filename)
    except ValueError as e:
        print_failure_message(filename, e.args[0])
    except WebDriverException as e:
        print_failure_message(filename, e.msg)
    finally:
        driver.quit()


def extract_tables(soup: BeautifulSoup) -> list[str] | None:
    """
    Extracts and processes tables from the HTML document.

    Args:
        soup: Parsed HTML document.

    Returns:
        List of HTML strings containing tables. Returns a None if no tables were found.
    """
    try:
        sanitized_html = sanitize_html(soup)
        dataframes = pd.read_html(StringIO(sanitized_html))
        for dataframe in dataframes:
            dataframe.fillna("", inplace=True)

        return [dataframe.to_html(index=False) for dataframe in dataframes]
    except ValueError:
        return None


def build_html_document(title: str, html_tables: list[str]) -> str:
    """
    Initializes a blank HTML page and inserts HTML table content.

    Args:
        title: Title for the HTML document.
        html_tables: List of HTML strings containing tables to insert.

    Returns:
        A string representation of the full .HTML document.
    """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            table {{ width: 100%; border-collapse: collapse; }}
            thead {{ display: table-row-group; }}
            th, td {{ font-size: 12px; border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <main>
            <h1>{title}</h1>
        </main>
    </body>
    </html>
    """
    document = BeautifulSoup(html, "lxml")

    main = document.find("main")

    for html_table in html_tables:
        div_tag = document.new_tag("div")
        main.append(div_tag)

        table = BeautifulSoup(html_table, "lxml")
        main.append(table)

    return str(document)
