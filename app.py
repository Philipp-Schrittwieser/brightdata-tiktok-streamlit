import streamlit as st
from streamlit_autorefresh import st_autorefresh
import scrape
from datetime import datetime
import time
from db.db import get_collection
import pytz

# Tabs importieren
from tabs.tab_01_new_scrape import render_new_scrape_tab
from tabs.tab_02_finished_jobs import render_finished_jobs_tab

from datetime import timedelta

st.set_page_config(
    page_title="TikTok Creator Analytics",
    page_icon=None,
    layout="wide"
)

# MongoDB Setup
jobs = get_collection("jobs")



def get_running_jobs():
    running_jobs = jobs.find({"status": "running"})
    jobs_list = list(running_jobs)
    # Sortiere nach created_at aufsteigend (älteste zuerst)
    jobs_list.sort(key=lambda x: x.get('created_at', datetime.min))
    return {
        "count": len(jobs_list),
        "last_check": datetime.now().strftime("%H:%M:%S"),
        "jobs": jobs_list
    }

st.markdown("""
            <style>
              #MainMenu {visibility: hidden !important;}
              footer {visibility: hidden !important;}
              #stDecoration {display: none !important;}
              #stToolbar {display: none !important;}
              .stAppToolbar {display: none !important;}
              #stHeader {display: none !important;}
              .st-emotion-cache-97ja1j {display: none !important;}
              .st-emotion-cache-1dp5vir {display: none !important;}
              .st-emotion-cache-zq5wmm {display: none !important;}
              .st-emotion-cache-1p1m4ay {display: none !important;}
              .stActionButton {display: none !important;}
            }
            """, unsafe_allow_html=True)




st.markdown("""
            <style>
              #MainMenu {visibility: hidden !important;}
              footer {visibility: hidden !important;}
              #stDecoration {display: none !important;}
              #stToolbar {display: none !important;}
              .stAppToolbar {display: none !important;}
              .stButton:focus {color: white !important; }
            
              
              /* Sidebar-Anpassungen - jetzt komplett schwarz */
              .css-1d391kg {
                  background-color: #000000;
                  border-right: 1px solid #374151;
              }
              
              /* Sidebar-Header */
              .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
                  color: #ec4899;
              }
              
              /* Sidebar-Elemente deutlicher machen */
              .css-1d391kg .stAlert {
                  background-color: #111827;
                  border: 1px solid #374151;
                  color: white;
              }
              </style>
            """, unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align: center; color: white; font-size: 3rem; font-weight: 700;'>TikTok Creator Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.5rem; margin-bottom: 3rem;'>We connect Boomers with Zoomers</p>", unsafe_allow_html=True)
    
    # Anleitung
    st.markdown("""
    <div style='background-color: rgba(31, 41, 55, 0.5); border: 1px solid #4b5563; border-radius: 0.5rem; padding: 1.5rem; max-width: 42rem; margin: 0 auto 3rem auto;'>
        <h3 style='font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem; color: #ec4899; text-align: center;'>So funktioniert's:</h3>
        <ul style='color: #d1d5db; margin-left: 1rem; list-style: none;'>
            <li style='margin-bottom: 0.75rem;'><span style='color: #ec4899;'>1.</span> Gib die TikTok Handles (inkl. @) ein und wähle die Anzahl der Posts</li>
            <li style='margin-bottom: 0.75rem;'><span style='color: #ec4899;'>2.</span> Klicke auf "Analysieren" und links siehst du deinen laufenden Job</li>
            <li style='margin-bottom: 0.75rem;'><span style='color: #ec4899;'>3.</span> Sobald der Job abgeschlossen ist, wird er in fertige Jobs angezeigt</li>
            <li style='margin-bottom: 0.75rem;'><span style='color: #ec4899;'>4.</span> Du kannst den Browser jederzeit schließen, das Scraping läuft weiter</li>
            <li style='margin-bottom: 0.75rem;'><span style='color: #ec4899;'>5.</span> Ein Scraping-Job dauert ca. 3 Minuten bis 2 Stunden, variert leider stark</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - aktive Jobs anzeigen
    with st.sidebar:
        st.image("logo.png", width=240)

        st.header("Aktive Jobs")
        jobs_info = get_running_jobs()
        
        if jobs_info["count"] > 0:
            # Auto-Refresh alle 3 Sekunden
            st_autorefresh(interval=30000, key="autorefresh")

            for job in jobs_info["jobs"]:
                handles = job.get('profile_handles', [])
                if handles:
                    handles_text = ", ".join(handles)
                    st.info(f"{handles_text} - {job.get('num_posts', 0)} Posts")
                else:
                    st.info("Unbekannte Creator - {job.get('num_posts', 0)} Posts")
        else:
            st.info("Keine aktiven Jobs")
            
        # Zeit in Wien-Zeitzone umwandeln
        vienna_tz = pytz.timezone('Europe/Vienna')
        current_time = datetime.now()
        time_parts = jobs_info['last_check'].split(':')
        last_check_dt = current_time.replace(hour=int(time_parts[0]), minute=int(time_parts[1]), second=int(time_parts[2]))
        last_check_vienna = last_check_dt.astimezone(vienna_tz)
        st.markdown(f"<p style='color: #94a3b8; font-size: 0.8rem;'>Letzter Check: {last_check_vienna.strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)

    # Hauptbereich mit Tabs
    tab1, tab2 = st.tabs(["Neuen Job", "Fertige Jobs"])
    
    # Tab-Inhalte aus externen Dateien
    with tab1:
        render_new_scrape_tab()
        
    with tab2:
        render_finished_jobs_tab()

if __name__ == "__main__":
    main() 