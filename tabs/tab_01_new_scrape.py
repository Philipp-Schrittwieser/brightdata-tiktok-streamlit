import streamlit as st
import scrape
from datetime import datetime
from db.db import get_collection
import time

# MongoDB Setup
jobs = get_collection("jobs")

def render_new_scrape_tab():
    # Custom CSS für modernes Design
    st.markdown("""
    <style>
    .stApp {
        background-color: black;
        color: white;
    }
    .css-18e3th9 {
        padding: 2rem 10rem;
    }
    .stButton>button {
        background-color: #ec4899;
        color: white;
        font-weight: 500;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
    }
    .stButton>button:hover {
        background-color: #db2777;
    }
    .stTextInput>div>div>input {
        background-color: #111827;
        border: 2px solid #374151;
        border-radius: 0.5rem;
        color: white;
        padding: 0.75rem 1.5rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #ec4899;
    }
    </style>
    """, unsafe_allow_html=True)
        
    
    # Input-Bereich
    col1, col2, col3 = st.columns([4, 1, 1])

    with col1:
        if 'key_input' not in st.session_state:
            st.session_state.key_input = 1
        tiktok_input = st.text_input("", value="", placeholder="@creator1 @creator2 @creator3", key=st.session_state.key_input)
    
    with col2:
        # Anzahl Posts
        st.write("")
        st.write("")
        num_posts = st.number_input("", min_value=1, value=10, label_visibility="collapsed")
    
    with col3:
        st.write("")
        if st.button("Analysieren", type="primary"):
            # Handles verarbeiten
            raw_parts = tiktok_input.split("@")
            handle_list = ["@" + part.strip() for part in raw_parts if part.strip()]
            
            if not handle_list:
                st.error("Bitte gib mindestens einen Handle ein")
            else:
                with st.spinner("Starte Analyse..."):
                    try:
                        tiktok_urls = [f"https://www.tiktok.com/{handle}" for handle in handle_list]
                        result = scrape.trigger_scraper(tiktok_urls, num_posts)
                        
                        if 'snapshot_id' in result:
                            job_data = {
                                'snapshot_id': result['snapshot_id'],
                                'profile_urls': tiktok_urls,
                                'profile_handles': handle_list,
                                'num_posts': num_posts,
                                'status': 'running',
                                'created_at': datetime.now()
                            }
                            jobs.insert_one(job_data)
                            st.toast("🚀 Scraping gestartet!", icon="✨")
                            time.sleep(2)
                            st.success(f"Analyse für {len(handle_list)} Profile gestartet!")
                            st.session_state.key_input += 1
                            st.rerun()
                        else:
                            st.error("Fehler beim Starten")
                    except Exception as e:
                        st.error(f"Fehler: {str(e)}") 