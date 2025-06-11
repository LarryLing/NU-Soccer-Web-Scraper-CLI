import time

from bs4 import BeautifulSoup
from selenium.common import TimeoutException, WebDriverException

from utils import initialize_web_driver, response_pdf_to_cwd


def download_stats(team_data: dict, years: list[int]) -> None:
    """
    Downloads a team's season stats to a PDF file.

    Args:
        team_data: Dictionary containing team data.
        years: Years for which to print stats for.

    Returns:
        None
    """
    driver = initialize_web_driver()

    pdf_url_in_embed = [
        "Northwestern",
        "Indiana",
        "Ohio State",
        "UCLA",
        "Michigan State",
        "Michigan",
        "DePaul"
    ]

    pdf_url_in_object = [
        "Maryland",
        "Washington",
        "Rutgers",
        "Wisconsin",
        "Penn State",
        "UIC",
        "Loyola Chicago",
        "Northern Illinois",
        "Chicago State"
    ]

    for year in years:
        filename = f"{team_data['abbreviation']} {year} Stats.pdf"

        try:
            if (team_data["name"] == "Penn State") or (team_data["name"] == "Northern Illinois"):
                driver.get(team_data["stats_url"][str(year)])
            else:
                driver.get(team_data["stats_url"].format(year))

            time.sleep(1)

            doc = BeautifulSoup(driver.page_source, "lxml")

            if team_data["name"] in pdf_url_in_embed:
                embed_tag = doc.find("embed")
                if embed_tag:
                    response_pdf_to_cwd(embed_tag["src"], filename)
                    continue
            elif team_data["name"] in pdf_url_in_object:
                object_tag = doc.find("object")
                if object_tag:
                    response_pdf_to_cwd(object_tag["data"], filename)
                    continue

            print(f"**{filename}** :x:  \nReason: Could not find the PDF url.")
        except TimeoutException as e:
            print(f"**{filename}** :x:  \nReason: {e.msg}")
            continue
        except WebDriverException as e:
            print(f"**{filename}** :x:  \nReason: {e.msg}")
            continue

    driver.quit()
