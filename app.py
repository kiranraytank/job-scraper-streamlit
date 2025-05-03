import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="RemoteOk Job Scraper", layout="wide")
st.title("💼 RemoteOk Job Scraper")
st.write("Scrape job listings and apply filters to download as Excel.")

# Scrape jobs function
@st.cache_data
def scrape_jobs():
    response = requests.get("https://remoteok.com/api")
    if response.status_code != 200:
        return None
    jobs_data = response.json()[1:]  # skip metadata
    job_list = []
    for job in jobs_data:
        job_entry = {
            "Date": job.get("date"),
            "Company": job.get("company"),
            "Position": job.get("position"),
            "Tags": ", ".join(job.get("tags", [])),
            "Location": job.get("location"),
            "URL": job.get("url")
        }
        job_list.append(job_entry)
    return pd.DataFrame(job_list)

# --- Scrape Button ---
if st.button("🔄 Scrape Jobs"):
    df = scrape_jobs()
    if df is not None:
        st.session_state.df = df
        st.success("✅ Jobs scraped successfully!")
    else:
        st.error("❌ Failed to scrape job data.")

# --- Sidebar Filters ---
if "df" in st.session_state:
    df = st.session_state.df

    st.sidebar.header("🔍 Filter Jobs")
    st.sidebar.markdown(f"**Total Jobs:** {len(df)}")

    # Search
    search = st.sidebar.text_input("Search (position or company)")

    # Language filter
    all_tags = sorted(set(tag.strip() for tags in df["Tags"] for tag in tags.split(",")))
    language = st.sidebar.selectbox("Language", ["All"] + all_tags)

    # Location filter
    all_locations = sorted(df["Location"].dropna().unique())
    location = st.sidebar.selectbox("Location", ["All"] + all_locations)

    # Apply Filter
    apply_filter = st.sidebar.button("✅ Apply Filter")

    filtered_df = df.copy()
    if apply_filter:
        if search:
            filtered_df = filtered_df[
                filtered_df["Position"].str.contains(search, case=False, na=False) |
                filtered_df["Company"].str.contains(search, case=False, na=False)
            ]
        if language != "All":
            filtered_df = filtered_df[filtered_df["Tags"].str.contains(language, case=False, na=False)]
        if location != "All":
            filtered_df = filtered_df[filtered_df["Location"] == location]
else:
    st.sidebar.info("⬆️ First click 'Scrape Jobs' to enable filters.")

# --- Display Table and Download ---
if "df" in st.session_state:
    st.markdown(f"### Showing {len(filtered_df)} of {len(df)} jobs")
    st.dataframe(filtered_df, use_container_width=True)

    # Download as Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False)
    buffer.seek(0)
    st.download_button(
        label="📥 Download Filtered Jobs",
        data=buffer,
        file_name="filtered_jobs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

