from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import ChromiumOptions
from bs4 import BeautifulSoup
import asyncio

def prompt():
    """
    Prompts the user for a team name returns it.
    """

    try:
        print()
        print("Enter A Team:")
        print("   Northwestern")
        print("   Indiana")
        print("   Ohio State")
        print("   Maryland")
        print("   Washington")
        print("   UCLA")
        print("   Michigan State")
        print("   Michigan")
        print("   Rutgers")
        print("   Wisconsin")
        print("   Penn State (not available)")
        print("   UIC")
        print("   Loyola")
        print("   DePaul")
        print("   Exit")

        team_name = input()
        return team_name

    except Exception as e:
        print("ERROR")
        print("ERROR: invalid input")
        print("ERROR")
        return -1

def initialize_web_driver(settings):
    service = Service(executable_path=settings["paths"]["chromedriver"])

    chrome_options = ChromiumOptions()

    for arg in settings["web_driver"]["arguments"]:
        chrome_options.add_argument(arg)

    return webdriver.Chrome(service=service, options=chrome_options)

def create_html_tables(title, tables):
    """
    Initialize a HTML table.
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

        # Insert the table caption
        if (table["caption"]):
            h3_tag = doc.new_tag("h3", string=table["caption"])
            div_tag.append(h3_tag)

        # Insert the table
        table_tag = doc.new_tag("table")
        div_tag.append(table_tag)

        # Insert the table header
        thead_tag = doc.new_tag("thead")

        for column in table["columns"]:
            th = doc.new_tag("th", string=column)
            thead_tag.append(th)

        table_tag.append(thead_tag)

        # Insert the table body
        tbody_tag = doc.new_tag("tbody")

        for row in table["rows"]:
            tr = doc.new_tag("tr")
            for cell in row:
                td = doc.new_tag("td", string=cell)
                tr.append(td)
            tbody_tag.append(tr)

        table_tag.append(tbody_tag)

    return doc.prettify()

async def process_tables(driver, url, ignore_columns):
    """
    Process the tables from the pages.
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

def process_table(table, ignore_columns):
    """
    Process the table from the page.
    """

    # Get the table caption
    processed_caption = None

    caption = table.find("caption")
    if (caption): processed_caption = caption.text

    # Get the table columns
    thead = table.find("thead")
    if (thead is None): return None

    # Get the column names and indexes of the columns to ignore
    ignore_column_indexes = []
    processed_columns = []

    for index, th in enumerate(thead.find_all("th")):
        if (th.text in ignore_columns):
            ignore_column_indexes.append(index)
            continue

        processed_columns.append(th.text)

    # Get the table content
    processed_rows = []

    tbody = table.find("tbody")
    if (tbody is None): return None

    for child in tbody.children:
        if (child.name != "tr"): continue

        # Get content of the rows, ignore row entirely if it contains "Skip Ad". Also skip cells if their index is in ignore_column_indexes
        row = [cell.text for index, cell in enumerate(child.find_all("td")) if (cell.text != "Skip Ad") and (index not in ignore_column_indexes)]

        processed_rows.append(row)

    return {
        "caption": processed_caption,
        "columns": processed_columns,
        "rows": processed_rows
    }
