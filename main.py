import asyncio
import streamlit as st
import json

from scrape import download_box_scores, download_roster, download_schedule, download_stats
from utils import select_output_folder

with open("settings.json", "r") as file:
    settings: dict[str, any] = json.load(file)

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
        label="Select the data you want to download:",
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
            label="Select which year's stats you want to download:",
            options=settings["stats_years"],
            default=settings["stats_years"][0:2],
            placeholder="ie: 2024"
        )

        st.warning("_Options for years will be added at the start of every calendar year. However, please be aware that depending on the time of current season, there might not be stats available to download yet._")

if ("Box Scores" in data_to_scrape):
    with st.container(border=True):
        count = st.number_input(
            label="Enter the number of box scores you want to download (1-10):",
            step=1,
            min_value=1,
            value=5,
            max_value=10,
            placeholder="ie: 5"
        )

        st.warning("_Box scores are downloaded in order from most newest to oldest. If there are not enough box scores available, we will attempt to download as many as possible._")

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
    label="Download data",
    disabled=((not team_name) or (not data_to_scrape) or (not output_folder_path))
)

if (scrape_button):
    if (len(data_to_scrape) == 1):
        st.write(f"Downloading {team_name}'s {data_to_scrape[0]}...")
    elif (len(data_to_scrape) == 2):
        st.write(f"Downloading {team_name}'s {" and ".join(data_to_scrape)}...")
    else:
        st.write(f"Downloading {team_name}'s {", ".join(data_to_scrape[:-1]) + ", and " + data_to_scrape[-1]}...")

    async def download_data():
        team_data = settings["teams"].get(team_name, None)

        promises = []

        if ("Roster" in data_to_scrape):
            promises.append(download_roster(team_data, output_folder_path, settings))

        if ("Schedule" in data_to_scrape):
            promises.append(download_schedule(team_data, output_folder_path, settings))

        if ("Box Scores" in data_to_scrape):
            promises.append(download_box_scores(team_data, count, output_folder_path, settings))

        await asyncio.gather(*promises)

        if ("Stats" in data_to_scrape):
            download_stats(team_data, years, output_folder_path, settings)

    asyncio.run(download_data())

    st.write("Done!")
