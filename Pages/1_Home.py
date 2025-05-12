import streamlit as st
import validators
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import os
from PIL import Image
from io import BytesIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def capture_website_screenshot(url):
    """Capture a screenshot of the website using headless Chrome"""
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1280,1024")
        
        # Initialize the driver
        from selenium.webdriver.chrome.service import Service as ChromeService
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)
        
        # Give the page some time to load
        time.sleep(3)
        
        # Capture screenshot
        screenshot = driver.get_screenshot_as_png()
        
        # Close the driver
        driver.quit()
        
        # Convert to PIL Image
        img = Image.open(BytesIO(screenshot))
        
        return img
    except Exception as e:
        st.error(f"Failed to capture screenshot: {str(e)}")
        return None

# --- UI Configuration ---
st.set_page_config(page_title="Seo-Auditor", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Enhanced UI with Dark Theme ---
st.markdown("""
<style>
    body {
        background-color: #121212;
        color: #EAEAEA;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }
    .main-header {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #4A90E2, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
        padding: 0 15px;
    }
    .sub-header {
        font-size: 1.1rem !important;
        color: #EAEAEA !important;
        text-align: center;
        margin-bottom: 25px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
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
    }
    .stButton>button:hover {
        background-color: #3A80D2;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(74, 144, 226, 0.4);
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 30px;
        text-align: center;
        border-left: 5px solid #4A90E2;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #4A90E2;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #EAEAEA;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .status-good {
        color: #4CAF50;
        font-weight: bold;
    }
    .status-warning {
        color: #FFC107;
        font-weight: bold;
    }
    .status-bad {
        color: #F44336;
        font-weight: bold;
    }
    .dashboard-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 25px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        height: 100%;
        transition: transform 0.3s ease;
        border-top: 3px solid #4A90E2;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
    }
    .dashboard-card:hover {
        transform: translateY(-5px);
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4A90E2;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }
    .card-title svg {
        margin-right: 10px;
    }
    .feature-card {
        background-color: #1A1A1A;
        border-radius: 12px;
        padding: 25px 20px;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
        border-bottom: 3px solid #4A90E2;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
    }
    .feature-title {
        font-size: 1.3rem;
        color: #FFFFFF;
        margin-bottom: 15px;
        font-weight: 600;
        text-align: center;
    }
    .feature-content {
        font-size: 0.95rem;
        color: #CCCCCC;
        line-height: 1.6;
        flex-grow: 1;
        word-wrap: break-word;
        overflow-wrap: break-word;
        hyphens: auto;
    }
    .feature-icon {
        font-size: 2.5rem;
        color: #4A90E2;
        margin-bottom: 15px;
        text-align: center;
        display: block;
    }
    .url-input {
        border-radius: 5px;
        border: 2px solid #4A90E2;
        padding: 10px;
        background-color: #2A2A2A;
        color: #EAEAEA;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #757575;
        font-size: 0.9rem;
        background-color: #1A1A1A;
        border-radius: 10px;
    }
    .nav-button {
        background-color: #1E1E1E;
        padding: 20px 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
        cursor: pointer;
        transition: all 0.3s;
        border: 1px solid #333333;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .nav-button:hover {
        background-color: #2A2A2A;
        transform: translateY(-5px);
        border-color: #4A90E2;
    }
    .icon-large {
        font-size: 2.2rem;
        color: #4A90E2;
        margin-bottom: 12px;
    }
    .progress-container {
        padding: 20px;
        background-color: #1E1E1E;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
    }
    .stProgress > div > div {
        background-color: #4A90E2;
    }
    .step-icon {
        font-size: 3rem;
        color: #4A90E2;
        margin-bottom: 15px;
        display: block;
        text-align: center;
    }
    .highlight-text {
        color: #4A90E2;
        font-weight: bold;
    }
    /* Feature section improvements */
    .features-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 30px;
    }
    .feature-container {
        flex: 1;
        min-width: 300px;
        display: flex;
        flex-direction: column;
    }
    /* Custom styling for the URL input area */
    .url-container {
        background: linear-gradient(135deg, #1E1E1E, #2A2A2A);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        border: 1px solid #333333;
        margin-bottom: 30px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    .stTextInput > div > div > input {
        background-color: #2A2A2A;
        color: #EAEAEA;
        border: 1px solid #4A90E2;
        border-radius: 5px;
        padding: 12px 15px;
        font-size: 1.1rem;
        width: 100%;
    }
    .stTextInput > div > div > input:focus {
        border: 2px solid #4A90E2;
        box-shadow: 0 0 10px rgba(74, 144, 226, 0.5);
    }
    .stTextInput > div > div > input::placeholder {
        color: #888888;
    }
    /* Badge styling */
    .seo-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 50px;
        font-weight: bold;
        margin-top: 5px;
        font-size: 0.85rem;
    }
    /* Layout and spacing improvements */
    .stContainer {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 20px;
    }
    /* How it works section */
    .how-it-works {
        margin: 40px 0;
    }
    .step-card {
        background-color: #1A1A1A;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border-left: 4px solid #4A90E2;
        height: 100%;
    }
    .step-number {
        background-color: #4A90E2;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
        margin-bottom: 10px;
    }
    .step-description {
        color: #CCCCCC;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    /* Responsive improvements */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem !important;
        }
        .feature-card {
            padding: 20px 15px;
        }
        .section-header {
            font-size: 1.3rem;
        }
        .feature-title {
            font-size: 1.1rem;
        }
    }
    .header-container {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'audit_complete' not in st.session_state:
    st.session_state.audit_complete = False
if 'audit_data' not in st.session_state:
    st.session_state.audit_data = None
if 'url' not in st.session_state:
    st.session_state.url = ""

# --- Utility Functions ---
def is_valid_url(url):
    return validators.url(url)

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.text if response.status_code == 200 else None
    except requests.RequestException:
        return None

def parse_html(html, url):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.text.strip() if soup.title else "No Title Found"
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = meta_desc["content"].strip() if meta_desc else "No Description Found"

    # Get meta keywords
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    keywords = meta_keywords["content"].strip() if meta_keywords else "No Keywords Found"

    headers = [(f"H{i}", tag.text.strip()) for i in range(1, 7) for tag in soup.find_all(f"h{i}")]
    page_text = ' '.join([p.get_text(strip=True) for p in soup.find_all(["p", "div", "span"])])

    # Simple readability calculation (words/sentences ratio)
    sentences = len([s for s in page_text.split('.') if s.strip()]) or 1
    word_count = len(page_text.split()) if page_text else 0
    readability_score = min(100, max(0, 206.835 - 1.015 * (word_count / sentences) - 84.6 * (sum(1 for word in page_text.split() if len(word) > 6) / word_count if word_count else 0)))

    paragraph_count = len(soup.find_all("p"))
    link_count = len(soup.find_all("a"))
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        alt = img.get("alt", "No Alt Text")
        if src:
            images.append((src, alt))

    # Check for SSL
    has_ssl = url.startswith("https://")

    return {
        "title": title,
        "title_length": len(title),
        "meta_description": description,
        "meta_description_length": len(description),
        "keywords": keywords,
        "header_structure": headers,
        "word_count": word_count,
        "readability_score": readability_score,
        "paragraph_count": paragraph_count,
        "link_count": link_count,
        "image_count": len(images),
        "images": images,
        "has_ssl": has_ssl
    }
    # In the Results Display Section, after you've shown the top metrics, add:
if st.session_state.audit_complete and st.session_state.audit_data:
    data = st.session_state.audit_data
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    # Score Overview
    st.markdown("<h2 class='section-header'>💡 Your SEO Performance</h2>", unsafe_allow_html=True)
    
    # Create two columns - one for metrics and one for website preview
    col_metrics, col_preview = st.columns([3, 2])
    
    with col_metrics:
        # Your existing metrics columns code
        col1, col2, col3 = st.columns(3)
        # ... (rest of your metrics display)
    with col_preview:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<h4 class='card-title'>💻 Website Preview</h4>", unsafe_allow_html=True)
        
        # Display the website screenshot if available
        if "screenshot" not in st.session_state:
            with st.spinner("Generating website preview..."):
                screenshot = capture_website_screenshot(st.session_state.url)
                if screenshot:
                    st.session_state.screenshot = screenshot
        
        if "screenshot" in st.session_state and st.session_state.screenshot:
            st.image(st.session_state.screenshot, use_column_width=True)
        else:
            st.warning("Unable to generate website preview")
        
        st.markdown("</div>", unsafe_allow_html=True)

def calculate_seo_score(data):
    score = 0
    max_score = 100
    
    # Title score (20%)
    if data["title_length"] > 0:
        if 40 <= data["title_length"] <= 60:
            score += 20
        elif 30 <= data["title_length"] < 40 or 60 < data["title_length"] <= 70:
            score += 15
        else:
            score += 10
    
    # Meta description score (15%)
    if data["meta_description_length"] > 0:
        if 140 <= data["meta_description_length"] <= 160:
            score += 15
        elif 120 <= data["meta_description_length"] < 140 or 160 < data["meta_description_length"] <= 180:
            score += 10
        else:
            score += 5
    
    # Content length score (20%)
    if data["word_count"] >= 1000:
        score += 20
    elif data["word_count"] >= 500:
        score += 15
    elif data["word_count"] >= 300:
        score += 10
    else:
        score += 5
    
    # Header structure score (15%)
    header_types = set(h_type for h_type, _ in data["header_structure"])
    if "H1" in header_types and len(header_types) >= 3:
        score += 15
    elif "H1" in header_types:
        score += 10
    elif header_types:
        score += 5
    
    # Image optimization score (15%)
    if data["image_count"] > 0:
        images_with_alt = sum(1 for _, alt in data["images"] if alt and alt != "No Alt Text")
        alt_score = (images_with_alt / data["image_count"]) * 15 if data["image_count"] > 0 else 0
        score += alt_score
    
    # SSL score (5%)
    if data["has_ssl"]:
        score += 5
    
    # Readability score (10%)
    if data["readability_score"] >= 60:
        score += 10
    elif data["readability_score"] >= 40:
        score += 7
    else:
        score += 3
    
    return int(min(score, max_score))

def get_score_color(score):
    if score >= 80:
        return "status-good"
    elif score >= 60:
        return "status-warning"
    else:
        return "status-bad"

def get_score_label(score):
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"

def save_data_to_session(data):
    st.session_state.audit_data = data
    st.session_state.audit_complete = True

# Hero Section
st.markdown("""
<div class="header-container">
    <h1 style='text-align: center;'>🚀 Welcome To Seo-Auditor</h1>
    <h5 style='text-align: center;'>🔍 Analyze & Visualize as Your Own Web</h5>
</div>
""", unsafe_allow_html=True)

# --- Input URL Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='url-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>✨ Enter Your Website URL</h3>", unsafe_allow_html=True)
    
    url = st.text_input("", placeholder="https://www.example.com", key="url_input", value=st.session_state.url)
    st.session_state.url = url
    
    audit = st.button("🚀 START COMPREHENSIVE SEO AUDIT", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("-----")
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
# --- Processing Logic ---
if audit and url:
    if not is_valid_url(url):
        st.error("❌ Please enter a valid URL including http:// or https://")
    else:
        # Progress bar animation
        st.markdown("<div class='progress-container'>", unsafe_allow_html=True)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(101):
            # Update progress bar
            progress_bar.progress(i)
            
            # Update status text based on progress
            if i < 20:
                status_text.text("🔍 Fetching website content...")
            elif i < 40:
                status_text.text("📊 Analyzing SEO metrics...")
            elif i < 60:
                status_text.text("📝 Checking content readability...")
            elif i < 80:
                status_text.text("🖼️ Processing images...")
            elif i < 100:
                status_text.text("🚀 Generating recommendations...")
            else:
                status_text.text("✅ Audit complete!")
            
            # Wait for 0.02 seconds
            time.sleep(0.02)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Fetch and analyze website
        html_content = fetch_html(url)
        
        if not html_content:
            st.error("❌ Failed to fetch website content. Please check the URL and try again.")
        else:
            # Parse HTML and analyze
            data = parse_html(html_content, url)
            
            # Calculate overall SEO score
            data["seo_score"] = calculate_seo_score(data)
            
            # Save data to session state
            save_data_to_session(data)
            
            # Force page refresh to show results
            st.rerun()

# --- Results Display Section ---
if st.session_state.audit_complete and st.session_state.audit_data:
    data = st.session_state.audit_data
    
    # Score Overview
    st.markdown("<h2 class='section-header'>🚀  Your SEO Performance</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <p class='metric-label'>📌  OVERALL SEO SCORE</p>
            <p class='metric-value'>{data["seo_score"]}<span style="font-size:1.5rem;">/100</span></p>
            <div class='seo-badge' style="background-color: {'#4CAF50' if data['seo_score'] >= 80 else '#FFC107' if data['seo_score'] >= 60 else '#F44336'}; color: white;">
                {get_score_label(data["seo_score"])}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <p class='metric-label'>📌 CONTENT QUALITY</p>
            <p class='metric-value'>{min(100, int(data["word_count"]/20))}<span style="font-size:1.5rem;">/100</span></p>
            <div class='seo-badge' style="background-color: {'#4CAF50' if data['word_count'] >= 1000 else '#FFC107' if data['word_count'] >= 500 else '#F44336'}; color: white;">
                {data["word_count"]} words
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <p class='metric-label'>📌 READABILITY</p>
            <p class='metric-value'>{int(data["readability_score"])}<span style="font-size:1.5rem;">/100</span></p>
            <div class='seo-badge' style="background-color: {'#4CAF50' if data['readability_score'] >= 70 else '#FFC107' if data['readability_score'] >= 50 else '#F44336'}; color: white;">
                {
                "Easy to Read" if data["readability_score"] >= 70 else 
                "Moderate" if data["readability_score"] >= 50 else 
                "Difficult"
                }
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    # Quick Summary
    st.markdown("<h3 class='section-header'>📸 Performance Snapshot</h3>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<h4 class='card-title'>📑 Meta Information</h4>", unsafe_allow_html=True)
        
        title_status = "status-good" if 40 <= data["title_length"] <= 60 else "status-warning" if (30 <= data["title_length"] < 40 or 60 < data["title_length"] <= 70) else "status-bad"
        st.markdown(f"<p><strong>Title:</strong> {data['title']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Title Length:</strong> <span class='{title_status}'>{data['title_length']} characters</span> {'✅' if 40 <= data['title_length'] <= 60 else '⚠️' if (30 <= data['title_length'] < 40 or 60 < data['title_length'] <= 70) else '❌'}</p>", unsafe_allow_html=True)
        
        desc_status = "status-good" if 140 <= data["meta_description_length"] <= 160 else "status-warning" if (120 <= data["meta_description_length"] < 140 or 160 < data["meta_description_length"] <= 180) else "status-bad"
        st.markdown(f"<p><strong>Meta Description:</strong> {data['meta_description']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Description Length:</strong> <span class='{desc_status}'>{data['meta_description_length']} characters</span> {'✅' if 140 <= data['meta_description_length'] <= 160 else '⚠️' if (120 <= data['meta_description_length'] < 140 or 160 < data['meta_description_length'] <= 180) else '❌'}</p>", unsafe_allow_html=True)
        
        ssl_status = "status-good" if data["has_ssl"] else "status-bad"
        ssl_text = "Secure HTTPS" if data["has_ssl"] else "Not Secure (HTTP)"
        ssl_icon = "✅" if data["has_ssl"] else "❌"
        st.markdown(f"<p><strong>Security:</strong> <span class='{ssl_status}'>{ssl_text}</span> {ssl_icon}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<h4 class='card-title'>📝 Content Overview</h4>", unsafe_allow_html=True)
        
        word_status = "status-good" if data["word_count"] >= 1000 else "status-warning" if data["word_count"] >= 500 else "status-bad"
        word_icon = "✅" if data["word_count"] >= 1000 else "⚠️" if data["word_count"] >= 500 else "❌"
        st.markdown(f"<p><strong>Word Count:</strong> <span class='{word_status}'>{data['word_count']} words</span> {word_icon}</p>", unsafe_allow_html=True)
        
        st.markdown(f"<p><strong>Paragraphs:</strong> {data['paragraph_count']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p><strong>Links:</strong> {data['link_count']}</p>", unsafe_allow_html=True)
        
        img_status = "status-good" if data["image_count"] > 0 else "status-warning"
        img_icon = "✅" if data["image_count"] > 0 else "⚠️"
        st.markdown(f"<p><strong>Images:</strong> <span class='{img_status}'>{data['image_count']}</span> {img_icon}</p>", unsafe_allow_html=True)
        
        header_status = "status-good" if any(h_type == "H1" for h_type, _ in data["header_structure"]) else "status-bad"
        header_text = "H1 Found" if any(h_type == "H1" for h_type, _ in data["header_structure"]) else "No H1 Tag"
        header_icon = "✅" if any(h_type == "H1" for h_type, _ in data["header_structure"]) else "❌"
        st.markdown(f"<p><strong>Header Structure:</strong> <span class='{header_status}'>{header_text}</span> {header_icon}</p>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        
    # Navigation to Detailed Reports
    st.markdown("<h3 class='section-header'>📃 Detailed Optimization Reports</h3>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class='nav-button'>
            <div class='icon-large'>📝</div>
            <h4>Content Analysis</h4>
            <p style="color: #BBBBBB;">Readability, keywords, and structure recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Content Analysis", key="content_btn", use_container_width=True):
            st.switch_page("pages/2_Content-Optimization.py")
    
    with col2:
        st.markdown("""
        <div class='nav-button'>
            <div class='icon-large'>🖼️</div>
            <h4>BackLinks & Authority</h4>
            <p style="color: #BBBBBB;">Analyze & Extract Your Competitors Backlinks</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("View Backlinks", key="backlink_btn", use_container_width=True):
            st.switch_page("pages/3_Backlinks & Authority.py")
            # Placeholder for future navigation
            pass
    
    with col3:
        st.markdown("""
        <div class='nav-button'>
            <div class='icon-large'>⚡</div>
            <h4>Site-Performance</h4>
            <p style="color: #BBBBBB;">Analyse Site performance & Core web Vitals</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Performance", key="perf_btn", use_container_width=True):
            st.switch_page("pages/4_Site Performance.py")
            # Placeholder for future navigation
            pass
    
    with col4:
        st.markdown("""
        <div class='nav-button'>
            <div class='icon-large'>⚙️</div>
            <h4>Technical Seo</h4>
            <p style="color: #BBBBBB;">Analyse technical SEO insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Technical SEO", key="tech_seo_btn", use_container_width=True):
            st.switch_page("pages/5_Technical SEO.py")
            # Placeholder for future navigation
            pass
        
    with col5:
        st.markdown("""
        <div class='nav-button'>
            <div class='icon-large'>📱</div>
            <h4>Chat With AI</h4>
            <p style="color: #BBBBBB;">Get instant recommendations Based on Your reports</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("AI Assistant", key="ai_assistant_btn", use_container_width=True):
            st.switch_page("pages/6_Chat with AI.py")
            # Placeholder for future navigation
            pass
# --- First-time visitor section ---
if not st.session_state.audit_complete:
    st.markdown("<h2 class='section-header'>🚀  Boost Your Search Rankings in Minutes</h2>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 class='card-title'>📊  Comprehensive Analysis</h3>
        <p>Our powerful tool scans your website for <span class="highlight-text">20+ critical SEO factors</span> including meta tags, content quality, keyword usage, and technical performance.</p>
        <p style="margin-top: 15px; color: #BBBBBB;">Identifies exactly what's holding your site back from ranking higher.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 class='card-title'>🔍 Actionable Insights</h3>
        <p>Get <span class="highlight-text">specific recommendations</span> tailored to your website that you can implement immediately to improve your search rankings.</p>
        <p style="margin-top: 15px; color: #BBBBBB;">No technical SEO expertise required - we break everything down in plain language.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 class='card-title'>📈  Track Performance</h3>
        <p>Monitor your SEO progress with our <span class="highlight-text">easy-to-understand dashboard</span> and see how your optimizations impact your search visibility over time.</p>
        <p style="margin-top: 15px; color: #BBBBBB;">Stay ahead of algorithm changes and outperform your competitors.</p>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    # How it works section
    st.markdown("<h3 class='section-header'>🪟  How It Works</h3>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 class='card-title'>Step 1: Enter URL 🔗</h3>
        <p>Paste your website URL in the input field above. Our tool works with any website or landing page.</p>
        <div style="text-align:center; margin-top:20px;">
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 class='card-title'>Step 2: Instant Analysis ⚙️</h3>
        <p>Our advanced algorithm analyzes your site in seconds, checking content, meta tags, images, and technical factors.</p>
        <div style="text-align:center; margin-top:20px;">
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("""
        <h3 class='card-title'>Step 3: Optimize & Grow 📈</h3>
        <p>Review your personalized improvement plan with prioritized action items to boost your search rankings.</p>
        <div style="text-align:center; margin-top:20px;">
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
