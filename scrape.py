from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from utils import create_html_tables, initialize_web_driver, process_tables
import asyncio
import pdfkit
import requests

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

    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} Roster.pdf"

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

    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} Schedule.pdf"

    ignore_columns = settings["schedule"]["ignore_columns"]

    processed_tables = await process_tables(driver, schedule_url, ignore_columns)

    driver.quit()

    html = create_html_tables(title, processed_tables)

    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

async def print_stats(team_data, year, settings):
    """
    Print the schedule page to a PDF file.
    """

    driver = initialize_web_driver(settings)

    stats_url = f"{team_data["base_url"]}/sports/mens-soccer/stats/{year}/pdf"
    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} {year} Stats.pdf"
    prompts = settings["stats"]["prompts"]

    driver.get(stats_url)

    await asyncio.sleep(1)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    a = doc.find_all(lambda tag: tag.name == "a" and tag.text in prompts)[0]

    if (a is None):
        print("ERROR")
        print("ERROR: unable to locate Download PDF link")
        print("ERROR")

        return

    api_url = team_data["base_url"] + a["href"]

    parsed_url = urlparse(api_url)
    query_params = parse_qs(parsed_url.query)

    file_location = next(iter(query_params.items()))[1][0]

    response = requests.get(file_location)

    with open(output_path, 'wb') as file:
        file.write(response.content)
