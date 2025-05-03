import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import io

st.title("RemoteOk Job Scraper")
st.write("🔍 Scrape remote jobs, filter them, and download as Excel.")

@st.cache_data
def scrape_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        return None
    jobs_data = response.json()[1:]
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
    return pd.DataFrame(job_list)

# Button to scrape
if st.button("Scrape Jobs"):
    df = scrape_jobs()
    if df is not None and not df.empty:
        # Search
        search_term = st.text_input("Search by position or location:")
        if search_term:
            df = df[df['Position'].str.contains(search_term, case=False, na=False) |
                    df['Location'].str.contains(search_term, case=False, na=False)]

        # Filter by company
        companies = ['All'] + sorted(df['Company'].dropna().unique().tolist())
        selected_company = st.selectbox("Filter by company", companies)
        if selected_company != 'All':
            df = df[df['Company'] == selected_company]

        # Show results
        st.dataframe(df)

        # Excel download
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button("📥 Download as Excel", output, file_name="filtered_jobs.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.error("❌ No data fetched from RemoteOk.")

