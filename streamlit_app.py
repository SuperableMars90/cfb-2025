import json
import streamlit as st
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
import pandas as pd

scopes =  [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
service = build('drive', 'v3', credentials=credentials)
folder_id = '1QGc6bgTHEmAsnZnREvkGmXQ_6x0KRhxh'


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

# ---- Streamlit Form ----
st.title("Bowl Picks")

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

    submitted = st.form_submit_button("Submit Picks")

if submitted:
    st.success('Submitted!')
    st.write(answers)
    filename = f"{answers['user_name']}_picks.json"
    file_metadata = {
        'name':filename,
        'parents':[folder_id]
    }

    media = MediaFileUpload(file_name, mimetype='text/plain')

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()