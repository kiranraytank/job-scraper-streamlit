import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Title and description
st.title("Upwork Job Scraper")
st.write("This is a demo Streamlit app to scrape jobs and download Excel file.")
st.sidebar.title("Filter Jobs")
st.sidebar.write("Select language/technology stack:")

# Available technologies (add or remove based on your preference)
languages = ["All", "Node.js", "PHP", "Laravel", "MySQL", "WordPress", "Shopify", "React", "Python", "Ruby"]

# Sidebar filter for languages/technologies
selected_language = st.sidebar.selectbox("Choose a technology:", languages)

# Available countries (Add more countries as needed)
countries = ["All", "United States", "Canada", "India", "United Kingdom", "Australia", "Germany", "France", "Brazil"]

# Sidebar filter for countries
selected_country = st.sidebar.selectbox("Choose a country:", countries)

# Scrape jobs from RemoteOK API and filter based on the selected language and country
def scrape_and_save_jobs(language, country):
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

        # Filter jobs based on selected language
        if language != "All" and language not in job_entry['Language']:
            continue

        # Filter jobs based on selected country
        if country != "All" and country not in job_entry['Country']:
            continue

        job_list.append(job_entry)

    return job_list

# Button to scrape jobs and show results
if st.button("Scrape Jobs"):
    job_list = scrape_and_save_jobs(selected_language, selected_country)
    
    if job_list:
        # Convert job list to a DataFrame
        df = pd.DataFrame(job_list)

        # Show total job count in the sidebar
        st.sidebar.write(f"Total Jobs Found: {len(df)}")
        
        # Display the jobs dataframe
        st.dataframe(df)
        
        # Generate filename with the current timestamp
        file_name = f"jobs_{selected_language}_{selected_country}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        
        # Add download button
        st.download_button("Download Excel", df.to_excel(index=False, engine='openpyxl'), file_name=file_name)
    else:
        st.warning("⚠️ No jobs found for the selected language and country.")
