import pdfkit
from utils import create_html_tables, initialize_web_driver, process_tables

async def print_roster(team_data, pdfkit_config, settings):
    """
    Print the roster page to a PDF file.
    """

    driver = initialize_web_driver(settings)

    title = f"{team_data["name"]} Mens Soccer Roster"

    roster_url = f"{team_data["base_url"]}/sports/mens-soccer/roster"
    if (team_data["type"] == 1):
        roster_url = roster_url + "/print"
    elif (team_data["type"] == 2):
        roster_url = roster_url + "?print=true"

    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]}_roster.pdf"

    ignore_columns = settings["roster"]["ignore_columns"]

    processed_tables = await process_tables(driver, roster_url, ignore_columns)

    driver.quit()

    html = create_html_tables(title, processed_tables)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

async def print_schedule(team_data, pdfkit_config, settings):
    """
    Print the schedule page to a PDF file.
    """

    driver = initialize_web_driver(settings)

    title = f"{team_data["name"]} Mens Soccer Schedule"
    
    schedule_url = f"{team_data["base_url"]}/sports/mens-soccer/schedule"
    if (team_data["type"] == 1):
        schedule_url = schedule_url + "?view=table&print=auto"
    elif (team_data["type"] == 2):
        schedule_url = schedule_url + "?print=true"

    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]}_schedule.pdf"

    ignore_columns = settings["schedule"]["ignore_columns"]

    processed_tables = await process_tables(driver, schedule_url, ignore_columns)

    driver.quit()

    html = create_html_tables(title, processed_tables)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)
