import asyncio
import pdfkit
import requests
import pandas as pd

from io import StringIO
from utils import insert_html_tables, get_boost_box_score_pdf_urls, get_sidearm_match_data, initialize_web_driver
from bs4 import BeautifulSoup
from pdfkit.configuration import Configuration

async def download_tables(url: str, output_file_path: str, ignore_columns: list[str], pdfkit_config: Configuration) -> dict[str, str]:
    """
    Print the roster page to a PDF file.

    Args:
        url (str): URL of the site.

    Returns:
        table_content (dict[str, str]): A dictionary of content from the HTML tables.
    """
    driver = initialize_web_driver()
    driver.get(url)
    await asyncio.sleep(1)

    doc = BeautifulSoup(driver.page_source, "lxml")

    extracted_tables = [StringIO(str(table)) for table in doc(["table"]) if (table.find("thead"))]

    html_tables = []
    for extracted_table in extracted_tables:
        dataframe = pd.read_html(extracted_table)[0]
        dataframe = dataframe.drop(columns=ignore_columns, errors="ignore")
        dataframe = dataframe.fillna("")

        html_tables.append(dataframe.to_html(index=False))

    full_html = insert_html_tables(doc.find("title"), html_tables)

    pdfkit.from_string(full_html, output_file_path, configuration=pdfkit_config)

def download_stats(team_data: dict[str, str], years: int, output_folder_path: str) -> None:
    """
    Print a team's season stats to a PDF file.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        years (int): Years for which to print stats for.
        output_folder_path (str): Path to the output folder.

    Returns:
        None
    """
    for year in years:
        if (team_data["base_website_type"] == 1):
            stats_url = f"https://dxbhsrqyrr690.cloudfront.net/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"
        elif (team_data["base_website_type"] == 2):
            stats_url = f"https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"

        response = requests.get(stats_url)
        output_path = f"{output_folder_path}\\{team_data["abbreviation"]} {year} Stats.pdf"

        with open(output_path, 'wb') as file:
            file.write(response.content)

async def download_box_scores(team_data: dict[str, str], count: int, output_folder_path: str) -> None:
    """
    Print box scores into respective PDF files.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        count (int): The number of box scores to print.
        output_folder_path (str): Path to the output folder.

    Returns:
        None
    """

    driver = initialize_web_driver()
    driver.get(team_data["conference_schedule_url"])

    await asyncio.sleep(2)

    doc = BeautifulSoup(driver.page_source, "html.parser")

    if (team_data["conference_schedule_provider"] == "Boost"):
        box_score_pdf_urls = get_boost_box_score_pdf_urls(doc, count)

        for box_score_pdf_url in box_score_pdf_urls:
            filename = box_score_pdf_url.split("/")[-1]

            response = requests.get(box_score_pdf_url)
            output_path = f"{output_folder_path}\\{filename}"

            with open(output_path, 'wb') as file:
                file.write(response.content)
    elif (team_data["conference_schedule_provider"] == "Sidearm"):
        match_data = get_sidearm_match_data(driver, team_data, doc, count)

        for home_team, away_team, date, box_score_pdf_url in match_data:
            filename = f"{home_team} vs {away_team} {date}.pdf"

            response = requests.get(box_score_pdf_url)
            output_path = f"{output_folder_path}\\{filename}"

            with open(output_path, 'wb') as file:
                file.write(response.content)

    driver.quit()
