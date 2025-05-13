import pdfkit
from scrape import print_roster, print_schedule
from utils import get_team_data, prompt
import json
import asyncio

async def main():
    with open("settings.json", "r") as file:
        settings = json.load(file)

    pdfkit_config = pdfkit.configuration(wkhtmltopdf=settings["paths"]["wkhtmltopdf"])

    team_name = prompt()

    while (team_name != "Exit"):
        team_data = get_team_data(team_name)

        if (team_data is None):
            print("ERROR")
            print("ERROR: invalid team name")
            print("ERROR")
            team_name = prompt()

            continue

        promises = [
            print_roster(team_data, pdfkit_config, settings),
            print_schedule(team_data, pdfkit_config, settings)
        ]

        await asyncio.gather(*promises)

        team_name = prompt()

    return

asyncio.run(main())
