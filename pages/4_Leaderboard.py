import streamlit as st
import pandas as pd
from database import get_leaderboard

st.set_page_config(page_title="Leaderboard", page_icon="🏆", layout="wide")
st.title("🏆 Leaderboard")

rows = get_leaderboard()

if not rows:
    st.info("Noch keine Teilnehmer vorhanden.")
    st.stop()

df = pd.DataFrame(rows)
df.columns = ["Username", "Punkte", "Bars besucht"]
df.index = df.index + 1

st.dataframe(df, use_container_width=True)

if st.session_state.get("current_user"):
    st.info(f"Du bist eingeloggt als {st.session_state.current_user['username']}.")