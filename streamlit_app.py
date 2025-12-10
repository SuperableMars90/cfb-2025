import json
import streamlit as st
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseUpload

from google.oauth2.service_account import Credentials
import io

import pandas as pd


# ---- Load your JSON file ----
with open("data/bowl_list.json", "r") as f:
    bowls = json.load(f)

# ---- Convert dict → sorted list by date ----
def parse_dt(dt):
    return datetime.fromisoformat(dt.replace("Z", "+00:00"))

sorted_items = sorted(
    bowls.items(), 
    key=lambda x: parse_dt(x[1]["date"])
)

playoffs = {
    'Orange Bowl':['Texas Tech','CFP Game 4 Winner'],
    'Rose Bowl':['Indiana','CFP Game 1 Winner'],
    'Sugar Bowl':['Georgia','CFP Game 3 Winner'],
    'Cotton Bowl':['Ohio State','CFP Game 2 Winner'],
    'Peach Bowl':['Orange Bowl Winner','Rose Bowl Winner'],
    'Fiesta Bowl':['Sugar Bowl Winner','Cotton Bowl Winner'],
    'National Championship':['Fiesta Bowl Winner','Peach Bowl Winner']
}

# ---- Streamlit Form ----
st.title("Bowl Picks")
st.header('Instructions')
st.markdown("""
<p>Make your picks for the CFB Bowl Pick 'em challenge here.</p>

<h3>Scoring</h3>
<p>
The base scoring is 1 point per correct pick. 
If you parlay picks together, you get additional points if <i>all</i> picks hit. 
If you miss one, you get 0 for all the picks. 
For each pick in the parlay, you get 1 additional point, so a 2-game parlay results in 
2 points per game (4 points total), a 3-game parlay 3 points each (9 total), etc.
</p>

<h3>Form instructions</h3>
<p>
For all the pre-set games (i.e., everything except the later rounds of the playoffs), 
simply select the team with the radio button. For the playoffs, write in the name of the 
team you think will win. If possible, please copy the team name from the prior round games 
if possible - keeping the name consistent helps me with record keeping later.<br>
For parlays, you can name them whatever you want, just be consistent. Again, copy-paste is 
preferable to ensure there aren't typos. I will combine all the picks that have the same parlay 
code together for scoring. If you leave it blank, I will score it as a single.
</p>

<p>Feel free to contact me if you have any questions.</p>
""", unsafe_allow_html=True)


with st.form("bowl_form"):
    answers = {}

    # Free-text name field
    answers["user_name"] = st.text_input("Your Name")

    st.write("---")

    # Loop through bowls in date order
    for bowl_id, info in sorted_items:

        # Group the radio + parlay code
        with st.container():
            selected = st.radio(
                label=info["name"],          # Display name
                options=info["teams"],       # Team options
                key=f"bowl_{bowl_id}"
            )

            parlay_code = st.text_input(
                label="Parlay code", 
                key=f"parlay_{bowl_id}"
            )

            answers[bowl_id] = {
                "pick": selected,
                "parlay_code": parlay_code
            }

        st.write("")  # small vertical space

    st.write("---")
    st.subheader("Playoff Picks")

    for key, pair in playoffs.items():

        display_text = f"{key}: {pair[0]} vs {pair[1]}"

        with st.container():
            text_response = st.text_input(
                label=display_text,
                key=f"playoff_resp_{key}"
            )

            parlay_code = st.text_input(
                label=f"{key} Parlay code",
                key=f"playoff_parlay_{key}"
            )

            answers[f"playoff_{key}"] = {
                "response": text_response,
                "parlay_code": parlay_code
            }

        st.write("")   # small vertical space

    submitted = st.form_submit_button("Submit Picks")

    


if submitted:
    st.success("Submitted!")
    #st.write(answers)

    # Convert dict to a compact JSON string
    results_text = json.dumps(answers, separators=(",", ":"))

    # ---- Setup Google Sheets API ----
    scopes =  [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
    creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)


    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # ---- Your Google Sheet ID ----
    SPREADSHEET_ID = "10BDWDVLFXisIyV1uH8jMuZ0EA6-ltNfxtur03qa7Qt0"
    RANGE_NAME = "Sheet1!A:B"   # two columns: timestamp | json

    # ---- Build row to insert ----
    now = datetime.utcnow().isoformat()
    row = [now, results_text]

    # ---- Append row ----
    request = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    )
    response = request.execute()

    st.success("Saved to Google Sheets!")
