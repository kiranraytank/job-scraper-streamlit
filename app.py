import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="RemoteOk Job Scraper", layout="wide")
st.title("💼 RemoteOk Job Scraper")
st.write("Scrape job listings and apply filters to download as Excel.")

# Scrape jobs
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

# Scrape button
if st.button("🔄 Scrape Jobs"):
    df = scrape_jobs()
    if df is not None:
        st.session_state.df = df
        st.success("✅ Jobs scraped successfully!")
    else:
        st.error("❌ Failed to fetch job data.")

# Filters in sidebar
if "df" in st.session_state:
    df = st.session_state.df

    st.sidebar.header("🔍 Filter Jobs")
    st.sidebar.markdown(f"**Total Jobs:** {len(df)}")

    # Search input
    search = st.sidebar.text_input("Search (Position or Company)")

    # Multi-select: Language
    all_tags = sorted(set(tag.strip() for tags in df["Tags"] for tag in tags.split(",")))
    selected_languages = st.sidebar.multiselect("Select Language(s)", all_tags)

    # Multi-select: Location
    all_locations = sorted(df["Location"].dropna().unique())
    selected_locations = st.sidebar.multiselect("Select Location(s)", all_locations)

    # Apply Filter
    apply_filter = st.sidebar.button("✅ Apply Filter")

    filtered_df = df.copy()
    if apply_filter:
        # Apply search
        if search:
            filtered_df = filtered_df[
                filtered_df["Position"].str.contains(search, case=False, na=False) |
                filtered_df["Company"].str.contains(search, case=False, na=False)
            ]
        # Apply language filter
        if selected_languages:
            filtered_df = filtered_df[
                filtered_df["Tags"].apply(lambda tags: any(lang in tags for lang in selected_languages))
            ]
        # Apply location filter
        if selected_locations:
            filtered_df = filtered_df[filtered_df["Location"].isin(selected_locations)]
else:
    st.sidebar.info("⬆️ First click 'Scrape Jobs' to enable filters.")

# Show table and download button
if "df" in st.session_state:
    if apply_filter:
        st.markdown(f"### Showing {len(filtered_df)} of {len(df)} jobs")
        st.dataframe(filtered_df, use_container_width=True)

        # Excel download
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

