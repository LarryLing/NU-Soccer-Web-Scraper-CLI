import pdfkit
from utils import create_html_table, process_table

def print_roster(university_name, driver, url, pdfkit_config, settings):
    """
    Print the roster page to a PDF file.
    """

    title = f"{university_name} Mens Soccer Roster"
    output_path = f"{settings["output"]["path"]}\\{university_name}_roster.pdf"

    ignore_columns = settings["roster"]["ignore_columns"]

    columns, rows = process_table(driver, url, ignore_columns=ignore_columns)

    html = create_html_table(title, columns, rows)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

def print_schedule(university_name, driver, url, pdfkit_config, settings):
    """
    Print the schedule page to a PDF file.
    """

    title = f"{university_name} Mens Soccer Schedule"
    output_path = f"{settings["output"]["path"]}\\{university_name}_schedule.pdf"

    ignore_columns = settings["schedule"]["ignore_columns"]

    columns, rows = process_table(driver, url, ignore_columns=ignore_columns)

    html = create_html_table(title, columns, rows)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)
