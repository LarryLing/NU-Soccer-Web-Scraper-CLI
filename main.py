import argparse
import json
from datetime import datetime

import pandas as pd

from articles import fetch_articles, download_articles
from box_scores import download_box_scores
from roster import download_roster
from schedule import download_schedule
from stats import download_stats
from utils import prompt_user_for_articles


def main():
    parser = argparse.ArgumentParser(description="Scrape Team Data")

    with open("teams.json", "r") as file:
        teams = json.load(file)

    parser.add_argument("-n", "--name",
                        required=True,
                        choices=list(teams.keys()),
                        help="Accepts a team name (e.g., -n Northwestern)")
    parser.add_argument("-r", "--roster",
                        action="store_true",
                        help="Determines whether or not the schedule is downloaded (e.g., -r)")
    parser.add_argument("-s", "--schedule",
                        action="store_true",
                        help="Determines whether or not the schedule is downloaded (e.g., -s)")
    parser.add_argument("-t", "--stats",
                        help="Accepts 0 or more years (e.g., -t 2024 2023)",
                        nargs="+",
                        type=int,
                        default=[datetime.now().year, datetime.now().year - 1])
    parser.add_argument("-b", "--box-scores",
                        help="Accepts a positive integer (e.g., -b 5)",
                        type=int,
                        default=5)
    parser.add_argument("-a", "--articles",
                        help="Accepts 1 or 2 dates (e.g., -a 12/12/2024 or -a 12/12/2024 05/01/2025)",
                        nargs="+")

    args = parser.parse_args()

    team_data = teams[args.name]

    if args.roster:
        filename = f"{team_data['abbreviation']} Roster.pdf"
        download_roster(team_data["roster_url"], filename)

    if args.schedule:
        filename = f"{team_data["abbreviation"]} Schedule.pdf"
        download_schedule(team_data["name"], team_data["schedule_url"], filename)

    if args.stats:
        download_stats(team_data, args.stats)

    if args.box_scores:
        download_box_scores(team_data, args.box_scores)

    if args.articles:
        start_date = datetime.strptime(args.articles, "%m/%d/%Y").date()
        now = datetime.now().date()

        fetched_articles = fetch_articles(team_data, (start_date, now))
        with pd.option_context('display.max_colwidth', None):
            print(fetched_articles.drop("URL", axis=1))

        article_indexes = prompt_user_for_articles(len(fetched_articles) - 1)
        filtered_articles = fetched_articles.iloc[article_indexes]

        download_articles(filtered_articles)

    print("All files have been downloaded!")


if __name__ == "__main__":
    main()
