import time
import tkinter as tk

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import ChromiumOptions
from bs4 import BeautifulSoup
from tkinter import filedialog

def prompt(teams: dict[str, dict[str, any]]) -> str:
    """
    Prompts the user for a team name returns it.

    Args:
        teams (dict[str, dict[str, any]]): Dictionary containing settings.

    Returns:
        team_name (str): The name of the team.
    """
    try:
        print()
        print("Enter A Team:")

        for team in teams.keys():
            print(f"   {team}")

        print("   Exit")

        team_name = input()
        return team_name

    except Exception as e:
        print("ERROR")
        print("ERROR: invalid input")
        print("ERROR")
        return -1

def select_output_folder() -> str:
    """
    Opens the file dialog, allowing users to select an output folder.

    Args:
        None

    Returns:
        folder_path (str): The full path to the selected folder.
    """
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(master=root)
    root.destroy()

    return folder_path

def initialize_web_driver() -> webdriver.Chrome:
    """
    Initializes a new web driver instance.

    Args:
        None

    Returns:
        driver (WebDriver): A new web driver instance.
    """
    service = Service(executable_path="chromedriver.exe")

    chrome_options = ChromiumOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")

    return webdriver.Chrome(service=service, options=chrome_options)

def insert_html_tables(title: str, html_tables: list[str]) -> str:
    """
    Initialize a HTML table.

    Args:
        title (str): Title for the HTML document.
        tables (list[tuple[str, list[str], list[list[str]]]]): List of processed tables repesented as a tuple of the form (caption, columns, rows) where:
            caption (str): The caption of the table.
            columns (list[str]): List of column names.
            rows (list[list[str]]): List of rows, each row is a list of cell values.

    Returns:
        str: A string representation of the HTML document.
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
            thead {{ display: table-row-group; }}
            th, td {{ font-size: 12px; border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f4f4f4; }}
        </style>
    </head>
    <body>
        <main>
            <h1>{title}</h1>
        </main>
    </body>
    </html>
    """

    doc = BeautifulSoup(html, "lxml")

    main = doc.find("main")

    for html_table in html_tables:
        div_tag = doc.new_tag("div")
        main.append(div_tag)

        table = BeautifulSoup(html_table, "lxml")
        main.append(table)

    return str(doc)

def get_boost_box_score_pdf_urls(doc: BeautifulSoup, count: int) -> list[str]:
    """
    Get the URLs of the box scores from the conference websites provided by Boost.

    Args:
        doc (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        count (int): The number of box scores to print

    Returns:
        list[str]: List of box score PDF URLs.
    """
    schedule_table = doc.find("table")

    box_score_pdf_urls = [a["href"] for a in schedule_table.find_all("a", string="Box Score")]

    return box_score_pdf_urls[(-1 * count):]

def get_sidearm_match_data(driver: webdriver.Chrome, team_data: dict[str, str], doc: BeautifulSoup, count: int) -> list[tuple[str, str, str, str]]:
    """
    Get the URLs of the box scores from the conference websites provided by Sidearm.

    Args:
        driver (WebDriver): The web driver instance.
        team_data (dict[str, str]): Dictionary containing team data.
        doc (BeautifulSoup): The BeautifulSoup object containing the parsed HTML.
        count (int): The number of box scores to print

    Returns:
        match_data (list[tuple[str, str, str, str]]): List of match data represented as a tuple of the form (home_team, away_team, date, box_score_url) where:
            home_team (str): Name of the home team.
            away_team (str): Name of the away team.
            date (str): The date of the match.
            box_score_url (str): The box score PDF url.
    """
    matches = []

    matchday_tables = doc.find_all("table")

    for matchday_table in matchday_tables:
        matchday_table_body = matchday_table.find("tbody")

        for tr in matchday_table_body.find_all("tr"):
            away_team_td = tr.select_one('td[class*="sidearm-team-away"]')
            home_team_td = tr.select_one('td[class*="sidearm-team-home"]')

            away_team = away_team_td.find("span", class_="sidearm-calendar-list-group-list-game-team-title").find(['a', 'span']).text
            home_team = home_team_td.find("span", class_="sidearm-calendar-list-group-list-game-team-title").find(['a', 'span']).text
            if (away_team != team_data["name"] and home_team != team_data["name"]): continue

            matchday_table_caption = matchday_table.find("caption")
            date = matchday_table_caption.find("span", class_="hide-on-medium sidearm-calendar-list-group-heading-date").text.replace("/", "_")

            box_score_href = team_data["conference_base_url"] + tr.find("a", string="Box Score")["href"]

            matches.append([home_team, away_team, date, box_score_href])

    match_data = []

    for match in matches[(-1 * count):]:
        driver.get(match[3])
        time.sleep(1)
        doc = BeautifulSoup(driver.page_source, "lxml")

        box_score_preview_url = team_data["conference_base_url"] + doc.find("div", id="print-bar").find("a")["href"]

        driver.get(box_score_preview_url)
        time.sleep(1)
        doc = BeautifulSoup(driver.page_source, "lxml")
        box_score_pdf_url = doc.find("a", string="Open")["href"]

        match_data.append((match[0], match[1], match[2], box_score_pdf_url))

    return match_data
