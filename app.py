import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

st.title("Upwork Job Scraper")
st.write("This is a demo Streamlit app to scrape jobs and download Excel file.")

# Add a dropdown or input field for language and country selection
selected_language = st.selectbox("Select Language", ["Any", "English", "Spanish", "French", "German"])
selected_country = st.selectbox("Select Country", ["Any", "United States", "Canada", "India", "Germany"])

def scrape_and_save_jobs(language, country):
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        st.error("❌ Failed to fetch data")
        return None

    jobs_data = response.json()[1:]
    job_list = []
    for job in jobs_data:
        # Filter jobs based on language and country
        job_language = job.get('language', 'Any')
        job_location = job.get('location', 'Any')
        
        if (language == "Any" or job_language == language) and (country == "Any" or job_location == country):
            job_entry = {
                'Date': job.get('date'),
                'Company': job.get('company'),
                'Position': job.get('position'),
                'Location': job.get('location'),
                'Language': job.get('language', 'Not specified'),
                'URL': job.get('url')
            }
            job_list.append(job_entry)

    if not job_list:
        st.warning("⚠️ No jobs found based on the selected filters")
        return None

    df = pd.DataFrame(job_list)
    return df

if st.button("Scrape Jobs"):
    df = scrape_and_save_jobs(selected_language, selected_country)
    if df is not None:
        st.dataframe(df)

        # Create the file name with the current date and time
        file_name = f"jobs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

        # Save dataframe to an in-memory Excel file
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        # Provide a download button for the in-memory Excel file
        st.download_button(
            label="Download Excel",
            data=excel_buffer,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
