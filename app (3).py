import streamlit as st
import pandas as pd
from datetime import datetime
import feedparser
import uuid # For generating unique IDs
from urllib.parse import quote_plus # To properly encode search queries
!pip install feedparser -q


# --- CONFIGURATION ---
st.set_page_config(page_title="GB News Live Feed", layout="wide")

# --- LIVE NEWS FETCHING ---
def fetch_live_news():
    """Fetches live news from Google News RSS for Gilgit-Baltistan and returns a DataFrame."""
    # Comprehensive list of regions to search for and categorize
    regional_keywords = [
        "Gilgit-Baltistan", "Skardu", "Hunza", "Ghizer", "Astore", 
        "Diamer", "Ghanche", "Kharmang", "Shigar", "Gilgit"
    ]
    search_terms = " OR ".join(regional_keywords)
    encoded_search_terms = quote_plus(search_terms)
    rss_url = f"https://news.google.com/rss/search?q={encoded_search_terms}&hl=en-IN&gl=IN&ceid=IN:en"
    
    feed = feedparser.parse(rss_url)
    
    news_entries = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        source = entry.source.title if 'source' in entry else 'Google News'
        
        published_date_str = entry.published if 'published' in entry else datetime.now().isoformat()
        try:
            published_date = datetime.strptime(published_date_str, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d')
        except ValueError:
            published_date = datetime.now().strftime('%Y-%m-%d')
            
        # Infer region from title based on keywords
        inferred_region = "Gilgit-Baltistan" # Default if no specific region found
        for r_kw in regional_keywords:
            if r_kw.lower() in title.lower():
                inferred_region = r_kw
                break # Assign the first matching region

        category = "Local" # Default, could be improved with NLP
        
        news_entries.append({
            "id": str(uuid.uuid4().hex), 
            "title": title,
            "source": source,
            "category": category,
            "region": inferred_region, # Use inferred region
            "date": published_date,
            "link": link
        })
    
    return pd.DataFrame(news_entries)

# Fetch live news when the app starts or reruns
df = fetch_live_news()
df['date'] = pd.to_datetime(df['date'])


# --- UI HEADER ---
st.title("🏔️ Gilgit-Baltistan Live News Feed")
st.markdown("A real-time dashboard for tracking regional and national coverage of GB.")

# --- SIDEBAR FILTERS (The 'API Query' Logic) ---
st.sidebar.header("Filter News")
category_filter = st.sidebar.multiselect("Category", ["Local", "National"], default=["Local", "National"])

# Define selectable regions dynamically or from a predefined list
all_selectable_regions = sorted(df['region'].unique().tolist() if not df.empty else [
    "Gilgit-Baltistan", "Skardu", "Hunza", "Ghizer", "Astore", 
    "Diamer", "Ghanche", "Kharmang", "Shigar", "Gilgit"
])
selected_regions = st.sidebar.multiselect("Filter by Region(s)", all_selectable_regions, default=all_selectable_regions)

date_period_options = ['All Time', 'Last 24 Hours', 'Last 7 Days', 'Last 30 Days', 'Last Year']
date_period = st.sidebar.selectbox("Date Period", date_period_options, index=0)

sort_order_options = ['Latest to Oldest', 'Oldest to Latest']
sort_order = st.sidebar.selectbox("Sort Order", sort_order_options, index=0)





# --- DATA PROCESSING ---
filtered_df = df[df['category'].isin(category_filter)]

# Apply region filter
if selected_regions:
    filtered_df = filtered_df[filtered_df['region'].isin(selected_regions)]

# --- Apply Date Filter ---
from datetime import timedelta

if date_period == 'All Time':
    pass # No date filter applied for 'All Time'
elif date_period == 'Last 24 Hours':
    filtered_df = filtered_df[filtered_df['date'] >= (datetime.now() - timedelta(days=1))]
elif date_period == 'Last 7 Days':
    filtered_df = filtered_df[filtered_df['date'] >= (datetime.now() - timedelta(days=7))]
elif date_period == 'Last 30 Days':
    filtered_df = filtered_df[filtered_df['date'] >= (datetime.now() - timedelta(days=30))]
elif date_period == 'Last Year':
    filtered_df = filtered_df[filtered_df['date'] >= (datetime.now() - timedelta(days=365))]

# --- Apply Sort Order ---
if sort_order == 'Latest to Oldest':
    filtered_df = filtered_df.sort_values(by='date', ascending=False)
else:
    filtered_df = filtered_df.sort_values(by='date', ascending=True)


# --- MAIN DISPLAY ---
st.subheader("Latest News Feed")

if not filtered_df.empty:
    for index, row in filtered_df.iterrows():
        st.markdown(f"**{row['title']}**")
        st.caption(f"Source: {row['source']} | Date: {row['date']} | Region: {row['region']}")
        st.link_button("Read More", row['link'], help="Click to read the full article")
        st.divider()
else:
    st.info("No news found matching your filters.")

