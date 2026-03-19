import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="Regensburger Sidequests", page_icon="🎮", layout="wide")

# Logo Pfad definieren
LOGO_PATH = Path("sidequests_logo.png")

# -----------------------------
# Demo data + state bootstrap
# -----------------------------
if "quests" not in st.session_state:
    now = datetime.now()
    st.session_state.quests = [
        {
            "id": 1,
            "title": "Sunset Sidequest an der Donau",
            "description": "Treffpunkt am Donauufer, kurz abschalten, quatschen und den Sonnenuntergang anschauen.",
            "category": "Social",
            "location": "Donauufer Regensburg",
            "start_time": now + timedelta(hours=2),
            "max_people": 6,
            "participants": ["Carl", "Lena"],
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
            "start_time": now + timedelta(days=1, hours=1),
            "max_people": 8,
            "participants": ["Tom", "Sarah", "Jan"],
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


# -----------------------------
# Helpers
# -----------------------------
def get_next_id() -> int:
    if not st.session_state.quests:
        return 1
    return max(q["id"] for q in st.session_state.quests) + 1


def join_quest(quest_id: int):
    username = st.session_state.username.strip() or "Gast"
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


def leave_quest(quest_id: int):
    username = st.session_state.username.strip() or "Gast"
    for quest in st.session_state.quests:
        if quest["id"] == quest_id:
            if username in quest["participants"]:
                quest["participants"].remove(username)
            if quest_id in st.session_state.joined_quests:
                st.session_state.joined_quests.remove(quest_id)
            st.toast("Du hast die Sidequest verlassen.")
            return


def quest_card(quest: dict):
    spots_left = quest["max_people"] - len(quest["participants"])
    joined = quest["id"] in st.session_state.joined_quests or st.session_state.username in quest["participants"]

    with st.container(border=True):
        top_left, top_right = st.columns([4, 1])
        with top_left:
            st.subheader(f"🎯 {quest['title']}")
            st.caption(f"{quest['quest_type']} · {quest['category']} · erstellt von {quest['creator']}")
        with top_right:
            st.markdown(f"### {quest['reward']}")

        st.write(quest["description"])

        a, b, c, d = st.columns(4)
        a.metric("Ort", quest["location"])
        b.metric("Start", quest["start_time"].strftime("%d.%m. %H:%M"))
        c.metric("Teilnehmer", f"{len(quest['participants'])}/{quest['max_people']}")
        d.metric("Frei", spots_left)

        st.write("**Bereits dabei:** " + ", ".join(quest["participants"]))

        btn1, btn2, _ = st.columns([1, 1, 3])
        with btn1:
            if joined:
                st.button("Verlassen", key=f"leave_{quest['id']}", use_container_width=True, on_click=leave_quest, args=(quest["id"],))
            else:
                st.button("Annehmen", key=f"join_{quest['id']}", use_container_width=True, on_click=join_quest, args=(quest["id"],))
        with btn2:
            if st.button("Details", key=f"details_{quest['id']}", use_container_width=True):
                st.info(
                    f"Quest-ID: {quest['id']}\n\n"
                    f"Beschreibung: {quest['description']}\n\n"
                    f"Typ: {quest['quest_type']}\n"
                    f"Kategorie: {quest['category']}\n"
                    f"Ort: {quest['location']}\n"
                    f"Start: {quest['start_time'].strftime('%d.%m.%Y %H:%M')}\n"
                    f"Belohnung: {quest['reward']}"
                )


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("🎮 Sidequests")
    st.text_input("Dein Name", key="username")
    st.metric("Deine XP", st.session_state.xp)
    level = st.session_state.xp // 100 + 1
    st.metric("Level", level)
    st.divider()

    st.markdown("**Filter**")
    st.session_state.filter_category = st.selectbox(
        "Kategorie",
        ["Alle", "Social", "Study", "Food", "Sport", "Nightlife", "Business"],
        index=["Alle", "Social", "Study", "Food", "Sport", "Nightlife", "Business"].index(st.session_state.filter_category),
    )

    quest_type_filter = st.radio("Quest-Typ", ["Alle", "Privat", "Business"], horizontal=False)
    only_open = st.checkbox("Nur Quests mit freien Plätzen", value=False)
    st.divider()
    st.caption("Prototyp für Regensburger Sidequests – Fokus auf Feed, Erstellen und Joinen.")


# -----------------------------
# Header
# -----------------------------
col1, col2 = st.columns([1, 3])

with col1:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=120)

with col2:
    st.title("Regensburger Sidequests")
    st.markdown("**Finde spontane Mini-Missionen in deiner Stadt**")

st.divider()

hero1, hero2, hero3 = st.columns(3)
hero1.metric("Aktive Quests", len(st.session_state.quests))
hero2.metric("Beigetreten", len(st.session_state.joined_quests))
hero3.metric("Business-Quests", sum(1 for q in st.session_state.quests if q["quest_type"] == "Business"))

feed_tab, create_tab, my_tab = st.tabs(["🔍 Quest Feed", "➕ Sidequest erstellen", "👤 Meine Sidequests"])


# -----------------------------
# Feed tab
# -----------------------------
with feed_tab:
    quests = st.session_state.quests[:]

    if st.session_state.filter_category != "Alle":
        if st.session_state.filter_category == "Business":
            quests = [q for q in quests if q["quest_type"] == "Business"]
        else:
            quests = [q for q in quests if q["category"] == st.session_state.filter_category]

    if quest_type_filter != "Alle":
        quests = [q for q in quests if q["quest_type"] == quest_type_filter]

    if only_open:
        quests = [q for q in quests if len(q["participants"]) < q["max_people"]]

    quests = sorted(quests, key=lambda x: x["start_time"])

    search = st.text_input("Suche nach Titel, Ort oder Beschreibung")
    if search:
        search_lower = search.lower()
        quests = [
            q for q in quests
            if search_lower in q["title"].lower()
            or search_lower in q["location"].lower()
            or search_lower in q["description"].lower()
        ]

    if not quests:
        st.warning("Keine passenden Sidequests gefunden.")
    else:
        for quest in quests:
            quest_card(quest)
            st.write("")


# -----------------------------
# Create tab
# -----------------------------
with create_tab:
    st.subheader("Neue Sidequest erstellen")
    st.write("Erstelle eine spontane Mission für Privatpersonen oder als Business.")

    with st.form("create_quest_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        title = col1.text_input("Titel*")
        category = col2.selectbox("Kategorie*", ["Social", "Study", "Food", "Sport", "Nightlife"])

        description = st.text_area("Beschreibung*")

        col3, col4 = st.columns(2)
        location = col3.text_input("Ort*")
        quest_type = col4.selectbox("Quest-Typ*", ["Privat", "Business"])

        col5, col6, col7 = st.columns(3)
        start_date = col5.date_input("Datum", value=datetime.now().date())
        start_time = col6.time_input("Uhrzeit", value=(datetime.now() + timedelta(hours=2)).time().replace(second=0, microsecond=0))
        max_people = col7.number_input("Max. Teilnehmer", min_value=2, max_value=50, value=6, step=1)

        reward = st.text_input("Belohnung", placeholder="z. B. 20 XP oder Free Drink + 50 XP")

        submitted = st.form_submit_button("Sidequest veröffentlichen", use_container_width=True)

        if submitted:
            if not title.strip() or not description.strip() or not location.strip():
                st.error("Bitte fülle alle Pflichtfelder aus.")
            else:
                new_quest = {
                    "id": get_next_id(),
                    "title": title.strip(),
                    "description": description.strip(),
                    "category": category,
                    "location": location.strip(),
                    "start_time": datetime.combine(start_date, start_time),
                    "max_people": int(max_people),
                    "participants": [],
                    "creator": st.session_state.username.strip() or "Gast",
                    "quest_type": quest_type,
                    "reward": reward.strip() if reward.strip() else "15 XP",
                }
                st.session_state.quests.append(new_quest)
                st.session_state.xp += 10
                st.success("Deine Sidequest wurde erstellt. +10 XP")
                st.rerun()


# -----------------------------
# My quests tab
# -----------------------------
with my_tab:
    st.subheader("Meine Übersicht")

    created = [q for q in st.session_state.quests if q["creator"] == (st.session_state.username.strip() or "Gast")]
    joined = [q for q in st.session_state.quests if (st.session_state.username.strip() or "Gast") in q["participants"]]

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Von dir erstellt")
        if not created:
            st.info("Du hast noch keine Sidequests erstellt.")
        else:
            for q in created:
                with st.container(border=True):
                    st.write(f"**{q['title']}**")
                    st.caption(f"{q['category']} · {q['quest_type']} · {q['start_time'].strftime('%d.%m. %H:%M')}")
                    st.write(q['location'])

    with c2:
        st.markdown("### Beigetreten")
        if not joined:
            st.info("Du bist noch keiner Sidequest beigetreten.")
        else:
            for q in joined:
                with st.container(border=True):
                    st.write(f"**{q['title']}**")
                    st.caption(f"{q['category']} · {q['quest_type']} · {q['start_time'].strftime('%d.%m. %H:%M')}")
                    st.write(q['location'])

    st.divider()
    st.markdown("### Nächste sinnvolle Ausbaustufen")
    st.markdown(
        "- echtes Login\n"
        "- Datenbank statt Session State\n"
        "- Kartenansicht\n"
        "- Business-Dashboard\n"
        "- Verlässlichkeitsscore / XP-System\n"
        "- Freigabe/Moderation für Quests"
    )