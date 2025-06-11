# NU Soccer Web Scraper (CLI Version)

A web scraper designed to extract and organize Northwestern University soccer team data from official team websites.

## Usage

### Select a team

Use the `-n` or `--name` flag to select a team. Currently, the app offers 16 teams for selection:
- `Northwestern`
- `Indiana`
- `Ohio State`
- `Maryland`
- `Washington`
- `UCLA`
- `Michigan State`
- `Michigan`
- `Rutgers`
- `Wisconsin`
- `Penn State`
- `UIC`
- `Loyola Chicago`
- `DePaul`
- `Northern Illinois`
- `Chicago State`

### Download roster

Use the `-r` or `--roster` flag to download a team's roster. No further options are needed.

### Download schedule

Use the `-s` or `--schedule` flag to download a team's schedule. No further options are needed.

### Download season statistics

Use the `-t` or `--stats` flag to download a team's season statistics. After the flag, the user may enter the years (separated by spaces) in which you would like to download stats for. If nothing has been entered, the app will default to the current year and the previous year.

Options for years will be added at the start of every Fall NCAA season. However, please be aware that depending on the time of the current season, there might not be stats available to download yet.

### Download box scores

Use the `-b` or `--box-scores` flag to download a team's box scores. After the flag, the user may enter the number of box scores to download. If nothing has been entered, the app will default to `5` box scores.

Box scores are downloaded in order from newest to oldest. And only the current season will be searched. If there are not enough box scores available, the app will attempt to download as many as possible.

### Download articles

Use the `-a` or `--articles` flag to download a team's articles. After the flag, either enter one or two dates. Both dates must follow the `MM/DD/YYYY` format.

If the user enters one date, the app fetches articles from the inputted date to the current date.

If the user enters two dates, the app fetches articles from the first date to the second date. The dates will be sorted if the first date comes after the second date.

After the articles have been fetched. The user will be asked to enter the indexes (separated by spaces) of the articles they would like to download.

### Example usage
```sh
python main.py -n Northwestern -r -s -t 2024 2023 -b 5 -a 12/12/2024
```
```sh
python main.py -n Northwestern -r -s -t 2024 2023 -b 5 -a 12/12/2024 05/01/2025
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change. Follow the instructions below to get an instance running on your local machine.

### Installation

Clone the repository on to your local machine.
```bash
git clone https://github.com/LarryLing/NU-Soccer-Web-Scraper.git
cd NU-Soccer-Web-Scraper
```

Create a virtual environment.
```bash
 python -m venv .venv
```

Install the required packages.
```bash
pip install -r requirements.txt
```

## License

[MIT](https://github.com/LarryLing/NU-Soccer-Web-Scraper/blob/readme/LICENSE)