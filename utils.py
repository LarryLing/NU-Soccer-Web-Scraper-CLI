from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import ChromiumOptions
from bs4 import BeautifulSoup, Tag
import asyncio
import time

def prompt(teams: dict[str, dict[str, any]]) -> str:
    """
    Prompts the user for a team name returns it.

    Args:
        teams (dict[str, dict[str, any]]): Dictionary containing settings.

    Returns:
        team_name (str): The name of the team.
    """
    try:
        print()
        print("Enter A Team:")

        for team in teams.keys():
            print(f"   {team}")

        print("   Exit")

        team_name = input()
        return team_name

    except Exception as e:
        print("ERROR")
        print("ERROR: invalid input")
        print("ERROR")
        return -1

def initialize_web_driver(web_driver_settings: dict[str, any]) -> webdriver.Chrome:
    """
    Initializes a new web driver instance.

    Args:
        web_driver_settings (dict[str, Any]): Dictionary containing web driver settings.

    Returns:
        driver (WebDriver): A new web driver instance.
    """
    service = Service(executable_path=web_driver_settings["executable_path"])

    chrome_options = ChromiumOptions()

    for arg in web_driver_settings["arguments"]:
        chrome_options.add_argument(arg)

    return webdriver.Chrome(service=service, options=chrome_options)

def create_html_tables(title: str, tables: list[tuple[str, list[str], list[list[str]]]]) -> str:
    """
    Initialize a HTML table.

    Args:
        title (str): Title for the HTML document.
        tables (list[tuple[str, list[str], list[list[str]]]]): List of processed tables repesented as a tuple of the form (caption, columns, rows) where:
            caption (str): The caption of the table.
            columns (list[str]): List of column names.
            rows (list[list[str]]): List of rows, each row is a list of cell values.

    Returns:
        str: A string representation of the HTML document.
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

    doc = BeautifulSoup(html, "html.parser")

    main = doc.find("main")

    for table in tables:
        div_tag = doc.new_tag("div")
        main.append(div_tag)

        if (table[0]):
            h3_tag = doc.new_tag("h3", string=table[0])
            div_tag.append(h3_tag)

        table_tag = doc.new_tag("table")
        div_tag.append(table_tag)

        thead_tag = doc.new_tag("thead")

        for column in table[1]:
            th = doc.new_tag("th", string=column)
            thead_tag.append(th)

        table_tag.append(thead_tag)

        tbody_tag = doc.new_tag("tbody")

        for row in table[2]:
            tr = doc.new_tag("tr")
            for cell in row:
                td = doc.new_tag("td", string=cell)
                tr.append(td)
            tbody_tag.append(tr)

        table_tag.append(tbody_tag)

    return doc.prettify()

async def process_tables(driver: webdriver.Chrome, url: str, ignore_columns: list[str]) -> list[tuple[str, list[str], list[list[str]]]]:
    """
    Process every table on the page.

    Args:
        driver (WebDriver): The web driver instance.
        url (str): The URL of the page to scrape.
        ignore_columns (list[str]): List of table columns to ignore.

    Returns:
        processed_tables (list[tuple[str, list[str], list[list[str]]]]): List of processed tables repesented as a tuple of the form (caption, columns, rows) where:
            caption (str): The caption of the table.
            columns (list[str]): List of column names.
            rows (list[list[str]]): List of rows, each row is a list of cell values.
    """
    driver.get(url)

    await asyncio.sleep(1)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    tables = doc.find_all("table")

    proccessed_tables = []
    for table in tables:
        processed_table = process_table(table, ignore_columns)
        if (processed_table is not None):
            proccessed_tables.append(processed_table)

    return proccessed_tables

def process_table(table: Tag, ignore_columns: list[str]) -> tuple[str, list[str], list[list[str]]] | None:
    """
    Process a single table on the page.

    Args:
        table (Tag): The table element to process.
        ignore_columns (list[str]): List of table columns to ignore.

    Returns:
        processed_table (tuple[str, list[str], list[list[str]]]): A processed tabled repesented as a tuple of the form (caption, columns, rows) where:
            caption (str): The caption of the table.
            columns (list[str]): List of column names.
            rows (list[list[str]]): List of rows, each row is a list of cell values.
        If the table is empty or has no rows, return None.
    """
    processed_caption = None

    caption = table.find("caption")
    if (caption): processed_caption = caption.text

    thead = table.find("thead")
    if (thead is None): return None

    ignore_column_indexes = []
    processed_columns = []

    for index, th in enumerate(thead.find_all("th")):
        if (th.text in ignore_columns):
            ignore_column_indexes.append(index)
            continue

        processed_columns.append(th.text)

    processed_rows = []

    tbody = table.find("tbody")
    if (tbody is None): return None

    for child in tbody.children:
        if (child.name != "tr"): continue

        row = [cell.text for index, cell in enumerate(child.find_all("td")) if (cell.text != "Skip Ad") and (index not in ignore_column_indexes)]

        processed_rows.append(row)

    return processed_caption, processed_columns, processed_rows

def get_boost_box_score_pdf_urls(doc: BeautifulSoup, box_score_settings: dict[str, any]) -> list[str]:
    """
    Get the URLs of the box scores from the conference websites provided by Boost.

    Args:
        doc (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        box_score_settings (dict[str, any]): Dictionary containing box score settings.

    Returns:
        list[str]: List of box score PDF URLs.
    """
    schedule_table = doc.find("table")

    box_score_pdf_urls = [a["href"] for a in schedule_table.find_all("a", string="Box Score")]

    return box_score_pdf_urls[(-1 * box_score_settings["count"]):]

def get_sidearm_box_score_pdf_urls(driver: webdriver.Chrome, team_data: dict[str, str], doc: BeautifulSoup, box_score_settings: dict[str, any]) -> list[str]:
    """
    Get the URLs of the box scores from the conference websites provided by Sidearm.

    Args:
        driver (WebDriver): The web driver instance.
        team_data (dict[str, str]): Dictionary containing team data.
        doc (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        box_score_settings (dict[str, any]): Dictionary containing box score settings.

    Returns:
        list[str]: List of box score PDF URLs.
    """
    matches = []

    matchday_tables = doc.find_all("table")

    for matchday_table in matchday_tables:
        matchday_table_body = matchday_table.find("tbody")

        for tr in matchday_table_body.find_all("tr"):
            away_team_td = tr.select_one('td[class*="sidearm-team-away"]')
            home_team_td = tr.select_one('td[class*="sidearm-team-home"]')

            away_team = away_team_td.find("span", class_="sidearm-calendar-list-group-list-game-team-title").find(['a', 'span']).text
            home_team = home_team_td.find("span", class_="sidearm-calendar-list-group-list-game-team-title").find(['a', 'span']).text
            if (away_team != team_data["name"] and home_team != team_data["name"]): continue

            box_score_href = team_data["conference_base_url"] + tr.find("a", string="Box Score")["href"]

            matches.append([home_team, away_team, box_score_href])

    box_score_pdf_urls = []

    for match in matches[(-1 * box_score_settings["count"]):]:
        driver.get(match[2])
        time.sleep(1)
        doc = BeautifulSoup(driver.page_source, "html.parser")

        box_score_preview_url = team_data["conference_base_url"] + doc.find("div", id="print-bar").find("a")["href"]

        driver.get(box_score_preview_url)
        time.sleep(1)
        doc = BeautifulSoup(driver.page_source, "html.parser")
        box_score_pdf_url = doc.find("a", string="Open")["href"]

        box_score_pdf_urls.append((match[0], match[1], box_score_pdf_url))

    return box_score_pdf_urls
