# packliste_app.py

import streamlit as st
import datetime
import os
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
from fpdf import FPDF

# Load environment variables
load_dotenv()
# Fallback: Nutze Streamlit Secrets, falls .env nicht verfügbar ist
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

st.set_page_config(page_title="Reise-Packlisten Generator", layout="centered")

# Versuche, ein Logo anzuzeigen (optional)
logo_path = "logo.png"
if os.path.exists(logo_path):
    st.image(logo_path, width=100)

# Stil und Titel
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Open Sans', sans-serif;
        background-color: #ffffff;
    }
    .main h1 { color: #40bceb; }
    .stButton button {
        background-color: #40bceb;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 6px;
        padding: 0.5em 1.2em;
    }
    .stButton button:hover {
        background-color: #329bc5;
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎒 Dein Reise-Packlisten-Generator")
st.markdown("Fülle das Formular aus und erhalte eine individuell abgestimmte Packliste.")

# Eingabefelder
st.subheader("📍 Reiseziel & Zeitraum")
reiseziel = st.text_input("Reiseziel", placeholder="z. B. Barcelona")

zeitwahl = st.radio("Wie möchtest du deinen Reisezeitraum angeben?", ["Start- und Enddatum", "Nur Monat angeben"])

if zeitwahl == "Start- und Enddatum":
    startdatum = st.date_input("Startdatum", value=datetime.date.today())
    enddatum = st.date_input("Enddatum", value=datetime.date.today() + datetime.timedelta(days=7))
    dauer = (enddatum - startdatum).days
    zeitraum_str = f"{startdatum} bis {enddatum} ({dauer} Tage)"
else:
    monat = st.selectbox("Monat", ["Jänner", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"])
    tage = st.number_input("Anzahl der Reisetage", min_value=1, max_value=60, value=7)
    startdatum = ""
    dauer = tage
    zeitraum_str = f"{monat}, {tage} Tage"

st.subheader("👥 Anzahl der Reisenden")
erwachsene = st.number_input("Erwachsene", min_value=1, max_value=10, value=1)
kinder = st.number_input("Kinder (inkl. Babys)", min_value=0, max_value=10, value=0)
babys = st.number_input("Davon Babys", min_value=0, max_value=kinder, value=0)
haustiere = st.number_input("Haustiere", min_value=0, max_value=5, value=0)

st.subheader("🧭 Reiseart & Unterkunft")
reiseart = st.selectbox("Reiseart", ["Strand", "Stadt", "Sport", "Familie", "Business", "Romantik / Flittern"])
unterkunft = st.selectbox("Unterkunft", ["Hotel", "Camping", "Selbstversorger"])
transportmittel = st.selectbox("Transportmittel", ["Auto", "Flugzeug", "Zug", "Bus", "Wohnmobil"])

st.subheader("🎯 Aktivitäten & Wünsche")
with st.expander("Aktivitäten auswählen"):
    aktivitaeten = st.multiselect(
        "Aktivitäten",
        ["Wandern", "Schwimmen", "Sightseeing", "Radfahren", "Klettern", "Wellness", "Tauchen", "Museen", "Skifahren"]
    )

with st.expander("Besondere Hinweise"):
    besondere_wuensche = st.text_area("Besondere Hinweise", placeholder="z. B. Allergien, barrierefreie Unterkunft")

# Button zum Generieren der Packliste
if st.button("📦 Packliste generieren"):
    prompt = f"""
    Erstelle eine Packliste für folgende Reisedaten:
    - Reiseziel: {reiseziel}
    - Reisezeitraum: {zeitraum_str}
    - Erwachsene: {erwachsene}, Kinder: {kinder}, davon Babys: {babys}, Haustiere: {haustiere}
    - Reiseart: {reiseart}
    - Unterkunft: {unterkunft}
    - Transportmittel: {transportmittel}
    - Aktivitäten: {', '.join(aktivitaeten)}
    - Besondere Wünsche: {besondere_wuensche}

    Gib die Packliste in klarer, stichpunktartiger Form zurück. Gruppiere ggf. nach Kategorien (Kleidung, Hygiene, Technik, Kinder, Haustiere etc.).
    Berücksichtige Wetter, Dauer und Art der Reise. Nutze dein Wissen über gängige Urlaubsregionen und sei hilfreich.
    Gib die Antwort auf Deutsch zurück.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        packliste = response.choices[0].message.content
        st.markdown("### 🧾 Deine Packliste")
        st.markdown(packliste)

        # PDF-Export
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in packliste.split("\n"):
            pdf.multi_cell(0, 10, line)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf.output(tmpfile.name)
            with open(tmpfile.name, "rb") as f:
                st.download_button(
                    label="📄 Packliste als PDF herunterladen",
                    data=f,
                    file_name=f"Packliste_{reiseziel}_{datetime.date.today()}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Fehler bei der Packlistenerstellung: {e}")
