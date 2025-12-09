import json
import streamlit as st
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

#def write_to_gsheet(sheet_name, worksheet_name="Sheet1"):
#    scopes = [
#       "https://www.googleapis.com/auth/spreadsheets",
#        "https://www.googleapis.com/auth/drive"
#    ]
#    credentials = Credentials.from_service_account_info(
#        st.secrets["gcp_service_account"], scopes=scope
#    )
#    client = gspread.authorize(credentials)
#    sheet = client.open_by_key("10BDWDVLFXisIyV1uH8jMuZ0EA6-ltNfxtur03qa7Qt0")
#    worksheet = sheet.sheet1
#    worksheet.append_row(row_data)

def get_sheet(sheet_name, worksheet_name="Sheet1"):
    scopes =  [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    client = gspread.authorize(credentials)
    sheet = client.open_by_key("10BDWDVLFXisIyV1uH8jMuZ0EA6-ltNfxtur03qa7Qt0")
    return sheet



def ensure_header(sheet, bowls_sorted):
    try:
        existing = sheet.row_values(1)
    except:
        test = 'Test'
    if existing:
        return existing  # Already exists

    header = ["user_name"]

    for bowl_id, info in bowls_sorted:
        header.append(info["name"])                   # pick column
        header.append(f"{info['name']} — Parlay")     # parlay column

    sheet.append_row(header)
    return header

def append_response(sheet, answers, bowls_sorted):
    row = [answers["user_name"]]

    for bowl_id, info in bowls_sorted:
        pick = answers[bowl_id]["pick"]
        parlay = answers[bowl_id]["parlay_code"]
        row.append(pick)
        row.append(parlay)

    sheet.append_row(row)


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

if st.button("Submit Picks"):
        # Build row: timestamp, person, then answers in fixed order
        row = [datetime.now().isoformat(), answers["user_name"]]
        for q_key in sorted_items:
            if q_key not in answers:
                row.append("")  # blank if missing
            else:
                val = answers[q_key]
                if isinstance(val, list):  # multiselect answers
                    row.append(", ".join(val))
                else:
                    row.append(val)
        scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scope
        )
        client = gspread.authorize(credentials)

        sheet = client.open_by_key("1RcC3Sv5NuD7isPRxac121rYwAseUlONyOv_cMLgD1Ak")
        worksheet = sheet.sheet1
        worksheet.append_row(row)
        st.success("Your picks have been submitted!")
        st.json(answers)