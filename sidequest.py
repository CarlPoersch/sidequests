import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Regensburger Sidequests", page_icon="🎮", layout="wide")

# ---------------------------------
# Config
# ---------------------------------
LOGO_PATH = Path("sidequests_logo.png")

DEFAULT_LOCATIONS = {
    "Donauufer": {"lat": 49.0134, "lon": 12.1016},
    "OTH Bibliothek": {"lat": 49.0148, "lon": 12.0965},
    "Altstadt Regensburg": {"lat": 49.0194, "lon": 12.0972},
    "Stadtamhof": {"lat": 49.0246, "lon": 12.1003},
    "Bismarckplatz": {"lat": 49.0186, "lon": 12.0904},
    "Hauptbahnhof Regensburg": {"lat": 49.0118, "lon": 12.0997},
}

# ---------------------------------
# Session State Init
# ---------------------------------
if "quests" not in st.session_state:
    now = datetime.now()
    st.session_state.quests = [
        {
            "id": 1,
            "title": "Sunset Sidequest an der Donau",
            "description": "Kurz abschalten, quatschen und den Sonnenuntergang anschauen.",
            "category": "Social",
            "location": "Donauufer",
            "lat": 49.0134,
            "lon": 12.1016,
            "start_time": now + timedelta(hours=2),
            "max_people": 6,
            "participants": ["Lena", "Tom"],
            "creator": "Mia",
            "quest_type": "Privat",
            "reward": "20 XP",
        },
        {
            "id": 2,
            "title": "Bib Focus Sprint 45",
            "description": "45 Minuten fokussiert lernen, danach kurzer Kaffee-Check-in.",
            "category": "Study",
            "location": "OTH Bibliothek",
            "lat": 49.0148,
            "lon": 12.0965,
            "start_time": now + timedelta(hours=4),
            "max_people": 4,
            "participants": ["Noah"],
            "creator": "Carl",
            "quest_type": "Privat",
            "reward": "35 XP",
        },
        {
            "id": 3,
            "title": "Burger Quest im Testladen",
            "description": "Neuen Burger testen und direkt Feedback geben. Erste 5 bekommen ein Getränk dazu.",
            "category": "Food",
            "location": "Altstadt Regensburg",
            "lat": 49.0194,
            "lon": 12.0972,
            "start_time": now + timedelta(days=1, hours=1),
            "max_people": 8,
            "participants": ["Jan", "Sarah", "Max"],
            "creator": "BurgerLab",
            "quest_type": "Business",
            "reward": "Free Drink + 50 XP",
        },
    ]

if "joined_quests" not in st.session_state:
    st.session_state.joined_quests = []

if "username" not in st.session_state:
    st.session_state.username = "Carl"

if "xp" not in st.session_state:
    st.session_state.xp = 120

if "filter_category" not in st.session_state:
    st.session_state.filter_category = "Alle"

if "quest_type_filter" not in st.session_state:
    st.session_state.quest_type_filter = "Alle"

if "only_open" not in st.session_state:
    st.session_state.only_open = False


# ---------------------------------
# Helper Functions
# ---------------------------------
def get_next_id():
    if not st.session_state.quests:
        return 1
    return max(q["id"] for q in st.session_state.quests) + 1


def get_display_name():
    return st.session_state.username.strip() or "Gast"


def join_quest(quest_id):
    username = get_display_name()

    for quest in st.session_state.quests:
        if quest["id"] == quest_id:
            if username in quest["participants"]:
                st.toast("Du bist dieser Sidequest schon beigetreten.")
                return
            if len(quest["participants"]) >= quest["max_people"]:
                st.toast("Diese Sidequest ist leider schon voll.")
                return

            quest["participants"].append(username)

            if quest_id not in st.session_state.joined_quests:
                st.session_state.joined_quests.append(quest_id)

            st.session_state.xp += 15
            st.toast("Sidequest angenommen. +15 XP")
            return


def leave_quest(quest_id):
    username = get_display_name()

    for quest in st.session_state.quests:
        if quest["id"] == quest_id:
            if username in quest["participants"]:
                quest["participants"].remove(username)

            if quest_id in st.session_state.joined_quests:
                st.session_state.joined_quests.remove(quest_id)

            st.toast("Du hast die Sidequest verlassen.")
            return


def get_location_coords(location_name):
    if location_name in DEFAULT_LOCATIONS:
        return DEFAULT_LOCATIONS[location_name]["lat"], DEFAULT_LOCATIONS[location_name]["lon"]
    return 49.0134, 12.1016


def render_quest_card(quest):
    username = get_display_name()
    joined = username in quest["participants"]
    spots_left = quest["max_people"] - len(quest["participants"])

    with st.container(border=True):
        top_left, top_right = st.columns([4, 1])

        with top_left:
            st.subheader(f"🎯 {quest['title']}")
            st.caption(
                f"{quest['quest_type']} · {quest['category']} · erstellt von {quest['creator']}"
            )

        with top_right:
            st.markdown(f"### {quest['reward']}")

        st.write(quest["description"])

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ort", quest["location"])
        c2.metric("Start", quest["start_time"].strftime("%d.%m. %H:%M"))
        c3.metric("Teilnehmer", f"{len(quest['participants'])}/{quest['max_people']}")
        c4.metric("Frei", spots_left)

        st.write("**Bereits dabei:** " + ", ".join(quest["participants"]) if quest["participants"] else "**Bereits dabei:** Noch niemand")

        b1, b2 = st.columns(2)

        with b1:
            if joined:
                st.button(
                    "Verlassen",
                    key=f"leave_{quest['id']}",
                    use_container_width=True,
                    on_click=leave_quest,
                    args=(quest["id"],),
                )
            else:
                st.button(
                    "Annehmen",
                    key=f"join_{quest['id']}",
                    use_container_width=True,
                    on_click=join_quest,
                    args=(quest["id"],),
                )

        with b2:
            st.button(
                "Quest-ID anzeigen",
                key=f"details_{quest['id']}",
                use_container_width=True,
                help=f"Quest-ID: {quest['id']}",
            )


def get_filtered_quests(search_term=""):
    quests = st.session_state.quests[:]

    if st.session_state.filter_category != "Alle":
        if st.session_state.filter_category == "Business":
            quests = [q for q in quests if q["quest_type"] == "Business"]
        else:
            quests = [q for q in quests if q["category"] == st.session_state.filter_category]

    if st.session_state.quest_type_filter != "Alle":
        quests = [q for q in quests if q["quest_type"] == st.session_state.quest_type_filter]

    if st.session_state.only_open:
        quests = [q for q in quests if len(q["participants"]) < q["max_people"]]

    if search_term.strip():
        s = search_term.lower().strip()
        quests = [
            q for q in quests
            if s in q["title"].lower()
            or s in q["location"].lower()
            or s in q["description"].lower()
        ]

    quests = sorted(quests, key=lambda x: x["start_time"])
    return quests


# ---------------------------------
# Sidebar
# ---------------------------------
with st.sidebar:
    st.title("🎮 Sidequests")
    st.text_input("Dein Name", key="username")

    st.metric("Deine XP", st.session_state.xp)
    level = st.session_state.xp // 100 + 1
    st.metric("Level", level)

    progress_in_level = (st.session_state.xp % 100) / 100
    st.progress(progress_in_level)

    st.divider()
    st.markdown("**Filter**")

    st.session_state.filter_category = st.selectbox(
        "Kategorie",
        ["Alle", "Social", "Study", "Food", "Sport", "Nightlife", "Business"],
        index=["Alle", "Social", "Study", "Food", "Sport", "Nightlife", "Business"].index(
            st.session_state.filter_category
        ),
    )

    st.session_state.quest_type_filter = st.radio(
        "Quest-Typ",
        ["Alle", "Privat", "Business"],
        index=["Alle", "Privat", "Business"].index(st.session_state.quest_type_filter),
    )

    st.session_state.only_open = st.checkbox(
        "Nur Quests mit freien Plätzen",
        value=st.session_state.only_open,
    )

    st.divider()
    st.caption("Prototyp für Regensburger Sidequests")


# ---------------------------------
# Header
# ---------------------------------
header_col1, header_col2 = st.columns([1, 3])

with header_col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)

with header_col2:
    st.title("Regensburger Sidequests")
    st.markdown("**Finde spontane Mini-Missionen in deiner Stadt**")

st.divider()

# ---------------------------------
# Top Metrics
# ---------------------------------
m1, m2, m3 = st.columns(3)
m1.metric("Aktive Quests", len(st.session_state.quests))
m2.metric("Beigetreten", len([q for q in st.session_state.quests if get_display_name() in q["participants"]]))
m3.metric("Business-Quests", len([q for q in st.session_state.quests if q["quest_type"] == "Business"]))

# ---------------------------------
# Tabs
# ---------------------------------
feed_tab, create_tab, my_tab = st.tabs(
    ["🔍 Quest Feed", "➕ Sidequest erstellen", "👤 Meine Sidequests"]
)

# ---------------------------------
# Feed Tab
# ---------------------------------
with feed_tab:
    st.subheader("🗺️ Sidequests Map")

    search = st.text_input("Suche nach Titel, Ort oder Beschreibung")
    filtered_quests = get_filtered_quests(search)

    map_center = [49.0134, 12.1016]
    if filtered_quests:
        map_center = [filtered_quests[0]["lat"], filtered_quests[0]["lon"]]

    m = folium.Map(location=map_center, zoom_start=13)

    for quest in filtered_quests:
        popup_text = (
            f"<b>{quest['title']}</b><br>"
            f"{quest['category']} · {quest['quest_type']}<br>"
            f"{quest['location']}<br>"
            f"{quest['start_time'].strftime('%d.%m.%Y %H:%M')}"
        )

        marker_color = "blue"
        if quest["quest_type"] == "Business":
            marker_color = "green"
        elif quest["category"] == "Food":
            marker_color = "red"
        elif quest["category"] == "Study":
            marker_color = "purple"

        folium.Marker(
            location=[quest["lat"], quest["lon"]],
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=quest["title"],
            icon=folium.Icon(color=marker_color, icon="flag"),
        ).add_to(m)

    st_folium(m, width=None, height=500)

    st.subheader("📋 Sidequests")

    if not filtered_quests:
        st.warning("Keine passenden Sidequests gefunden.")
    else:
        for quest in filtered_quests:
            render_quest_card(quest)
            st.write("")

# ---------------------------------
# Create Tab
# ---------------------------------
with create_tab:
    st.subheader("Neue Sidequest erstellen")
    st.write("Erstelle eine spontane Mission für Privatpersonen oder als Business.")

    with st.form("create_quest_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        title = c1.text_input("Titel*")
        category = c2.selectbox("Kategorie*", ["Social", "Study", "Food", "Sport", "Nightlife"])

        description = st.text_area("Beschreibung*")

        c3, c4 = st.columns(2)
        location = c3.selectbox("Ort*", list(DEFAULT_LOCATIONS.keys()))
        quest_type = c4.selectbox("Quest-Typ*", ["Privat", "Business"])

        c5, c6, c7 = st.columns(3)
        start_date = c5.date_input("Datum", value=datetime.now().date())
        start_time = c6.time_input(
            "Uhrzeit",
            value=(datetime.now() + timedelta(hours=2)).time().replace(second=0, microsecond=0),
        )
        max_people = c7.number_input("Max. Teilnehmer", min_value=2, max_value=50, value=6, step=1)

        reward = st.text_input("Belohnung", placeholder="z. B. 20 XP oder Free Drink + 50 XP")

        submitted = st.form_submit_button("Sidequest veröffentlichen", use_container_width=True)

        if submitted:
            if not title.strip() or not description.strip() or not location.strip():
                st.error("Bitte fülle alle Pflichtfelder aus.")
            else:
                lat, lon = get_location_coords(location)

                new_quest = {
                    "id": get_next_id(),
                    "title": title.strip(),
                    "description": description.strip(),
                    "category": category,
                    "location": location,
                    "lat": lat,
                    "lon": lon,
                    "start_time": datetime.combine(start_date, start_time),
                    "max_people": int(max_people),
                    "participants": [],
                    "creator": get_display_name(),
                    "quest_type": quest_type,
                    "reward": reward.strip() if reward.strip() else "15 XP",
                }

                st.session_state.quests.append(new_quest)
                st.session_state.xp += 10
                st.success("Deine Sidequest wurde erstellt. +10 XP")
                st.rerun()

# ---------------------------------
# My Tab
# ---------------------------------
with my_tab:
    st.subheader("Meine Übersicht")

    username = get_display_name()

    created = [q for q in st.session_state.quests if q["creator"] == username]
    joined = [q for q in st.session_state.quests if username in q["participants"]]

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown("### Von dir erstellt")
        if not created:
            st.info("Du hast noch keine Sidequests erstellt.")
        else:
            for q in created:
                with st.container(border=True):
                    st.write(f"**{q['title']}**")
                    st.caption(
                        f"{q['category']} · {q['quest_type']} · {q['start_time'].strftime('%d.%m. %H:%M')}"
                    )
                    st.write(q["location"])

    with right_col:
        st.markdown("### Beigetreten")
        if not joined:
            st.info("Du bist noch keiner Sidequest beigetreten.")
        else:
            for q in joined:
                with st.container(border=True):
                    st.write(f"**{q['title']}**")
                    st.caption(
                        f"{q['category']} · {q['quest_type']} · {q['start_time'].strftime('%d.%m. %H:%M')}"
                    )
                    st.write(q["location"])

    st.divider()
    st.markdown("### Nächste sinnvolle Ausbaustufen")
    st.markdown(
        "- echtes Login\n"
        "- Datenbank statt Session State\n"
        "- automatische Geocoding-Orteingabe\n"
        "- Business-Dashboard\n"
        "- Verlässlichkeitsscore / XP-System\n"
        "- Freigabe/Moderation für Quests"
    )