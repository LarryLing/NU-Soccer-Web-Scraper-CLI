from bs4 import BeautifulSoup
from utils import create_html_tables, get_boost_box_score_pdf_urls, get_sidearm_box_score_pdf_urls, initialize_web_driver, process_tables
import asyncio
import pdfkit
import requests

async def print_roster(team_data, pdfkit_config, settings):
    """
    Print the roster page to a PDF file.
    """

    driver = initialize_web_driver(settings)

    processed_tables = await process_tables(driver, team_data["roster_url"], settings["roster"]["ignore_columns"])

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

    processed_tables = await process_tables(driver, team_data["schedule_url"], settings["schedule"]["ignore_columns"])

    driver.quit()

    title = f"{team_data["name"]} Mens Soccer Schedule"
    html = create_html_tables(title, processed_tables)
    output_path = f"{settings["paths"]["output"]}\\{team_data["name"]} Schedule.pdf"
    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

def print_stats(team_data, settings):
    """
    Print a team's season stats to a PDF file.
    """

    for year in settings["stats"]["years"]:
        if (team_data["base_website_type"] == 1):
            stats_url = f"https://dxbhsrqyrr690.cloudfront.net/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"
        elif (team_data["base_website_type"] == 2):
            stats_url = f"https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"

        response = requests.get(stats_url)
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

    if (team_data["conference_schedule_provider"] == "Boost"):
        box_score_pdf_urls = get_boost_box_score_pdf_urls(doc, settings)

        for box_score_pdf_url in box_score_pdf_urls:
            filename = box_score_pdf_url.split("/")[-1]

            response = requests.get(box_score_pdf_url)
            output_path = f"{settings["paths"]["output"]}\\{filename}"
            with open(output_path, 'wb') as file:
                file.write(response.content)
    elif (team_data["conference_schedule_provider"] == "Sidearm"):
        box_score_pdf_urls = get_sidearm_box_score_pdf_urls(driver, team_data, doc, settings)

        for home_team, away_team, box_score_pdf_url in box_score_pdf_urls:
            filename = f"{home_team} vs {away_team} Box Score.pdf"

            response = requests.get(box_score_pdf_url)
            output_path = f"{settings["paths"]["output"]}\\{filename}"
            with open(output_path, 'wb') as file:
                file.write(response.content)

    driver.quit()


