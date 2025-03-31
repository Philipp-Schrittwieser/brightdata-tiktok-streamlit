import streamlit as st
import pymongo
from datetime import datetime

def close_database():
    if 'db' in st.session_state:
        st.session_state.db.client.close()
        del st.session_state.db

def get_database():
    if 'db' not in st.session_state:
        # Schließe alte Verbindung falls vorhanden
        close_database()
        # Erstelle neue Verbindung
        client = pymongo.MongoClient(st.secrets["DB_CONNECTION_STRING"])
        st.session_state.db = client["tiktok_scraper"]
    
    return st.session_state.db

def get_collection(collection_name):
    db = get_database()
    return db[collection_name]

def get_scraped_profile(snapshot_id):
    """
    Holt ein gescraptes Profil aus der Datenbank.
    
    Args:
        snapshot_id (str): ID des Scrape-Jobs
        
    Returns:
        dict: Gescraptes Profil oder None
    """
    profiles = get_collection("scraped_profiles")
    return profiles.find_one({"snapshot_id": snapshot_id}) 