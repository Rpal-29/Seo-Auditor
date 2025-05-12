import streamlit as st
import validators
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
import concurrent.futures
import time
import base64
import json

st.set_page_config(page_title="Backlinks & Authority", layout="wide")

# Enhanced CSS for better styling with dark mode compatibility
st.markdown("""
<style>
    /* Core container styles with dark mode support */
    .metric-card {
        background-color: rgba(248, 249, 250, 0.1);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #4CAF50;
    }
    
    .metric-label {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.8);
        margin-top: 5px;
    }
    
    .header-container {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    .input-section {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .results-section {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stExpander {
        border: none !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        border-radius: 10px !important;
        margin-bottom: 20px;
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    /* Table styles with enhanced visibility */
    table {
        width: 100%;
        border-collapse: collapse;
        color: rgba(255, 255, 255, 0.9);
    }
    
    th {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 10px;
        text-align: left;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #ffffff;
        font-weight: bold;
    }
    
    td {
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    tr:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.05);
    }
    
    tr:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    /* Status colors with enhanced visibility */
    .status-active {
        color: #4CAF50;
        font-weight: bold;
        text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
    }
    
    .status-broken {
        color: #FF5252;
        font-weight: bold;
        text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
    }
    
    .status-redirect {
        color: #FFC107;
        font-weight: bold;
        text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
    }
    
    .gsc-connection {
        background-color: rgba(248, 249, 250, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Button styling with enhanced visibility */
    .stButton>button {
        background-color: #4A90E2;
        color: white;
        font-weight: bold;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        transition: all 0.3s ease;
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    .stButton>button:hover {
        background-color: #3A80D2;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.6);
    }
    
    /* Link styling with enhanced visibility */
    a {
        color: #64B5F6 !important;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
        color: #90CAF9 !important;
    }
    
    /* Enhanced visibility for status indicators */
    .active-status {
        background-color: rgba(76, 175, 80, 0.2);
        color: #4CAF50;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .broken-status {
        background-color: rgba(255, 82, 82, 0.2);
        color: #FF5252;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    
    .redirect-status {
        background-color: rgba(255, 193, 7, 0.2);
        color: #FFC107;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Define spam keywords list for toxic link detection
spam_keywords = ['casino', 'poker', 'viagra', 'cialis', 'sex', 'porn', 'xxx', 
                 'gambling', 'bet', 'forex', 'loan', 'dating', 'adult', 'pharmacy',
                 'weight-loss', 'diet', 'pills', 'mortgage', 'insurance', 'crypto']

# Hero Section
st.markdown("""
<div class="header-container">
    <h1 style='text-align: center;'>🚀 Backlinks & Authority</h1>
    <h5 style='text-align: center;'>🔍 Analyze & Extract Your Competitors Backlinks</h5>
</div>
""", unsafe_allow_html=True)

# --- Input URL Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='url-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>✨ Enter Your Website URL</h3>", unsafe_allow_html=True)
    
    url = st.text_input("", placeholder="https://www.example.com", key="url_input") 
    st.session_state.url = url
    
    audit = st.button("🚀 Analyze Backlinks & Authority", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("-----")
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# ✅ Utility Functions
def is_valid_url(url):
    return validators.url(url)

def fetch_html(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        return response.text if response.status_code == 200 else None
    except requests.RequestException:
        return None

# Check link status with proper handling
def check_link_status(href):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.head(href, headers=headers, timeout=5, allow_redirects=True)
        status_code = response.status_code
        final_url = response.url if response.url != href else "-"
        
        if status_code == 200:
            status = "✅ Active"
            status_class = "active-status"
        elif 300 <= status_code < 400:
            status = "🔄 Redirected"
            status_class = "redirect-status"
        else:
            status = "⚠️ Broken"
            status_class = "broken-status"
            
        # If head request doesn't work, try a GET request
        if status_code in [403, 405]:
            try:
                get_response = requests.get(href, headers=headers, timeout=5, allow_redirects=True)
                status_code = get_response.status_code
                final_url = get_response.url if get_response.url != href else "-"
                
                if status_code == 200:
                    status = "✅ Active"
                    status_class = "active-status"
                elif 300 <= status_code < 400:
                    status = "🔄 Redirected"
                    status_class = "redirect-status"
            except:
                pass
            
    except requests.RequestException:
        status = "❌ Broken"
        status_class = "broken-status"
        final_url = "-"
        status_code = "N/A"
        
    return {
        "status": status,
        "status_class": status_class,
        "final_url": final_url,
        "status_code": status_code
    }

# 🔗 Extract Backlinks & Status with concurrent processing
def extract_backlinks(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    all_links = []
    
    # Get all links first
    links_data = []
    for link in soup.find_all("a", href=True):
        href = link.get("href", "").strip()
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue
            
        try:
            href = urllib.parse.urljoin(base_url, href)
            anchor_text = link.get_text(strip=True) or "No Anchor Text"
            rel_attr = link.get("rel", [])
            is_dofollow = "nofollow" not in rel_attr
            
            if is_dofollow:
                link_type = "Do-Follow"
            else:
                link_type = "No-Follow"
                
            if any(keyword in href.lower() for keyword in spam_keywords):
                link_type = "Toxic"
                
            links_data.append({
                "href": href,
                "anchor_text": anchor_text,
                "link_type": link_type
            })
            
        except Exception:
            continue
    
    # Use progress bar to show status check progress
    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    status_placeholder.text("Checking link statuses...")
    
    # Process link statuses in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit all tasks
        future_to_link = {executor.submit(check_link_status, link["href"]): link for link in links_data}
        
        total = len(future_to_link)
        completed = 0
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_link):
            link_data = future_to_link[future]
            try:
                status_data = future.result()
                
                all_links.append({
                    "anchor_text": link_data['anchor_text'],
                    "url": link_data['href'],
                    "type": link_data['link_type'],
                    "status": status_data['status'],
                    "status_class": status_data['status_class'],
                    "final_url": status_data['final_url'],
                    "status_code": status_data['status_code']
                })
                
            except Exception as e:
                # Handle any exceptions in the future
                pass
                
            # Update progress
            completed += 1
            progress_bar.progress(completed / total)
            status_placeholder.text(f"Checking link statuses... ({completed}/{total})")
            
    # Clear progress indicators
    progress_bar.empty()
    status_placeholder.empty()
    
    return all_links

# Display metric in a card
def display_metric_card(title, value, icon):
    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 24px;">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
    </div>
    """, unsafe_allow_html=True)

# Function to generate Google Search Console exportable data
def prepare_gsc_data(broken_links):
    gsc_data = []
    for link in broken_links:
        gsc_data.append({
            "URL": link["url"],
            "Response Code": link["status_code"],
            "Source Page": link.get("final_url", "-"),
            "Anchor Text": link["anchor_text"]
        })
    return gsc_data

# Function to create a download link for GSC data
def get_gsc_export_link(broken_links):
    gsc_data = prepare_gsc_data(broken_links)
    csv = pd.DataFrame(gsc_data).to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="gsc_broken_links.csv" target="_blank" class="download-link">Export to Google Search Console Format</a>'
    return href

# Helper function to create HTML for formatted status
def format_status_html(status, status_class):
    return f'<span class="{status_class}">{status}</span>'

# 🚀 Audit Process
if audit:
    if url and is_valid_url(url):
        # Start UI for analysis
        st.markdown(
            """
            <div class="results-section">
                <h3>Backlink Analysis Results</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        with st.spinner(f"📊 Analyzing: {url}"):
            start_time = time.time()
            html_content = fetch_html(url)

            if html_content:
                # Extract and check all backlinks
                all_links = extract_backlinks(html_content, url)
                
                # Calculate analysis time
                analysis_time = round(time.time() - start_time, 2)
                st.success(f"✅ Analysis completed in {analysis_time} seconds")
                
                # Create DataFrame
                df = pd.DataFrame(all_links)
                
                # Filter dataframes for metrics
                df_dofollow = df[df["type"] == "Do-Follow"]
                df_nofollow = df[df["type"] == "No-Follow"]
                df_toxic = df[df["type"] == "Toxic"]
                df_broken = df[df["status"].str.contains("Broken")]
                df_redirected = df[df["status"].str.contains("Redirected")]
                
                # Display metrics in cards
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    display_metric_card("Total Links", len(df), "🔗")
                
                with col2:
                    display_metric_card("Do-Follow", len(df_dofollow), "✅")
                
                with col3:
                    display_metric_card("No-Follow", len(df_nofollow), "🚫")
                
                with col4:
                    display_metric_card("Broken", len(df_broken), "⚠️")
                
                with col5:
                    display_metric_card("Redirects", len(df_redirected), "🔄")
                
                # Display results in expandable sections with enhanced visibility
                with st.expander("🔗 **Extracted Backlinks (See More)**", expanded=True):
                    if not df.empty:
                        # Create a copy for display purposes
                        df_display = df[["anchor_text", "url", "status", "status_class"]].copy()
                        
                        # Format status with color-coded spans
                        df_display["status_formatted"] = df_display.apply(
                            lambda row: format_status_html(row["status"], row["status_class"]), axis=1
                        )
                        
                        # Convert URLs to clickable links with improved styling
                        df_display["url_formatted"] = df_display["url"].apply(
                            lambda x: f'<a href="{x}" target="_blank">{x}</a>'
                        )
                        
                        # Final dataframe for display
                        display_df = df_display[["anchor_text", "url_formatted", "status_formatted"]]
                        display_df.columns = ["Anchor", "URL", "Status"]
                        
                        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.warning("❌ No backlinks found.")

                with st.expander("✅ **Do-Follow Links**"):
                    if not df_dofollow.empty:
                        # Create a copy for display
                        df_dofollow_display = df_dofollow[["anchor_text", "url"]].copy()
                        
                        # Convert URLs to clickable links with improved styling
                        df_dofollow_display["url_formatted"] = df_dofollow_display["url"].apply(
                            lambda x: f'<a href="{x}" target="_blank">{x}</a>'
                        )
                        
                        # Final dataframe for display
                        display_df = df_dofollow_display[["anchor_text", "url_formatted"]]
                        display_df.columns = ["Anchor", "URL"]
                        
                        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.warning("❌ No Do-Follow links found.")

                with st.expander("🚫 **No-Follow Links**"):
                    if not df_nofollow.empty:
                        # Create a copy for display
                        df_nofollow_display = df_nofollow[["anchor_text", "url"]].copy()
                        
                        # Convert URLs to clickable links with improved styling
                        df_nofollow_display["url_formatted"] = df_nofollow_display["url"].apply(
                            lambda x: f'<a href="{x}" target="_blank">{x}</a>'
                        )
                        
                        # Final dataframe for display
                        display_df = df_nofollow_display[["anchor_text", "url_formatted"]]
                        display_df.columns = ["Anchor", "URL"]
                        
                        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.warning("❌ No No-Follow links found.")

                with st.expander("⚠️ **Broken Links (With Status Code)**"):
                    if not df_broken.empty:
                        # Create a copy for display
                        df_broken_display = df_broken[["anchor_text", "url", "status_code"]].copy()
                        
                        # Convert URLs to clickable links with improved styling
                        df_broken_display["url_formatted"] = df_broken_display["url"].apply(
                            lambda x: f'<a href="{x}" target="_blank">{x}</a>'
                        )
                        
                        # Final dataframe for display
                        display_df = df_broken_display[["anchor_text", "url_formatted", "status_code"]]
                        display_df.columns = ["Anchor", "URL", "Status Code"]
                        
                        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                        
                        # Add GSC export option
                        st.markdown(get_gsc_export_link(df_broken.to_dict('records')), unsafe_allow_html=True)
                    else:
                        st.success("✅ No broken links found.")

                with st.expander("🔄 **Redirected Links**"):
                    if not df_redirected.empty:
                        # Create a copy for display
                        df_redirected_display = df_redirected[["anchor_text", "url", "final_url"]].copy()
                        
                        # Convert URLs to clickable links with improved styling
                        df_redirected_display["url_formatted"] = df_redirected_display["url"].apply(
                            lambda x: f'<a href="{x}" target="_blank">{x}</a>'
                        )
                        
                        df_redirected_display["final_url_formatted"] = df_redirected_display["final_url"].apply(
                            lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x != "-" else "-"
                        )
                        
                        # Final dataframe for display
                        display_df = df_redirected_display[["anchor_text", "url_formatted", "final_url_formatted"]]
                        display_df.columns = ["Anchor", "URL", "Redirects To"]
                        
                        st.write(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                    else:
                        st.success("✅ No redirects found.")
                        
            else:
                st.error("❌ Could not fetch website content. The site may be blocking requests or unavailable.")
    else:
        st.error("❌ Please enter a valid URL!")