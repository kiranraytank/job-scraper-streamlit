
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

# --- Scrape Button ---
if st.button("🔄 Scrape Jobs"):
    df = scrape_jobs()
    if df is not None and not df.empty:
        st.session_state.df = df
        st.success("✅ Job data scraped successfully.")
    else:
        st.error("❌ Failed to scrape job data.")

# --- Sidebar Filters ---
if "df" in st.session_state:
    df = st.session_state.df

    st.sidebar.header("🔍 Filter Jobs")
    st.sidebar.markdown(f"**Total Jobs:** {len(df)}")

    search_text = st.sidebar.text_input("Search (by position/company)")
    
    all_languages = sorted({lang for tags in df["Tags"] for lang in tags.split(", ")})
    selected_lang = st.sidebar.selectbox("Language", ["All"] + all_languages)

    all_locations = sorted(df["Location"].dropna().unique())
    selected_location = st.sidebar.selectbox("Location", ["All"] + all_locations)

    apply_filter = st.sidebar.button("✅ Apply Filter")

    # --- Apply Filters ---
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
else:
    st.sidebar.info("Please scrape jobs first.")

# --- Show Table ---
if "df" in st.session_state:
    st.markdown(f"### Showing {len(filtered_df)} job(s) out of {len(df)}")
    st.dataframe(filtered_df, use_container_width=True)

    # --- Excel Download ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False)
    buffer.seek(0)
    st.download_button("📥 Download Filtered Jobs", data=buffer,
                       file_name="filtered_jobs.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


