import pdfkit
from utils import create_html_table, process_table

def print_roster(team_data, driver, pdfkit_config, settings):
    """
    Print the roster page to a PDF file.
    """

    title = f"{team_data["name"]} Mens Soccer Roster"
    roster_url = f"{team_data["base_url"]}/sports/mens-soccer/roster/print"
    output_path = f"{settings["output"]["path"]}\\{team_data["name"]}_roster.pdf"

    ignore_columns = settings["roster"]["ignore_columns"]

    columns, rows = process_table(driver, roster_url, ignore_columns)

    html = create_html_table(title, columns, rows)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

def print_schedule(team_data, driver, pdfkit_config, settings):
    """
    Print the schedule page to a PDF file.
    """

    title = f"{team_data["name"]} Mens Soccer Schedule"
    schedule_url = f"{team_data["base_url"]}/sports/mens-soccer/schedule?view=table&print=auto"
    output_path = f"{settings["output"]["path"]}\\{team_data["name"]}_schedule.pdf"

    ignore_columns = settings["schedule"]["ignore_columns"]

    columns, rows = process_table(driver, schedule_url, ignore_columns)

    html = create_html_table(title, columns, rows)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)
