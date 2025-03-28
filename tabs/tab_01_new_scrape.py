import streamlit as st
import scrape
from datetime import datetime
from db.db import get_collection

# MongoDB Setup
jobs = get_collection("jobs")

def render_new_scrape_tab():
    st.header("Neuen Scrape starten")
    
    # TikTok Handle Eingabe 
    tiktok_handle = st.text_input("TikTok Handle", "@marswalk")
    
    # Validierung
    if not tiktok_handle.startswith('@'):
        st.error("Der Handle muss mit @ beginnen")
        is_valid = False
    else:
        is_valid = True
    
    # Nur noch Anzahl der Posts wählbar
    num_posts = st.number_input("Anzahl Posts", min_value=1, value=10)
    
    # Start Button
    if st.button("Start Scraping", type="primary") and is_valid:
        with st.spinner("Starte Scraping..."):
            try:
                tiktok_url = f"https://www.tiktok.com/{tiktok_handle}"
                # # TikTok URL zusammenbauen
                # tiktok_handles_list = tiktok_handle.split(" ")
                # tiktok_urls = []
                # for handle in tiktok_handles_list:
                #     tiktok_urls.append(f"https://www.tiktok.com/{handle}")
                
                # Scraping starten
                result = scrape.trigger_scraper(tiktok_url, num_posts)

                print(result)
                
                if 'snapshot_id' in result:
                    # In MongoDB speichern
                    job_data = {
                        'snapshot_id': result['snapshot_id'],
                        'profile_url': tiktok_url,
                        'profile_handle': tiktok_handle,
                        'num_posts': num_posts,
                        'status': 'running',
                        'created_at': datetime.now()
                    }
                    jobs.insert_one(job_data)
                    st.success(f"Scraping gestartet! Job ID: {result['snapshot_id']}")
                    st.info("Der Job läuft im Hintergrund weiter.")
                    st.rerun()

                else:
                    st.error("Fehler beim Starten")
            except Exception as e:
                st.error(f"Fehler: {str(e)}") 