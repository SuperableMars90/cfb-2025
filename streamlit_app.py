import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

with open("data/current_teams.json") as f:
    poll_data = json.load(f)
with open('data/.tokens') as f:
    tokens = json.load(f)

token = st.text_input("Enter your username:").lower()

if token:
    if token in tokens:
        st.success(f"Welcome, {tokens[token]}!")
        st.session_state["user_id"] = token
        st.session_state["user_name"] = tokens[token]
    else:
        st.error("Invalid access code.")
else:
    st.warning("Please enter your access code.")

if "responses" not in st.session_state:
    st.session_state.responses = {}

main_qid = "Player"
main_q = poll_data[main_qid]

# Insert dummy option at the top
main_options = ["-- Select a player --"] + main_q["answers"]
selected_main = st.selectbox(main_q["question"], main_options, index=0, key=main_qid)

if selected_main != "-- Select a player --":
    st.session_state.responses[main_qid] = selected_main

    followups = main_q.get("followups", {}).get(selected_main, {})
    for fqid, fqdata in followups.items():
        f_options = ["-- Select an option --"] + fqdata["answers"]
        selected_f = st.selectbox(fqdata["question"], f_options, index=0, key=fqid)
        if selected_f != "-- Select an option --":
            st.session_state.responses[fqid] = selected_f
        else:
            st.session_state.responses.pop(fqid, None)
else:
    # Clear follow-ups if main question reset
    for answer in main_q["answers"]:
        sub = main_q.get("followups", {}).get(answer, {})
        for qid in sub:
            st.session_state.responses.pop(qid, None)

# Check if all required questions are answered
ready_to_submit = main_qid in st.session_state.responses
if ready_to_submit:
    followups = main_q.get("followups", {}).get(st.session_state.responses[main_qid], {})
    for fqid in followups:
        if fqid not in st.session_state.responses:
            ready_to_submit = False
            break

if st.button("Submit", disabled=not ready_to_submit):
    st.session_state.responses["timestamp"] = datetime.now().isoformat()
    df = pd.DataFrame([st.session_state.responses])
    df.to_csv("data/picks.csv", mode="a", index=False, header=not os.path.exists("results.csv"))
    st.success("Response recorded!")

    # Reset state for next submission
    for key in list(st.session_state.responses.keys()):
        st.session_state.pop(key)