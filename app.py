from pathlib import Path

import pandas as pd
import streamlit as st

from incident_lab.database import reset_database
from incident_lab.incidents import INCIDENTS, correct, investigate, reproduce

DB = Path("data/demo.db")
st.set_page_config(page_title="SQL Incident Lab", page_icon="🔎", layout="wide")
st.title("SQL Incident Investigation Lab")
st.caption("Safe, disposable incident reproduction for application-support practice")

if not DB.exists():
    reset_database(DB)

left, right = st.columns([1, 2])
with left:
    selected = st.selectbox("Incident", list(INCIDENTS), format_func=lambda key: INCIDENTS[key].title)
    incident = INCIDENTS[selected]
    st.metric("Scenario", f"{list(INCIDENTS).index(selected) + 1} / {len(INCIDENTS)}")
    if st.button("Reproduce safely", type="primary"):
        st.success(reproduce(DB, selected))
    if st.button("Apply correction"):
        correct(DB, selected)
        st.success("Correction applied where the local simulation supports it.")
    if st.button("Reset disposable database"):
        reset_database(DB)
        st.success("Database restored to its clean seed state.")

with right:
    st.subheader(incident.title)
    symptom, root, prevention = st.tabs(["Symptom", "Root cause", "Prevention"])
    symptom.write(incident.symptom)
    root.write(incident.root_cause)
    prevention.write(incident.prevention)
    st.code(incident.investigation_sql, language="sql")
    try:
        rows = investigate(DB, selected)
        st.dataframe(pd.DataFrame(rows), width="stretch")
    except Exception as exc:
        st.error(f"Investigation query failed safely: {exc}")

