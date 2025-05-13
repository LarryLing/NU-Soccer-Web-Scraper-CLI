import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import ChromiumOptions
from scrape import print_roster, print_schedule
from utils import get_team_data, prompt
import json

# Initialize the Chrome WebDriver
service = Service(executable_path="chromedriver.exe")
chrome_options = ChromiumOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=chrome_options)

# Configure PDFKit by setting the path to wkhtmltopdf
wkhtmltopdf_path = "wkhtmltopdf\\bin\\wkhtmltopdf.exe"
pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# Read JSON settings file
with open("settings.json", "r") as file:
    settings = json.load(file)

team_name = prompt()

while (team_name != "Exit"):
    team_data = get_team_data(team_name)

    if (team_data is None):
        print("ERROR")
        print("ERROR: invalid team name")
        print("ERROR")
        team_name = prompt()

        continue

    print_roster(team_data, driver, pdfkit_config, settings)

    print_schedule(team_data, driver, pdfkit_config, settings)

    team_name = prompt()

driver.quit()
