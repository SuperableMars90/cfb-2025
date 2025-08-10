import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
import gspread
from google.oauth2.service_account import Credentials

import streamlit as st
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -----------------------
# Google Sheets Functions
# -----------------------

def write_to_gsheet(row_data):
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
    worksheet.append_row(row_data)

def get_all_question_ids(poll_data):
    keys = []
    for main_qid, main_q in poll_data.items():
        keys.append(main_qid)
        for followups in main_q.get("followups", {}).values():
            keys.extend(followups.keys())
    return keys

def has_submitted_this_week(user_id, week):
    """Check if a given user_id already has a submission for this week."""
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
    records = worksheet.get_all_values()  # list of rows

    # Assuming first col = user_id, second col = week
    for row in records[1:]:  # skip header if present
        if len(row) >= 2 and row[0] == user_id and row[1] == str(week):
            return True
    return False

# -----------------------
# Load JSON Poll Data
# -----------------------
with open("data/current_teams.json", "r") as f:
    poll_data = json.load(f)

question_ids = get_all_question_ids(poll_data)

# -----------------------
# Login
# -----------------------
if "page" not in st.session_state:
    st.session_state.page = "login"
if "responses" not in st.session_state:
    st.session_state.responses = {}

if st.session_state.page == "login":
    st.header("Login")
    user_id = st.text_input("Enter your Player ID")
    week = st.number_input("Week Number", min_value=1, step=1)

    if st.button("Start Poll"):
        if user_id in st.secrets["player_ids"].values():
            if has_submitted_this_week(user_id, week):
                st.error(f"You have already submitted for Week {week}.")
            else:
                st.session_state.user_id = user_id
                st.session_state.week = week
                st.session_state.page = "poll"
                st.rerun()
        else:
            st.error("Invalid Player ID")

# -----------------------
# Poll Page
# -----------------------
elif st.session_state.page == "poll":
    st.header(f"Weekly Poll - Week {st.session_state.week}")

    ready_to_submit = True

    for qid, qdata in poll_data.items():
        st.subheader(qdata["text"])

        if qdata.get("type") == "multiselect":
            selections = st.multiselect(
                qdata["text"],
                qdata["options"],
                key=qid
            )
            st.session_state.responses[qid] = selections

        elif qdata.get("type") == "selectbox":
            choice = st.selectbox(
                qdata["text"],
                [""] + qdata["options"],
                key=qid
            )
            st.session_state.responses[qid] = choice

        else:
            st.error(f"Unknown question type for {qid}")

    if st.button("Submit", disabled=not ready_to_submit):
        st.session_state.responses["timestamp"] = datetime.now().isoformat()

        row = [st.session_state.get("user_id", ""), str(st.session_state.get("week", ""))]
        row += [json.dumps(st.session_state.responses.get(qid, "")) for qid in question_ids]
        row.append(st.session_state.responses.get("timestamp", ""))

        write_to_gsheet(row)

        st.success("Response recorded!")
        st.session_state.page = "login"
        st.session_state.responses = {}
