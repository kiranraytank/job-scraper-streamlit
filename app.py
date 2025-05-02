import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.title("Upwork Job Scraper")
st.write("This is a demo Streamlit app to scrape jobs and download Excel file.")

def scrape_and_save_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        st.error("❌ Failed to fetch data")
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

    df = pd.DataFrame(job_list)
    return df

if st.button("Scrape Jobs"):
    df = scrape_and_save_jobs()
    if df is not None:
        st.dataframe(df)
        st.download_button("Download Excel", df.to_excel(index=False, engine='openpyxl'), file_name="jobs.xlsx")
