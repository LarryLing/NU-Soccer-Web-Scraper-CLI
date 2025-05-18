import asyncio
import pdfkit
import requests
import pandas as pd
import streamlit as st

from utils import find_penn_state_stats_url, insert_html_tables, get_boost_box_score_pdf_urls, get_sidearm_match_data, initialize_web_driver, sanitize_table
from bs4 import BeautifulSoup
from pdfkit.configuration import Configuration

async def download_tables(team_name: str, type: str, url: str, output_file_path: str, ignored_columns: list[str], pdfkit_config: Configuration) -> None:
    """
    Download the roster page to a PDF file.

    Args:
        team_name (str): Name of the team.
        type (str): Type of table(s) to download. Either "roster" or "schedule".
        url (str): URL of the site.
        output_file_path (str): Path to the downloaded PDF file.
        ignored_columns: (list[str]): List of columns to ignore.

    Returns:
        None
    """
    st.write(f"Downloading {team_name}'s {type}...")

    driver = initialize_web_driver()
    driver.get(url)
    await asyncio.sleep(1)

    doc = BeautifulSoup(driver.page_source, "lxml")

    driver.quit()

    extracted_tables = []
    for table in doc(["table"]):
        if (not table.find("thead")):
            continue

        sanitized_table = sanitize_table(str(table))
        extracted_tables.append(sanitized_table)

    html_tables = []
    for extracted_table in extracted_tables:
        dataframe = pd.read_html(extracted_table)[0]
        dataframe = dataframe.drop(columns=ignored_columns, errors="ignore")
        dataframe = dataframe.fillna("")

        html_tables.append(dataframe.to_html(index=False))

    full_html = insert_html_tables(doc.find("title"), html_tables)

    pdfkit.from_string(full_html, output_file_path, configuration=pdfkit_config)

    st.write(f"Finished downloading {team_name}'s {type}!")

async def download_stats(team_data: dict[str, str], years: list[int], output_folder_path: str) -> None:
    """
    Print a team's season stats to a PDF file.

    Args:
        team_data (dict[str, str]): Dictionary containing team data.
        years (list[int]): Years for which to print stats for.
        output_folder_path (str): Path to the output folder.

    Returns:
        None
    """
    st.write(f"Downloading {team_data["name"]}'s stats...")

    if (team_data["name"] == "Penn State"):
        url = f"https://{team_data["hostname"]}/sports/mens-soccer"
        stats_url = await find_penn_state_stats_url(url)

        response = requests.get(stats_url)

        if (response.status_code == 404):
            return

        output_path = f"{output_folder_path}\\{team_data["abbreviation"]} Stats.pdf"

        with open(output_path, 'wb') as file:
            file.write(response.content)

        st.write(f"Finished downloading {team_data["name"]}'s stats!")
        return

    for year in years:
        stats_url = None

        if (team_data["base_website_type"] == 1):
            stats_url = f"https://dxbhsrqyrr690.cloudfront.net/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"
        elif (team_data["base_website_type"] == 2):
            stats_url = f"https://s3.us-east-2.amazonaws.com/sidearm.nextgen.sites/{team_data["hostname"]}/stats/msoc/{year}/pdf/cume.pdf"

        response = requests.get(stats_url)

        if (response.status_code == 404):
            continue

        output_path = f"{output_folder_path}\\{team_data["abbreviation"]} {year} Stats.pdf"

        with open(output_path, 'wb') as file:
            file.write(response.content)

    st.write(f"Finished downloading {team_data["name"]}'s stats!")

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
    st.write(f"Downloading {team_data["name"]}'s box scores...")

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

    st.write(f"Finished downloading {team_data["name"]}'s box scores!")
