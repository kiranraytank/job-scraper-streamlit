import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io

st.title("Upwork Job Scraper (RemoteOK Live Data)")

# Step 1: Scrape jobs
def scrape_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        st.error("❌ Failed to fetch data from RemoteOK API.")
        return None

    jobs_data = response.json()[1:]  # Skip metadata
    job_list = []
    for job in jobs_data:
        job_entry = {
            'Date': job.get('date'),
            'Company': job.get('company'),
            'Position': job.get('position'),
            'Location': job.get('location'),
            'URL': job.get('url')
        }
        job_list.append(job_entry)

    if not job_list:
        st.warning("⚠️ No jobs found.")
        return None

    return pd.DataFrame(job_list)

# Step 2: Trigger scraping on button click
if st.button("Fetch Latest Jobs"):
    df = scrape_jobs()
    if df is not None:
        st.success(f"✅ Scraped {len(df)} jobs.")
        st.dataframe(df)

        # Step 3: Create downloadable Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="Download Excel",
            data=output,
            file_name="remoteok_jobs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
