from utils import create_html_tables, get_boost_box_score_pdf_urls, get_sidearm_match_data, initialize_web_driver, process_tables
from pdfkit.configuration import Configuration
from bs4 import BeautifulSoup
import asyncio
import pdfkit
import requests

async def print_roster(team_data: dict[str, str], pdfkit_config: Configuration, settings: dict[str, any]) -> None:
    """
    Print the roster page to a PDF file.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        pdfkit_config (Configuration): Configuration for pdfkit.
        settings (dict[str, Any]): Dictionary containing settings.

    Returns:
        None
    """
    driver = initialize_web_driver(settings["web_driver"])

    processed_tables = await process_tables(driver, team_data["roster_url"], settings["ignore_roster_columns"])

    driver.quit()

    title = f"{team_data["name"]} Mens Soccer Roster"
    html = create_html_tables(title, processed_tables)

    output_path = f"{settings["base_output_path"]}\\{team_data["name"]}\\{team_data["abbreviation"]} Roster.pdf"
    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

async def print_schedule(team_data: dict[str, str], pdfkit_config: Configuration, settings: dict[str, any]) -> None:
    """
    Print the schedule page to a PDF file.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        pdfkit_config (Configuration): Configuration for pdfkit.
        settings (dict[str, Any]): Dictionary containing settings.

    Returns:
        None
    """
    driver = initialize_web_driver(settings["web_driver"])

    processed_tables = await process_tables(driver, team_data["schedule_url"], settings["ignore_schedule_columns"])

    driver.quit()

    title = f"{team_data["name"]} Mens Soccer Schedule"
    html = create_html_tables(title, processed_tables)

    output_path = f"{settings["base_output_path"]}\\{team_data["name"]}\\{team_data["abbreviation"]} Schedule.pdf"
    pdfkit.from_string(html, output_path, configuration=pdfkit_config)

def print_stats(team_data: dict[str, str], settings: dict[str, any]) -> None:
    """
    Print a team's season stats to a PDF file.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        settings (dict[str, Any]): Dictionary containing settings.

    Returns:
        None
    """
    for year in settings["stats"]["years"]:
        if (team_data["base_website_type"] == 1):
            stats_url = f"https://dxbhsrqyrr690.cloudfront.net/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"
        elif (team_data["base_website_type"] == 2):
            stats_url = f"https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"

        response = requests.get(stats_url)
        output_path = f"{settings["base_output_path"]}\\{team_data["name"]}\\{team_data["abbreviation"]} {year} Stats.pdf"
        with open(output_path, 'wb') as file:
            file.write(response.content)

async def print_box_scores(team_data: dict[str, str], settings: dict[str, any]) -> None:
    """
    Print box scores into respective PDF files.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        settings (dict[str, Any]): Dictionary containing settings.

    Returns:
        None
    """

    driver = initialize_web_driver(settings["web_driver"])
    driver.get(team_data["conference_schedule_url"])

    await asyncio.sleep(3)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    if (team_data["conference_schedule_provider"] == "Boost"):
        box_score_pdf_urls = get_boost_box_score_pdf_urls(doc, settings["box_scores"])

        for box_score_pdf_url in box_score_pdf_urls:
            filename = box_score_pdf_url.split("/")[-1]

            response = requests.get(box_score_pdf_url)
            output_path = f"{settings["base_output_path"]}\\{team_data["name"]}\\{filename}"
            with open(output_path, 'wb') as file:
                file.write(response.content)
    elif (team_data["conference_schedule_provider"] == "Sidearm"):
        match_data = get_sidearm_match_data(driver, team_data, doc, settings["box_scores"])

        for home_team, away_team, date, box_score_pdf_url in match_data:
            filename = f"{home_team} vs {away_team} {date}.pdf"

            response = requests.get(box_score_pdf_url)
            output_path = f"{settings["base_output_path"]}\\{team_data["name"]}\\{filename}"
            with open(output_path, 'wb') as file:
                file.write(response.content)

    driver.quit()


