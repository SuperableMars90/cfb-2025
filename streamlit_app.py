import json
import streamlit as st
from datetime import datetime

# ---- Load your JSON file ----
with open("bowls.json", "r") as f:
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
    st.success("Submitted!")
    st.write(answers)
