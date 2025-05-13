from bs4 import BeautifulSoup
import time
import json

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
        print("   Penn State")
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

def get_team_data(team_name):
    with open("teams.json", "r") as file:
        teams = json.load(file)

    return teams.get(team_name, None)

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

    column_cells = doc.find_all("th")
    columns = [column_cell.text for column_cell in column_cells if (column_cell.text not in ignore_columns)]

    rows = []

    tbody = doc.find("tbody")
    for child in tbody.children:
        if (child.name != "tr"): continue

        child_td = child.find_all("td")
        table_row = [table_row_cell.text for table_row_cell in child_td if (table_row_cell.text != "Skip Ad")]

        zipped = list(zip(columns, table_row))

        rows.append([item[1] for item in zipped])

    return columns, rows
