import argparse
import json

from box_scores import download_box_scores
from roster import download_roster
from schedule import download_schedule
from stats import download_stats


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
        pass

    print("All files have been downloaded!")


if __name__ == "__main__":
    main()
