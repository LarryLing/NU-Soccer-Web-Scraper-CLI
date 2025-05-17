import asyncio
import os
import pdfkit
import streamlit as st
import json

from scrape import print_box_scores, print_roster, print_schedule, print_stats

with open("settings.json", "r") as file:
    settings: dict[str, any] = json.load(file)

pdfkit_config = pdfkit.configuration(wkhtmltopdf=settings["wkhtmltopdf"])

functions_table = {
    "Roster": print_roster,
    "Schedule": print_schedule,
    "Box Scores": print_box_scores
}

st.title = "NU Soccer Web Scraper"

team_name = st.selectbox(
    label="Enter a team name:",
    options=settings["teams"].keys(),
    index=None,
    placeholder="ie: Northwestern",
)

with st.container(border=True):
    st.write()

    if ("disabled" not in st.session_state):
        st.session_state.disabled = False

    selected_data = st.segmented_control(
        label="Select the data you want to download",
        options=settings["data_options"],
        selection_mode="multi",
        disabled=st.session_state.disabled
    )

    select_all = st.toggle(
        label="Select all",
        key="disabled"
    )

data_to_scrape = settings["data_options"] if (select_all) else selected_data

if ("Stats" in data_to_scrape):
    with st.container(border=True):
        years = st.multiselect(
            label="Select which year's stats you want to download",
            options=settings["stats"]["years"],
            default=settings["stats"]["years"][0:2],
        )

if ("Box Scores" in data_to_scrape):
    with st.container(border=True):
        count = st.number_input(
            label="Enter how many box scores you want to download (1-10)",
            step=1,
            min_value=1,
            value=5,
            max_value=10
        )

        st.write("_Disclaimer: Box scores are downloaded in order from most recent to oldest_")

scrape_button = st.button(
    "Download data",
    disabled=(not team_name or not (data_to_scrape))
)

if (scrape_button):
    if (len(data_to_scrape) == 1):
        st.write(f"Downloading {team_name}'s {data_to_scrape[0]}...")
    elif (len(data_to_scrape) == 2):
        st.write(f"Downloading {team_name}'s {" and ".join(data_to_scrape)}...")
    else:
        st.write(f"Downloading {team_name}'s {", ".join(data_to_scrape[:-1]) + ", and " + data_to_scrape[-1]}...")

    async def scrape_data():
        team_data = settings["teams"].get(team_name, None)

        team_output_path = f"{settings['base_output_path']}\\{team_data['name']}"
        if (not os.path.exists(team_output_path)):
            os.makedirs(team_output_path)

        promises = []

        if ("Roster" in data_to_scrape):
            promises.append(print_roster(team_data, pdfkit_config, settings))

        if ("Schedule" in data_to_scrape):
            promises.append(print_schedule(team_data, pdfkit_config, settings))

        if ("Box Scores" in data_to_scrape):
            promises.append(print_box_scores(team_data, settings))

        await asyncio.gather(*promises)

        if ("Stats" in data_to_scrape):
            print_stats(team_data, settings)

    asyncio.run(scrape_data())

    st.write("Done!")
