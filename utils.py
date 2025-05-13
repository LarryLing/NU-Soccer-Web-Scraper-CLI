from bs4 import BeautifulSoup
import time

def prompt():
    """
    Prompts the user and returns the command number
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
        print("   Penn State")
        print("   UIC")
        print("   Loyola")
        print("   DePaul")
        print("   Exit")

        cmd = input()
        return cmd

    except Exception as e:
        print("ERROR")
        print("ERROR: invalid input")
        print("ERROR")
        return -1

def get_team_data(team_name):
    teams = {
        "Northwestern": {
            "base_url": "https://nusports.com",
            "type": 1
        },
        "Indiana": {
            "base_url": "https://iuhoosiers.com",
            "type": 1
        },
        "Ohio State": {
            "base_url": "https://ohiostatebuckeyes.com",
            "type": 1
        },
        "Maryland": {
            "base_url": "https://umterps.com",
            "type": 2
        },
        "Washington": {
            "base_url": "https://gohuskies.com",
            "type": 2
        },
        "UCLA": {
            "base_url": "https://uclabruins.com",
            "type": 1
        },
        "Michigan State": {
            "base_url": "https://msuspartans.com",
            "type": 1
        },
        "Michigan": {
            "base_url": "https://mgoblue.com",
            "type": 1
        },
        "Rutgers": {
            "base_url": "https://scarletknights.com",
            "type": 2
        },
        "Wisconsin": {
            "base_url": "https://uwbadgers.com",
            "type": 2
        },
        "Penn State": {
            "base_url": "https://gopsusports.com",
            "type": 3
        },
        "UIC": {
            "base_url": "https://uicflames.com",
            "type": 2
        },
        "Loyola": {
            "base_url": "https://loyolaramblers.com",
            "type": 2
        },
        "DePaul": {
            "base_url": "https://depaulbluedemons.com",
            "type": 1
        },
    }

    if (team_name in teams):
        return teams[team_name]
    else:
        return None

def create_html_table(title, columns, rows):
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
            th, td {{ font-size: 12px; border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <main>
            <h3>{title}</h3>
            <table>
                <thead>
                    <tr>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </main>
    </body>
    </html>
    """

    doc = BeautifulSoup(html, "html.parser")

    tr = doc.find("tr")
    for column in columns:
        th = doc.new_tag("th", string=column)
        tr.append(th)

    tbody = doc.find("tbody")
    for row in rows:
        tr = doc.new_tag("tr")
        for cell in row:
            td = doc.new_tag("td", string=cell)
            tr.append(td)
        tbody.append(tr)

    return doc.prettify()

def process_table(driver, url, ignore_columns):
    """
    Process the table from the page.
    """

    driver.get(url)

    time.sleep(2)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    # First get the columns
    column_cells = doc.find_all("th")
    columns = [column_cell.text for column_cell in column_cells if (column_cell.text not in ignore_columns)]

    # Then get the rows
    rows = []

    tbody = doc.find("tbody")
    for child in tbody.children:
        if (child.name != "tr"): continue

        child_td = child.find_all("td")
        table_row = [table_row_cell.text for table_row_cell in child_td if (table_row_cell.text != "Skip Ad")]

        zipped = list(zip(columns, table_row))

        rows.append([item[1] for item in zipped])

    return columns, rows
