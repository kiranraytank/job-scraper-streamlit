
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io

st.set_page_config(page_title="Job Scraper", layout="wide")

st.title("🌍 RemoteOk Job Scraper")
st.write("Use the sidebar to search and filter jobs by language and location.")

@st.cache_data
def scrape_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        return None
    jobs_data = response.json()[1:]  # skip the first element (meta info)
    job_list = []
    for job in jobs_data:
        job_entry = {
            'Date': job.get('date'),
            'Company': job.get('company'),
            'Position': job.get('position'),
            'Tags': ', '.join(job.get('tags', [])),  # language/skills
            'Location': job.get('location'),
            'URL': job.get('url')
        }
        job_list.append(job_entry)
    return pd.DataFrame(job_list)

# Load and display job data
df = scrape_jobs()
if df is None or df.empty:
    st.error("❌ Failed to fetch job data.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filters")

search_text = st.sidebar.text_input("Search (position/company)")
selected_language = st.sidebar.selectbox("Filter by Language", ["All"] + sorted(set(tag for tags in df['Tags'] for tag in tags.split(', '))))
selected_location = st.sidebar.selectbox("Filter by Location", ["All"] + sorted(df['Location'].dropna().unique()))

apply_filter = st.sidebar.button("Apply Filter")

# --- Apply filters ---
filtered_df = df.copy()

if apply_filter:
    if search_text:
        filtered_df = filtered_df[
            filtered_df['Position'].str.contains(search_text, case=False, na=False) |
            filtered_df['Company'].str.contains(search_text, case=False, na=False)
        ]

    if selected_language != "All":
        filtered_df = filtered_df[filtered_df['Tags'].str.contains(selected_language, case=False, na=False)]

    if selected_location != "All":
        filtered_df = filtered_df[filtered_df['Location'] == selected_location]

    st.success(f"🔎 Showing {len(filtered_df)} job(s) matching filters")

    st.dataframe(filtered_df, use_container_width=True)

    # Download Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        filtered_df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Filtered Jobs (Excel)",
        data=output,
        file_name="filtered_jobs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Apply filters from the sidebar to see results.")



