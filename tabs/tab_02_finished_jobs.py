import streamlit as st
from db.db import get_collection, get_scraped_profile

# MongoDB Setup
jobs = get_collection("jobs")

def render_finished_jobs_tab():
    st.header("Abgeschlossene Jobs")
    
    completed_jobs = jobs.find({"status": "completed"}).sort('completed_at', -1)
    completed_jobs_list = list(completed_jobs)
    
    if len(completed_jobs_list) == 0:
        st.info("Keine fertigen Jobs gefunden")
    else:
        for job in completed_jobs_list:
            handle = job.get('profile_handle', job.get('profile_url', 'Unbekannt'))
            with st.expander(f"{job['num_posts']} Posts von {handle[:18]}... gescraped am {job['created_at'].strftime('%d.%m.%Y um %H:%M')}"):
                st.write(f"**Profil:** {job.get('profile_url', 'Nicht verfügbar')}")
                st.write(f"**Posts:** {job['num_posts']}")
                st.write(f"**Erstellt:** {job['created_at'].strftime('%d.%m.%Y, %H:%M')}")
                st.write(f"**Abgeschlossen:** {job['completed_at'].strftime('%d.%m.%Y, %H:%M')}")
                
                
                # Profildaten laden
                profile_data = get_scraped_profile(job['snapshot_id'])
                
                if profile_data:
                    st.write(f"**Posts gefunden:** {len(profile_data['posts'])}")
                    st.write("---")
                    st.write("### Posts:")
                    for i, post in enumerate(profile_data['posts']):
                        st.write(f"**Post {i+1}**")
                        st.write(f"**Beschreibung:** {post.get('description', 'Keine Beschreibung')}")
                        st.write(f"**Likes:** {post.get('digg_count', 0)}")
                        st.write(f"**Shares:** {post.get('share_count', 0)}")
                        st.write(f"**Kommentare:** {post.get('comment_count', 0)}")
                        st.write(f"**Aufrufe:** {post.get('play_count', 0)}")
                        st.write(f"**Erstellt:** {post.get('create_time', 'Unbekannt')}")
                        st.write("---") 