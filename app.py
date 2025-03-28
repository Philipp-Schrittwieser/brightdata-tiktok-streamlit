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

st.set_page_config(
    page_title="TikTok Scraper",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Start Job Checker wenn noch nicht gestartet
    if 'job_checker_running' not in st.session_state:
        thread = threading.Thread(target=check_running_jobs, daemon=True)
        thread.start()
        st.session_state.job_checker_running = True
    
    st.title("TikTok Scraper")
    
    # Sidebar - aktive Jobs anzeigen
    with st.sidebar:
        st.header("Aktive Jobs")
        running_jobs = jobs.find({"status": "running"}).sort('created_at', -1)
        running_jobs_list = list(running_jobs)
        
        if len(running_jobs_list) == 0:
            st.info("Keine aktiven Jobs")
        else:
            for job in running_jobs_list:
                handle = job.get('profile_handle', job.get('profile_url', 'Unbekannt'))
                st.info(f"{job['num_posts']} Posts von {handle[:8]}... läuft")

    # Hauptbereich mit Tabs
    tab1, tab2 = st.tabs(["Neuer Scrape", "Fertige Jobs"])
    
    # Tab-Inhalte aus externen Dateien
    with tab1:
        render_new_scrape_tab()
        
    with tab2:
        render_finished_jobs_tab()

if __name__ == "__main__":
    main() 