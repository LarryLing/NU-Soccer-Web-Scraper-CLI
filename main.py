import sys
import os
from pathlib import Path

# Get the directory where this script lives
script_dir = Path(__file__).parent.absolute()

# Add to Python path if not already present
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

import argparse
import json
from datetime import datetime

import pandas as pd

from articles import fetch_articles, download_articles
from box_scores import download_box_scores
from roster import download_roster
from schedule import download_schedule
from stats import download_stats
from utils import prompt_user_for_articles, validate_articles_argument, validate_box_scores_argument, NORMAL, GREEN, \
    BOLD


def main():
    parser = argparse.ArgumentParser(description="Scrape Team Data")

    with open(script_dir / "teams.json", "r") as file:
        teams = json.load(file)

    parser.add_argument("-n", "--name",
                        choices=list(teams.keys()),
                        required=True,
                        help="Accepts a team name (e.g., -n Northwestern)")
    parser.add_argument("-r", "--roster",
                        action="store_true",
                        help="Determines whether or not the schedule is downloaded (e.g., -r)")
    parser.add_argument("-s", "--schedule",
                        action="store_true",
                        help="Determines whether or not the schedule is downloaded (e.g., -s)")
    parser.add_argument("-t", "--stats",
                        nargs="*",
                        help="Accepts 0 or more years (e.g., -t 2024 2023)")
    parser.add_argument("-b", "--box-scores",
                        nargs="?",
                        const = 5,
                        type=int,
                        help="Accepts 0 or 1 integers greater than 1 (e.g., -b 5)")
    parser.add_argument("-a", "--articles",
                        nargs="+",
                        help="Accepts 1 or 2 dates (e.g., -a 12/12/2024 or -a 12/12/2024 05/01/2025)")

    args = parser.parse_args()

    if hasattr(args, 'box_scores') and args.box_scores is not None:
        try:
            args.box_scores = validate_box_scores_argument(args.box_scores)
        except argparse.ArgumentTypeError as e:
            parser.error(str(e))

    if hasattr(args, 'articles') and args.articles is not None:
        try:
            args.articles = validate_articles_argument(args.articles)
        except argparse.ArgumentTypeError as e:
            parser.error(str(e))

    team_data = teams[args.name]

    if args.roster:
        filename = f"{team_data['abbreviation']} Roster.pdf"
        download_roster(team_data["roster_url"], filename)

    if args.schedule:
        filename = f"{team_data["abbreviation"]} Schedule.pdf"
        download_schedule(team_data["name"], team_data["schedule_url"], filename)

    if args.stats is not None:
        stats = args.stats if len(args.stats) > 0 else [str(datetime.now().year), str(datetime.now().year - 1)]
        download_stats(team_data, stats)

    if args.box_scores is not None:
        download_box_scores(team_data, args.box_scores)

    if args.articles is not None:
        fetched_articles = fetch_articles(team_data, args.articles)
        with pd.option_context('display.max_colwidth', None):
            print(fetched_articles.drop("URL", axis=1))

        article_indexes = prompt_user_for_articles(len(fetched_articles) - 1)
        filtered_articles = fetched_articles.iloc[article_indexes]

        download_articles(filtered_articles)

    print(f"{BOLD}{GREEN}[DONE]{NORMAL} Finished downloading files to {os.getcwd()}")


if __name__ == "__main__":
    main()
