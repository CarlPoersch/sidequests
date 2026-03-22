import streamlit as st
from database import get_or_create_user

st.set_page_config(page_title="Login", page_icon="👤", layout="wide")
st.title("👤 Login")

if "current_user" not in st.session_state:
    st.session_state.current_user = None

username = st.text_input("Wähle deinen Benutzernamen")

if st.button("Einloggen / Registrieren", use_container_width=True):
    username = username.strip()

    if not username:
        st.error("Bitte einen Benutzernamen eingeben.")
    else:
        user = get_or_create_user(username)
        st.session_state.current_user = user
        st.success(f"Du bist jetzt als {user['username']} eingeloggt.")
        st.rerun()

if st.session_state.current_user:
    st.info(f"Aktiver User: {st.session_state.current_user['username']}")

    if st.button("Logout", use_container_width=True):
        st.session_state.current_user = None
        st.rerun()