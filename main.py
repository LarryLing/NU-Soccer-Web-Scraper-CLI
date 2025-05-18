import asyncio
import pdfkit
import streamlit as st
import json

from scrape import download_box_scores, download_stats, download_tables
from utils import select_output_folder

with open("teams.json", "r") as file:
    teams: dict[str, any] = json.load(file)

pdfkit_config = pdfkit.configuration(wkhtmltopdf="wkhtmltopdf\\bin\\wkhtmltopdf.exe")

st.title = "NU Soccer Web Scraper"

team_name = st.selectbox(
    label="Enter a team name:",
    options=teams.keys(),
    index=None,
    placeholder="ie: Northwestern",
)

with st.container(border=True):
    st.write()

    if ("disabled" not in st.session_state):
        st.session_state.disabled = False

    selected_data = st.segmented_control(
        label="Select the data you want to download:",
        options=["Roster", "Schedule", "Stats", "Box Scores", "Related Articles"],
        selection_mode="multi",
        disabled=st.session_state.disabled
    )

    select_all = st.toggle(
        label="Select all",
        key="disabled"
    )

data_to_scrape = ["Roster", "Schedule", "Stats", "Box Scores", "Related Articles"] if (select_all) else selected_data

if ("Roster" in data_to_scrape):
    with st.container(border=True):
        ignored_roster_columns = st.multiselect(
            label="Select the roster columns that you would like to ignore:",
            options=["Image", "Twitter", "Instagram", "Major"],
            default=["Image", "Twitter", "Instagram", "Major"],
            accept_new_options=True,
            placeholder="ie: Twitter"
        )

if ("Schedule" in data_to_scrape):
    with st.container(border=True):
        ignored_schedule_columns = st.multiselect(
            label="Select the schedule columns that you would like to ignore:",
            options=["Links"],
            default=["Links"],
            accept_new_options=True,
            placeholder="ie: Links"
        )

if ("Stats" in data_to_scrape):
    with st.container(border=True):
        years = st.multiselect(
            label="Select which year's stats you would like to download:",
            options=["2025", "2024", "2023"],
            default=["2025", "2024"],
            placeholder="ie: 2024"
        )

        with st.expander("**Disclaimer**"):
            st.warning("Options for years will be added at the start of every calendar year. However, please be aware that depending on the time of current season, there might not be stats available to download yet.")

if ("Box Scores" in data_to_scrape):
    with st.container(border=True):
        count = st.number_input(
            label="Enter the number of box scores you would like download (1-10):",
            step=1,
            min_value=1,
            value=5,
            max_value=10,
            placeholder="ie: 5"
        )

        with st.expander("**Disclaimer**"):
            st.warning("Box scores are downloaded in order from most newest to oldest. If there are not enough box scores available, we will attempt to download as many as possible.")

with st.container(border=True):
    output_folder_path: str | None = st.session_state.get("output_folder_path", None)
    folder_select_button = st.button("Select Output Folder")

    if (folder_select_button):
        output_folder_path = select_output_folder()
        st.session_state.output_folder_path = output_folder_path

    if (output_folder_path):
        st.write(f"_{output_folder_path}_")
    else:
        st.write("_No output folder selected._")

scrape_button = st.button(
    label="Download",
    disabled=((not team_name) or (not data_to_scrape) or (not output_folder_path))
)

if (scrape_button):
    async def download_data():
        team_data = teams.get(team_name, None)

        promises = []

        if ("Roster" in data_to_scrape):
            output_file = f"{output_folder_path}\\{team_data["abbreviation"]} Roster.pdf"
            promises.append(download_tables(team_data["name"], "roster", team_data["roster_url"], output_file, ignored_roster_columns, pdfkit_config))

        if ("Schedule" in data_to_scrape):
            output_file = f"{output_folder_path}\\{team_data["abbreviation"]} Schedule.pdf"
            promises.append(download_tables(team_data["name"], "schedule", team_data["schedule_url"], output_file, ignored_schedule_columns, pdfkit_config))

        if ("Box Scores" in data_to_scrape):
            promises.append(download_box_scores(team_data, count, output_folder_path))

        if ("Stats" in data_to_scrape):
            promises.append(download_stats(team_data, years, output_folder_path))

        await asyncio.gather(*promises)

        st.write("Finished!")

    asyncio.run(download_data())
