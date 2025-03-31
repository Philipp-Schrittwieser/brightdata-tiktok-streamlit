import streamlit as st
import scrape
from datetime import datetime
import time
import threading
from db.db import get_collection

# Tabs importieren
from tabs.tab_01_new_scrape import render_new_scrape_tab
from tabs.tab_02_finished_jobs import render_finished_jobs_tab


# MongoDB Setup
jobs = get_collection("jobs")

st.set_page_config(
    page_title="TikTok Creator Analytics",
    page_icon=None,
    layout="wide"
)

st.markdown("""
            <style>
              #MainMenu {visibility: hidden;}
              footer {visibility: hidden;}
              #stDecoration {display: none;}
              #stToolbar {display: none;}
              .stAppToolbar {display: none;}
              #stHeader {display: none;}
            """, unsafe_allow_html=True)



# Job Checker Funktion
def check_running_jobs():
    while True:
        running_jobs = jobs.find({"status": "running"})
        for job in running_jobs:
            status = scrape.check_status(job['snapshot_id'])
            if 'message' in status:
                jobs.update_one(
                    {'_id': job['_id']},
                    {'$set': {
                        'status': 'completed',
                        'completed_at': datetime.now()
                    }}
                )
        time.sleep(30)  # 30 Sekunden warten

st.markdown("""
            <style>
              #MainMenu {visibility: hidden;}
              footer {visibility: hidden;}
              #stDecoration {display: none;}
              #stToolbar {display: none;}
              .stAppToolbar {display: none;}
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
    # Start Job Checker wenn noch nicht gestartet
    if 'job_checker_running' not in st.session_state:
        thread = threading.Thread(target=check_running_jobs, daemon=True)
        thread.start()
        st.session_state.job_checker_running = True
    
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
            <li style='margin-bottom: 0.75rem;'><span style='color: #ec4899;'>4.</span> Du kannst den Browser oder Tab jederzeit schließen - der Job läuft weiter</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - aktive Jobs anzeigen
    with st.sidebar:
        st.image("logo.png", width=240)

        st.header("Aktive Jobs")
        running_jobs = jobs.find({"status": "running"}).sort('created_at', -1)
        running_jobs_list = list(running_jobs)
        
        if len(running_jobs_list) == 0:
            st.info("Keine aktiven Jobs")
        else:
            for job in running_jobs_list:
                # Anpassung für mehrere Handles
                if 'profile_handles' in job:
                    handle_count = len(job['profile_handles'])
                    handles_text = f"{handle_count} Profile" if handle_count > 1 else job['profile_handles'][0][:8]
                else:
                    handles_text = job.get('profile_handle', job.get('profile_url', 'Unbekannt'))[:8]
                
                st.info(f"{job['num_posts']} Posts von {handles_text}... läuft")

    # Hauptbereich mit Tabs
    tab1, tab2 = st.tabs(["Neuer Scrape", "Fertige Jobs"])
    
    # Tab-Inhalte aus externen Dateien
    with tab1:
        render_new_scrape_tab()
        
    with tab2:
        render_finished_jobs_tab()

if __name__ == "__main__":
    main() 