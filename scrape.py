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

    roster_url = f"{team_data["base_url"]}/roster"
    if (team_data["base_website_type"] == 1):
        roster_url = roster_url + "/print"
    elif (team_data["base_website_type"] == 2):
        roster_url = roster_url + "?print=true"

    processed_tables = await process_tables(driver, roster_url, settings["roster"]["ignore_columns"])

    driver.quit()

    title = f"{team_data["name"]} Mens Soccer Roster"
    html = create_html_tables(title, processed_tables)
    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} Roster.pdf"
    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

async def print_schedule(team_data, pdfkit_config, settings):
    """
    Print the schedule page to a PDF file.
    """

    driver = initialize_web_driver(settings)

    schedule_url = f"{team_data["base_url"]}/schedule"
    if (team_data["base_website_type"] == 1):
        schedule_url = schedule_url + "?view=table&print=auto"
    elif (team_data["base_website_type"] == 2):
        schedule_url = schedule_url + "?print=true"

    processed_tables = await process_tables(driver, schedule_url, settings["schedule"]["ignore_columns"])

    driver.quit()

    title = f"{team_data["name"]} Mens Soccer Schedule"
    html = create_html_tables(title, processed_tables)
    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} Schedule.pdf"
    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

async def print_stats(team_data, year, settings):
    """
    Print a team's season stats to a PDF file.
    """

    driver = initialize_web_driver(settings)
    stats_url = f"{team_data["base_url"]}/stats/{year}/pdf"
    driver.get(stats_url)

    await asyncio.sleep(1)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    prompts = settings["stats"]["prompts"]
    a = doc.find_all(lambda tag: tag.name == "a" and tag.text in prompts)[0]

    if (a is None): return

    api_url = team_data["base_url"] + a["href"]
    parsed_url = urlparse(api_url)
    query_params = parse_qs(parsed_url.query)
    file_location = next(iter(query_params.items()))[1][0]

    response = requests.get(file_location)
    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} {year} Stats.pdf"
    with open(output_path, 'wb') as file:
        file.write(response.content)

async def print_box_scores(team_data, settings):
    """
    Print box scores into respective PDF files.
    """

    driver = initialize_web_driver(settings)
    driver.get(team_data["conference_schedule_url"])

    await asyncio.sleep(3)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    driver.quit()

    schedule_table = doc.find("table")
    box_scores = [a["href"] for a in schedule_table.find_all("a", string="Box Score")][(-1 * settings["box_scores"]["count"]):]
    for box_score in box_scores:
        filename = box_score.split("/")[-1]

        response = requests.get(box_score)
        output_path = f"{settings["paths"]["output"]}\\{filename}"
        with open(output_path, 'wb') as file:
            file.write(response.content)
