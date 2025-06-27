# packliste_app.py

import streamlit as st
import datetime
import os
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
from fpdf import FPDF

# Umgebung laden
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Layout & Stil
st.set_page_config(page_title="Reise-Packlisten Generator", layout="centered")

st.image("Instant Article Logo 1.png", width=100)

# Stildefinitionen
st.markdown("""
    <style>
    body {
        font-family: 'Open Sans', sans-serif;
        color: #5d5d5d;
    }
    h1, h2, h3 {
        color: #40bceb;
    }
    .stButton>button {
        background-color: #40bceb;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.6em 1em;
    }
    .stButton>button:hover {
        background-color: #2fa1cf;
    }
    .stDownloadButton>button {
        background-color: #f9414f;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Logo einfügen
st.image("5534c596-5dc5-4828-a5c2-904406d88317.png", width=100)

st.title("🎒 Dein Reise-Packlisten-Generator")
st.markdown("Fülle das Formular aus und erhalte eine individuell abgestimmte Packliste.")

# Eingabefelder
st.subheader("📍 Reiseziel & Zeitraum")
reiseziel = st.text_input("Reiseziel", placeholder="z. B. Barcelona")

startdatum = st.date_input("Startdatum", value=datetime.date.today())
enddatum = st.date_input("Enddatum", value=datetime.date.today() + datetime.timedelta(days=7))
dauer = (enddatum - startdatum).days

st.subheader("👥 Anzahl der Reisenden")
erwachsene = st.number_input("Erwachsene", min_value=1, max_value=10, value=1)
kinder = st.number_input("Kinder", min_value=0, max_value=10, value=0)
haustiere = st.number_input("Haustiere", min_value=0, max_value=5, value=0)

st.subheader("🧭 Reiseart & Unterkunft")
reiseart = st.selectbox("Reiseart", ["Strand", "Stadt", "Sport", "Familie", "Business"])
unterkunft = st.selectbox("Unterkunft", ["Hotel", "Camping", "Selbstversorger"])
transportmittel = st.selectbox("Transportmittel", ["Auto", "Flugzeug", "Zug", "Bus", "Wohnmobil"])

st.subheader("🎯 Aktivitäten & Wünsche")
aktivitaeten = st.multiselect(
    "Aktivitäten",
    ["Wandern", "Schwimmen", "Sightseeing", "Radfahren", "Klettern", "Wellness", "Tauchen", "Museen", "Skifahren"]
)

besondere_wuensche = st.text_area("Besondere Hinweise", placeholder="z. B. Allergien, barrierefreie Unterkunft")

# Button zum Generieren der Packliste
if st.button("📦 Packliste generieren"):
    prompt = f"""
    Erstelle eine Packliste für folgende Reisedaten:
    - Reiseziel: {reiseziel}
    - Reisezeitraum: {startdatum} bis {enddatum} ({dauer} Tage)
    - Erwachsene: {erwachsene}, Kinder: {kinder}, Haustiere: {haustiere}
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
                    file_name=f"Packliste_{reiseziel}_{startdatum}.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Fehler bei der Packlistenerstellung: {e}")
        
