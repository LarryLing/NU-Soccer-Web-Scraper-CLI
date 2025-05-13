import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import ChromiumOptions
from scrape import print_roster, print_schedule
from utils import get_team_data, prompt

service = Service(executable_path="chromedriver.exe")
chrome_options = ChromiumOptions()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=chrome_options)

wkhtmltopdf_path = "wkhtmltopdf\\bin\\wkhtmltopdf.exe"
pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

team_name = prompt()

while (team_name != "Exit"):
    team_data = get_team_data(team_name)

    if (team_data is None):
        print("ERROR")
        print("ERROR: invalid team name")
        print("ERROR")
        team_name = prompt()
        continue

    url = f"{team_data["base_url"]}/sports/mens-soccer/roster/print"
    print_roster(team_name, driver, url, pdfkit_config)

    url = f"{team_data["base_url"]}/sports/mens-soccer/schedule?view=table&print=auto"
    print_schedule(team_name, driver, url, pdfkit_config)

    team_name = prompt()

driver.quit()
