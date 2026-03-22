import streamlit as st
from pathlib import Path
from database import init_db, seed_bars

st.set_page_config(page_title="Sidequests Rallye", page_icon="🍻", layout="wide")

LOGO_PATH = Path("sidequests_logo.png")

init_db()
seed_bars()

if "current_user" not in st.session_state:
    st.session_state.current_user = None

st.title("Sidequests Rallye")

col1, col2 = st.columns([1, 4])

with col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=110)

with col2:
    st.subheader("Event-Challenge Plattform")
    st.write("Multipage-Prototyp für Kneipenrallyes, QR-Check-ins und Leaderboards.")

st.divider()

if st.session_state.current_user:
    st.success(f"Eingeloggt als: {st.session_state.current_user['username']}")
else:
    st.warning("Noch nicht eingeloggt. Öffne links zuerst die Login-Seite.")

st.markdown("### Navigation")
st.write("Nutze links die Seiten:")
st.write("- Login")
st.write("- Event")
st.write("- Checkin")
st.write("- Leaderboard")