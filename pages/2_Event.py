import streamlit as st
from database import get_all_bars, get_checked_in_bar_ids_for_user, get_score_for_user

st.set_page_config(page_title="Event", page_icon="🍻", layout="wide")
st.title("🍻 Event")

if "current_user" not in st.session_state or not st.session_state.current_user:
    st.warning("Bitte zuerst einloggen.")
    st.stop()

user = st.session_state.current_user
bars = get_all_bars()
checked_in_bar_ids = get_checked_in_bar_ids_for_user(user["id"])
score = get_score_for_user(user["id"])

st.subheader("USO Kneipenrallye Regensburg")
st.write("Besuche Bars, scanne QR-Codes und sammle Punkte.")

c1, c2, c3 = st.columns(3)
c1.metric("Startpunkt", "Heart Regensburg")
c2.metric("Startzeit", "19:00 Uhr")
c3.metric("Punkte", score)

st.divider()
st.markdown("### Teilnehmende Bars")

for bar in bars:
    checked_in = bar["id"] in checked_in_bar_ids

    with st.container(border=True):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(f"**{bar['name']}**")
            st.caption(f"{bar['points']} Punkte")

        with col2:
            if checked_in:
                st.success("Erledigt")
            else:
                st.info("Offen")

        with col3:
            st.code(bar["token"])