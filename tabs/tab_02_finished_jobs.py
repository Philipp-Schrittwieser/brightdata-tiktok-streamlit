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
            # print("JOB STRUKTUR:")
            # print(json.dumps(job, default=str, indent=2))  # Bessere Ausgabe
            # Statt profile_handle/profile_url sollten wir die URLs aus den Posts holen
            profile_url = job['posts'][0].get('profile_url', 'Unbekannt')
            username = None
            for post in job['posts']:
                if 'profile_username' in post:
                    username = post['profile_username']
                    break
            
            handle_text = username or "Unbekannt"
            
            # Zwei Spalten erstellen
            col1, col2, col3 = st.columns([8, 1, 1])
            
            with col1:
                expander = st.expander(f"Posts von {handle_text} gescraped am {job['scraped_at'].strftime('%d.%m.%Y um %H:%M')}")
            
            # Posts direkt aus job verwenden
            posts = [p for p in job['posts'] if 'warning' not in p]
            
            # Downloads nur anzeigen wenn Posts vorhanden
            if posts:
                with col2:
                    df = pd.DataFrame(posts)
                    # entferne post_id, original_sound, profile_id, profile_avatar, profile_biography, preview_image, official_item, secu_id, original_item, shortcode, width, ratio, video_url, music, cdn_url, is_verified, carousel_images, tagged_user, tt_chain_token, commerce_info, timestamp, input, discovery_input, region
                    df = df.drop(columns=['post_id', 'original_sound', 'profile_id', 'profile_avatar', 'profile_biography', 'preview_image', 'offical_item', 'secu_id', 'original_item', 'shortcode', 'width', 'ratio', 'video_url', 'music', 'cdn_url', 'is_verified', 'carousel_images', 'tagged_user', 'tt_chain_token', 'commerce_info', 'timestamp', 'input', 'discovery_input', 'region'])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="CSV",
                        data=csv,
                        file_name=f"tiktok_data_{job['_id']}.csv",
                        mime='text/csv',
                        use_container_width=True,
                        type="primary"
                    )
                
                with col3:
                    json_str = json.dumps(posts, default=str, ensure_ascii=False)
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
                if posts:
                    st.write("**Profile:**")
                    # Sammle unique URLs
                    profile_urls = set()
                    for post in posts:
                        if 'profile_url' in post:
                            profile_urls.add(post['profile_url'])
                    
                    # Zeige alle gefundenen URLs
                    for url in profile_urls:
                        st.write(f"- {url}")
                else:
                    st.write("**Profil:** Keine Posts verfügbar")
                
                # st.write(f"**Posts pro Profil:** {job['num_posts']}")
                st.write(f"**Erstellt:** {job['scraped_at'].strftime('%d.%m.%Y, %H:%M')}")
                
                if posts:
                    st.write(f"**Posts gefunden:** {len(posts)}")
                    
                    # Tabelle erstellen
                    table_data = []
                    for post in posts:
                        table_data.append({
                            "Profil": post.get('profile_username', '-'),
                            "Beschreibung": post.get('description', 'Keine Beschreibung')[:50] + '...' if len(post.get('description', '')) > 50 else post.get('description', 'Keine Beschreibung'),
                            "Likes": str(post.get('digg_count', 0)),
                            "Shares": str(post.get('share_count', 0)),
                            "Kommentare": str(post.get('comment_count', 0)),
                            "Gespeichert": str(post.get('collect_count', 0)),
                            "Aufrufe": str(post.get('play_count', 0)),
                            "Erstellt": post.get('create_time', 'Unbekannt').split('T')[0] if 'T' in post.get('create_time', '') else post.get('create_time', 'Unbekannt'),
                            "Link": f"{post.get('url', '')}"
                        })
                    
                    # DataFrame erstellen und anzeigen
                    df = pd.DataFrame(table_data)
                    st.dataframe(df, use_container_width=True)
                        