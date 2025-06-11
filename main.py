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

    parser.add_argument("-n", "--name", required=True, choices=list(teams.keys()), help="Name of the team to scrape")
    parser.add_argument("-r", "--roster", action="store_true", help="Get the roster data")
    parser.add_argument("-s", "--schedule", action="store_true", help="Get the schedule data")
    parser.add_argument("-t", "--stats", help="Years for which to download stats", nargs="+", type=int)
    parser.add_argument("-b", "--box-scores", help="Number of box scores to download", type=int)
    parser.add_argument("-a", "--articles", help="Start date from which to search for articles")

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
