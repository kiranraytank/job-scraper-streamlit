import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Title and description
st.title("Upwork Job Scraper")
st.write("This is a demo Streamlit app to scrape jobs and download Excel file.")

# Scrape jobs from RemoteOK API
def scrape_and_save_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        st.error("❌ Failed to fetch data")
        return None

    jobs_data = response.json()[1:]  # Skip metadata
    job_list = []

    for job in jobs_data:
        job_entry = {
            'Date': job.get('date'),
            'Company': job.get('company'),
            'Position': job.get('position'),
            'Location': job.get('location'),
            'URL': job.get('url'),
            'Language': job.get('tags', []),
            'Country': job.get('location', '')  # Assume location contains country info
        }
        job_list.append(job_entry)

    return job_list

# Button to scrape jobs and show results
if st.button("Scrape Jobs"):
    job_list = scrape_and_save_jobs()

    if job_list:
        # Convert job list to a DataFrame
        df = pd.DataFrame(job_list)

        # Show total job count in the sidebar
        st.sidebar.write(f"Total Jobs Found: {len(df)}")

        # Display the jobs dataframe in a table
        st.dataframe(df)

        # Allow users to filter/search through the displayed jobs dynamically
        st.sidebar.title("Search Jobs")

        # Search by job title or company
        search_term = st.sidebar.text_input("Search by Position or Company", "")
        if search_term:
            df = df[df['Position'].str.contains(search_term, case=False) | df['Company'].str.contains(search_term, case=False)]

        # Search by country (optional)
        country_filter = st.sidebar.selectbox("Select Country", ["All"] + df['Country'].unique().tolist())
        if country_filter != "All":
            df = df[df['Country'] == country_filter]

        # Display the filtered dataframe
        st.dataframe(df)

        # Generate filename with the current timestamp
        file_name = f"jobs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Add download button for filtered jobs
        st.download_button("Download Excel", df.to_excel(index=False, engine='openpyxl'), file_name=file_name)
    else:
        st.warning("⚠️ No jobs found. Please try again later.")
