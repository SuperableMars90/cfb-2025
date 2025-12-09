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

import streamlit as st
import json

# ----------------
# Load your single JSON file
# ----------------
with open("data/bowl_list.json") as f:
    data = json.load(f)

# Top-level keys are players
#players = list(data.keys())

# ----------------
# Step 1: Pick person
# ----------------
st.title("Bowl Pick 'em Survey")

person = st.text_input(label="Who are you?")

if person:
    st.write(f"Welcome, **{person}**! Please make your picks.")

    answers = {}
    person_questions = data   # <-- dictionary of categories for that person

    # ----------------
    # Step 2: Iterate questions
    # ----------------
    # Unordered

    #for q_key, opts in person_questions.items():
    for q_key in data:
        opts = data[q_key]['teams']
        st.markdown(f"### {q_key}")


    # ----------------
    # Step 3: Submit
    # ----------------
    if st.button("Submit"):
        # Build row: timestamp, person, then answers in fixed order
        row = [datetime.now().isoformat(), person]
        for q_key in QUESTION_ORDER:
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