import streamlit as st
import pandas as pd
import requests
from datetime import datetime
<<<<<<< HEAD
from io import BytesIO
from PIL import Image
import base64

# Set the page config as the first command
st.set_page_config(page_title="Job Scraper", layout="wide")

def get_base64_image(img_path):
    img = Image.open(img_path)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return img_str

# Get the logo image in base64 and display it
img_str = get_base64_image("raytik_blue.png")
st.markdown(
    f"<div style='text-align: center;'><img src='data:image/png;base64,{img_str}' width='150'></div>",
    unsafe_allow_html=True
)

st.title("🌐 Upwork Job Scraper")

# Initialize session state to persist data
if "df" not in st.session_state:
    st.session_state.df = None

def scrape_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        return pd.DataFrame()
    
    jobs = response.json()[1:]  # Skip first item (metadata)
    job_list = []

    for job in jobs:
        job_list.append({
=======

st.title("RemoteOk Job Scraper")
st.write("This is a demo Streamlit app to scrape jobs and download Excel file.")

def scrape_and_save_jobs():
    response = requests.get('https://remoteok.com/api')
    if response.status_code != 200:
        st.error("❌ Failed to fetch data")
        return None

<<<<<<< HEAD
    # 🔍 Show full raw JSON from API
    st.subheader("Full JSON Response")
    st.json(response.json())  # 👈 This will display the entire JSON response in a pretty format


=======
>>>>>>> e6256d1 (Commit #K4 set in dev)
    jobs_data = response.json()[1:]
    job_list = []
    for job in jobs_data:
        job_entry = {
>>>>>>> b469fe9 (Commit #K3.2 Show json)
            'Date': job.get('date'),
            'Company': job.get('company'),
            'Position': job.get('position'),
            'Location': job.get('location'),
<<<<<<< HEAD
            'Language': ', '.join(job.get('tags', [])),
            'URL': job.get('url')
        })

    return pd.DataFrame(job_list)

# Scrape Button
if st.button("🔄 Scrape Jobs"):
    st.session_state.df = scrape_jobs()

df = st.session_state.df

if df is not None and not df.empty:
    st.sidebar.header("🔍 Filter Options")

    # Sidebar filters
    keyword = st.sidebar.text_input("Search (Position or Company)").lower()
    languages = sorted({lang for row in df['Language'].dropna() for lang in row.split(', ')})
    selected_langs = st.sidebar.multiselect("Language(s)", languages)

    locations = sorted(df['Location'].dropna().unique())
    selected_locs = st.sidebar.multiselect("Location(s)", locations)

    # Filter logic
    filtered_df = df.copy()

    if keyword:
        filtered_df = filtered_df[filtered_df['Position'].str.lower().str.contains(keyword) |
                                  filtered_df['Company'].str.lower().str.contains(keyword)]

    if selected_langs:
        filtered_df = filtered_df[filtered_df['Language'].apply(lambda tags: any(lang in tags for lang in selected_langs))]

    if selected_locs:
        filtered_df = filtered_df[filtered_df['Location'].isin(selected_locs)]

    # Display total jobs and filtered table
    st.sidebar.markdown(f"### 📊 Total Jobs: {len(filtered_df)}")
    st.subheader(f"📋 Filtered Jobs: {len(filtered_df)}")
    st.dataframe(filtered_df, use_container_width=True)

    # Download filtered data
    if not filtered_df.empty:
        output = BytesIO()
        file_name = f"jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filtered_df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        st.download_button("📥 Download Excel", output, file_name=file_name)
else:
    st.info("Click 'Scrape Jobs' to load job listings.")

=======
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
>>>>>>> b469fe9 (Commit #K3.2 Show json)
