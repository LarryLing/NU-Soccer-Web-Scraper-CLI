from scrape import print_box_scores, print_roster, print_schedule, print_stats
from utils import prompt
import pdfkit
import json
import asyncio

async def main():
    with open("settings.json", "r") as file:
        settings = json.load(file)

    pdfkit_config = pdfkit.configuration(wkhtmltopdf=settings["paths"]["wkhtmltopdf"])

    team_name = prompt(settings)

    while (team_name != "Exit"):
        team_data = settings["teams"].get(team_name, None)

        if (team_data is None):
            print("ERROR")
            print("ERROR: invalid team name")
            print("ERROR")
            team_name = prompt(settings)

            continue

        promises = [
            print_roster(team_data, pdfkit_config, settings),
            print_schedule(team_data, pdfkit_config, settings),
            print_box_scores(team_data, settings)
        ]

        await asyncio.gather(*promises)

        print_stats(team_data, settings)

        team_name = prompt(settings)

    return

asyncio.run(main())
