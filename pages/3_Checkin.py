import streamlit as st
from database import get_bar_by_token, create_checkin

st.set_page_config(page_title="Checkin", page_icon="📷", layout="wide")
st.title("📷 QR-Check-in")

if "current_user" not in st.session_state or not st.session_state.current_user:
    st.warning("Bitte zuerst einloggen.")
    st.stop()

user = st.session_state.current_user

st.write("Für den Prototypen simulieren wir den QR-Scan über einen Token.")

token_input = st.text_input("QR-Token eingeben")

if st.button("Check-in bestätigen", use_container_width=True):
    token_input = token_input.strip()

    if not token_input:
        st.error("Bitte einen Token eingeben.")
    else:
        bar = get_bar_by_token(token_input)

        if not bar:
            st.error("Ungültiger QR-Token.")
        else:
            success = create_checkin(user["id"], bar["id"])

            if success:
                st.success(f"Check-in bei {bar['name']} erfolgreich. +{bar['points']} Punkte")
            else:
                st.warning(f"Du hast {bar['name']} bereits eingecheckt.")

st.divider()
st.markdown("### Demo-Tokens")

demo_tokens = [
    ("Heart Regensburg", "heart123"),
    ("Murphy's Law", "murphys123"),
    ("Barock", "barock123"),
    ("Alte Filmbühne", "film123"),
    ("Banane", "banane123"),
]

for name, token in demo_tokens:
    st.write(f"- **{name}** → `{token}`")