import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import BytesIO

st.set_page_config(layout="wide")  # Optional: for better layout

st.title("Upwork Job Scraper")
st.write("Scrape RemoteOK jobs and filter by keyword, language, or country.")

# Define scraping function
@st.cache_data
def scrape_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        return []
    jobs_data = response.json()[1:]
    job_list = []
    for job in jobs_data:
        job_list.append({
            'Date': job.get('date'),
            'Company': job.get('company'),
            'Position': job.get('position'),
            'Location': job.get('location'),
            'Language': ', '.join(job.get('tags', [])),
            'URL': job.get('url')
        })
    return job_list

# Button to scrape
if st.button("Scrape Jobs"):
    job_data = scrape_jobs()

    if not job_data:
        st.error("No jobs found.")
    else:
        df = pd.DataFrame(job_data)

        st.sidebar.subheader("🔍 Filter Options")

        # Search filter
        keyword = st.sidebar.text_input("Search by keyword (Position or Company)").strip().lower()

        # Language filter
        all_languages = sorted({tag for tags in df['Language'].str.split(', ') for tag in tags})
        selected_languages = st.sidebar.multiselect("Select Language(s)", all_languages)

        # Country filter
        all_countries = sorted(df['Location'].dropna().unique())
        selected_countries = st.sidebar.multiselect("Select Country(s)", all_countries)

        # Apply filters
        filtered_df = df.copy()
        if keyword:
            filtered_df = filtered_df[
                filtered_df['Position'].str.lower().str.contains(keyword) |
                filtered_df['Company'].str.lower().str.contains(keyword)
            ]
        if selected_languages:
            filtered_df = filtered_df[
                filtered_df['Language'].apply(lambda x: any(lang in x for lang in selected_languages))
            ]
        if selected_countries:
            filtered_df = filtered_df[filtered_df['Location'].isin(selected_countries)]

        # Show job count
        st.sidebar.markdown(f"### 📊 Total Jobs: {len(filtered_df)}")

        # Show table
        st.subheader(f"Showing {len(filtered_df)} job(s)")
        if len(filtered_df) > 0:
            st.dataframe(filtered_df)

            # Download button
            output = BytesIO()
            file_name = f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            filtered_df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            st.download_button("Download Excel", output, file_name=file_name)
        else:
            st.warning("No jobs match the selected filters.")

