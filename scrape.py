import streamlit as st
import requests
import json
from datetime import datetime

# ===== API Konfiguration =====
# Secrets aus Streamlit Config laden
BRIGHTDATA_API_KEY = st.secrets["BRIGHTDATA_API_KEY"]  # API-Key für Brightdata
DATASET_ID = st.secrets["DATASET_ID"]                  # Dataset ID für TikTok Scraper
AWS_ACCESS_KEY = st.secrets["AWS_ACCESS_KEY"]          # AWS Zugangsdaten für S3
AWS_SECRET_KEY = st.secrets["AWS_SECRET_KEY"]          # AWS Secret für S3

# Grundlegende Prüfung der Konfiguration
if not BRIGHTDATA_API_KEY:
    raise ValueError("BRIGHTDATA_API_KEY nicht gefunden in Streamlit secrets")


import requests



# ===== Scraper Funktionen =====
def trigger_scraper(profile_urls=None, num_posts=10):
    """Startet einen Scraping-Job für TikTok-Profile"""
    
    print("Trigger Scraper")
    
    # Input-Daten als Array erstellen
    data = []
    
    for url in profile_urls:
        data.append({
            "url": url,
            "num_of_posts": num_posts,
            "what_to_collect": "Posts & Reposts",
            "start_date": "",
            "end_date": "",
            "post_type": "",
        })
    

    url = "https://api.brightdata.com/datasets/v3/trigger"
    
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    
    params = {
        "dataset_id": DATASET_ID,
        "include_errors": "true",
        "type": "discover_new",
        "discover_by": "profile_url",
    }
  
    print("API-Anfrage senden")
    response = requests.post(url, headers=headers, params=params, json=data)
    print(response.json())
    
    # Fehlerbehandlung
    try:
        return response.json()
    except Exception as e:
        print(f"Fehler: {e}, Status: {response.status_code}, Text: {response.text}")
        return {"error": str(e)}


def check_status(snapshot_id):
    """
    Prüft den Status eines laufenden Scraping-Jobs und speichert
    die Ergebnisse in der MongoDB-Datenbank.
    
    Args:
        snapshot_id (str): Die ID des zu prüfenden Scraping-Jobs
        
    Returns:
        dict: Status-Nachricht oder Fehlermeldung
    """
    check_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}"
    }
    
    # API-Anfrage senden
    response = requests.get(check_url, headers=headers)
    
    if response.status_code == 200:
        try:
            # Prüfen, ob die Antwort leer ist
            if not response.text.strip():
                return {"error": "API lieferte leere Antwort"}
            
            # Der API-Response kann mehrere JSON-Objekte enthalten
            text = "[" + response.text.replace("}\n{", "},{") + "]"
            data = json.loads(text)
            
            # Daten in MongoDB speichern (scraped_profiles Collection)
            from db.db import get_collection
            profiles = get_collection("scraped_profiles")
            
            # Ergebnisse strukturieren und speichern
            result_data = {
                'snapshot_id': snapshot_id,
                'scraped_at': datetime.now(),
                'posts': data
            }
            
            profiles.insert_one(result_data)
            return {"message": "Daten in MongoDB gespeichert"}
            
        except Exception as e:
            print(f"Fehler beim Parsen: {e}")
            return {"error": str(e)}
    else:
        return {"error": f"Status code: {response.status_code}"}


# ===== Test Code =====
# Dieser Code wird nur ausgeführt, wenn die Datei direkt aufgerufen wird
# In der Produktion sollte dieser Code deaktiviert oder entfernt werden
"""
# Test für einen bestimmten Snapshot
snapshot_id = "s_m8sl09lp1kv6n5c7ni"
check_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
headers = {"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"}
print(check_status(snapshot_id))
"""