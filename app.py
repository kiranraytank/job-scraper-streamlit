import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

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

# Create a button for scraping jobs
if st.button("Scrape Jobs"):
    job_list = scrape_and_save_jobs()

    if job_list:
        # Convert job list to DataFrame
        df = pd.DataFrame(job_list)

        # Display total job count in the sidebar
        st.sidebar.write(f"Total Jobs Found: {len(df)}")

        # Search bar in sidebar for filtering jobs by position or company
        search_term = st.sidebar.text_input("Search by Position or Company", "")
        
        if search_term:
            df = df[df['Position'].str.contains(search_term, case=False) | df['Company'].str.contains(search_term, case=False)]

        # Filter jobs by country
        country_filter = st.sidebar.selectbox("Select Country", ["All"] + df['Country'].unique().tolist())
        if country_filter != "All":
            df = df[df['Country'] == country_filter]

        # Show the filtered dataframe
        st.dataframe(df)

        # Generate filename with the current timestamp
        file_name = f"jobs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Save the dataframe to a BytesIO object
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)  # Go to the beginning of the buffer

        # Add download button for filtered jobs
        st.download_button("Download Excel", excel_buffer, file_name=file_name)
    else:
        st.warning("⚠️ No jobs found. Please try again later.")

