import streamlit as st
from db.db import get_collection, get_scraped_profile
import json
import pandas as pd
import io

# MongoDB Setup
scraped_profiles = get_collection("scraped_profiles")


def render_finished_jobs_tab():
    st.header("Abgeschlossene Jobs")
    
    if scraped_profiles.count_documents({}) == 0:
        st.info("Keine fertigen Jobs gefunden")
    else:
        scraped_cursor = scraped_profiles.find()
        for job in scraped_cursor:
            # Anpassung für mehrere Handles
            if 'profile_handles' in job:
                # Mehrere Handles
                handle_count = len(job['profile_handles'])
                handle_text = f"{handle_count} Profile ({job['profile_handles'][0][:50]}...)" if handle_count > 0 else "Unbekannt"
            else:
                # Altes Format (ein Handle)
                handle = job.get('profile_handle', job.get('profile_url', 'Unbekannt'))
                handle_text = f"{handle[:50]}..."
            
            # Profildaten für Export laden
            profile_data = get_scraped_profile(job['_id'])
            
            # Zwei Spalten erstellen: eine für Expander, eine für Buttons
            col1, col2, col3 = st.columns([8, 1, 1])
            
            with col1:
                expander = st.expander(f"Posts von {handle_text} gescraped am {job['scraped_at'].strftime('%d.%m.%Y um %H:%M')}")
            
            # Buttons nur hinzufügen wenn Daten verfügbar
            if profile_data and 'posts' in profile_data:
                # CSV Download
                with col2:
                    # Daten für CSV vorbereiten
                    if len(profile_data['posts']) > 0:
                        df = pd.DataFrame(profile_data['posts'])
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="CSV",
                            data=csv,
                            file_name=f"tiktok_data_{job['_id']}.csv",
                            mime='text/csv',
                            use_container_width=True,
                            type="primary"
                        )
                
                # JSON Download
                with col3:
                    # Daten für JSON vorbereiten
                    json_str = json.dumps(profile_data['posts'], indent=2)
                    st.download_button(
                        label="JSON",
                        data=json_str,
                        file_name=f"tiktok_data_{job['_id']}.json",
                        mime='application/json',
                        use_container_width=True,
                        type="primary"
                    )
            
            # Inhalt des Expanders bleibt gleich
            with expander:
                # Anzeige der URLs
                if 'profile_urls' in job:
                    st.write("**Profile:**")
                    for url in job['profile_urls']:
                        st.write(f"- {url}")
                else:
                    st.write(f"**Profil:** {job.get('profile_url', 'Nicht verfügbar')}")
                
                # st.write(f"**Posts pro Profil:** {job['num_posts']}")
                st.write(f"**Erstellt:** {job['scraped_at'].strftime('%d.%m.%Y, %H:%M')}")
                
                if profile_data and 'posts' in profile_data:
                    posts = profile_data['posts']
                    st.write(f"**Posts gefunden:** {len(posts)}")
                    
                    if posts:
                        # Tabelle erstellen
                        table_data = []
                        for post in posts:
                            table_data.append({
                                "Creator": post.get('profile_username', '-'),
                                "Beschreibung": post.get('description', 'Keine Beschreibung')[:25] + '...' if len(post.get('description', '')) > 50 else post.get('description', 'Keine Beschreibung'),
                                "Likes": post.get('digg_count', 0),
                                "Shares": post.get('share_count', 0),
                                "Kommentare": post.get('comment_count', 0),
                                "Gespeichert": post.get('collect_count', 0),
                                "Aufrufe": post.get('play_count', 0),
                                "Erstellt": post.get('create_time', 'Unbekannt').split('T')[0] if 'T' in post.get('create_time', '') else post.get('create_time', 'Unbekannt')
                            })
                        
                        # DataFrame erstellen und anzeigen
                        df = pd.DataFrame(table_data)
                        st.dataframe(df, use_container_width=True)
                        
                       