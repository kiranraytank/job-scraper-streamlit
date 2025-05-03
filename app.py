
import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="RemoteOK Job Scraper", layout="wide")
st.title("💼 RemoteOK Job Scraper")

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

# --- Sidebar ---
st.sidebar.header("📊 Job Summary")
if "df" in st.session_state:
    st.sidebar.success(f"Total Jobs: {len(st.session_state.df)}")
else:
    st.sidebar.info("No jobs scraped yet.")

# --- Main UI ---
if st.button("🔄 Scrape Jobs"):
    df = scrape_jobs()
    if df is not None and not df.empty:
        st.session_state.df = df
        st.success("✅ Job data scraped successfully.")
    else:
        st.error("❌ Failed to scrape job data.")

# --- Filtering UI ---
if "df" in st.session_state:
    df = st.session_state.df

    with st.expander("🔍 Filter Jobs", expanded=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            search_text = st.text_input("Search (by position or company)")
        with col2:
            languages = ["All"] + sorted({lang for tags in df["Tags"] for lang in tags.split(", ")})
            selected_lang = st.selectbox("Filter by Language", languages)
        with col3:
            locations = ["All"] + sorted(df["Location"].dropna().unique())
            selected_location = st.selectbox("Filter by Location", locations)

        apply_filter = st.button("✅ Apply Filter")

    filtered_df = df.copy()

    if apply_filter:
        if search_text:
            filtered_df = filtered_df[
                filtered_df["Position"].str.contains(search_text, case=False, na=False) |
                filtered_df["Company"].str.contains(search_text, case=False, na=False)
            ]
        if selected_lang != "All":
            filtered_df = filtered_df[filtered_df["Tags"].str.contains(selected_lang, case=False, na=False)]
        if selected_location != "All":
            filtered_df = filtered_df[filtered_df["Location"] == selected_location]

        st.info(f"Showing {len(filtered_df)} job(s) out of {len(df)}")
    else:
        st.info(f"Showing all {len(df)} job(s)")
        filtered_df = df

    st.dataframe(filtered_df, use_container_width=True)

    # Download button
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Jobs as Excel", data=buffer, file_name="filtered_jobs.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.warning("Please click 'Scrape Jobs' to start.")

