import streamlit as st
import validators
import requests
from bs4 import BeautifulSoup
import pandas as pd
import textstat  # Free readability scoring library
import plotly.express as px
from PIL import Image
from io import BytesIO
import re
import urllib.parse  # For handling relative URLs
from streamlit_lottie import st_lottie
import json
from urllib.parse import urlparse

# --- UI Styling ---
st.set_page_config(page_title="SEO Audit Tool", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for enhanced UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.2rem !important;
        color: #EEEEEE !important;
        text-align: center;
        margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border: none;
        padding: 15px 25px;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #FF8F00;
        transform: scale(1.05);
    }
    .metric-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #FF4B4B;
    }
    .metric-label {
        font-size: 1rem;
        color: #EEEEEE;
    }
    .status-good {
        color: #00FF00;
        font-weight: bold;
    }
    .status-warning {
        color: #FFBF00;
        font-weight: bold;
    }
    .status-bad {
        color: #FF4B4B;
        font-weight: bold;
    }
    .expander-header {
        font-size: 1.3rem !important;
        font-weight: bold !important;
    }
    .data-table {
        background-color: #2D2D2D;
        border-radius: 5px;
    }
    .url-input {
        border-radius: 5px;
        border: 2px solid #FF4B4B;
        padding: 10px;
    }
    .stProgress .st-eb {
        background-color: #FF4B4B;
    }
    .recommendation-item {
        background-color: #2D2D2D;
        border-left: 5px solid #FF4B4B;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 0 5px 5px 0;
    }
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        grid-gap: 10px;
    }
    .image-card {
        background-color: #2D2D2D;
        border-radius: 5px;
        padding: 10px;
        text-align: center;
    }
    .image-thumbnail {
        max-width: 100%;
        height: auto;
        border-radius: 5px;
        margin-bottom: 5px;
    }
    .tab-content {
        padding: 20px;
        background-color: #1E1E1E;
        border-radius: 0 5px 5px 5px;
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
     .header-container {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)
# ✅ **Utility Functions** - MOVED BEFORE THEY'RE CALLED
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

    readability_score = textstat.flesch_reading_ease(page_text) if page_text else None
    word_count = len(page_text.split()) if page_text else 0
    paragraph_count = len(soup.find_all("p"))
    link_count = len(soup.find_all("a"))
    
    # Extract sentences for readability analysis
    sentences = re.split(r'(?<=[.!?]) +', page_text) if page_text else []
    
    # Extract common words for keyword analysis
    words = page_text.lower().split() if page_text else []
    word_freq = {}
    stop_words = {'the', 'and', 'to', 'of', 'a', 'in', 'that', 'is', 'it', 'for', 'with', 'as', 'on', 'was', 'are', 'by', 'this', 'from', 'be'}
    for word in words:
        if word not in stop_words and len(word) > 3:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
    common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]

    image_tags = soup.find_all("img")
    images = []
    for img in image_tags:
        src = img.get("src")
        alt = img.get("alt", "No Alt Text")
        if src:
            src = urllib.parse.urljoin(url, src)  # Convert relative URLs to absolute
            images.append((src, alt))

    return title, description, keywords, headers, readability_score, word_count, paragraph_count, images, link_count, page_text, sentences, common_words

def check_image_compression(image_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(image_url, stream=True, timeout=5, headers=headers)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            size_kb = len(response.content) / 1024
            dimensions = img.size  # (width, height)
            return size_kb, dimensions
    except Exception:
        return None, None

def highlight_complex_sentences(text, threshold=50):
    sentences = re.split(r'(?<=[.!?]) +', text)
    complex_sentences = [(s, textstat.flesch_reading_ease(s)) for s in sentences if len(s.split()) > 10 and textstat.flesch_reading_ease(s) < threshold]
    return complex_sentences

def get_score_color(score, threshold_good=70, threshold_ok=50):
    if score >= threshold_good:
        return "status-good"
    elif score >= threshold_ok:
        return "status-warning"
    else:
        return "status-bad"

def create_recommendation_card(title, description, severity):
    severity_color = {
        "high": "#FF4B4B",
        "medium": "#FFBF00",
        "low": "#00FF00"
    }
    
    severity_icon = {
        "high": "❌",
        "medium": "⚠️",
        "low": "ℹ️"
    }
    
    return f"""
    <div style="background-color:#2D2D2D; padding:15px; border-radius:5px; margin-bottom:15px; border-left:5px solid {severity_color[severity]}">
        <h4 style="margin-top:0; color:white;">{severity_icon[severity]} {title}</h4>
        <p style="color:#EEEEEE; margin-bottom:0;">{description}</p>
    </div>
    """

def calculate_text_metrics(text):
    """Calculate various text metrics using textstat (free library)"""
    metrics = {}
    if text:
        metrics["reading_ease"] = textstat.flesch_reading_ease(text)
        metrics["grade_level"] = textstat.flesch_kincaid_grade(text)
        metrics["smog_index"] = textstat.smog_index(text)
        metrics["automated_readability"] = textstat.automated_readability_index(text)
        metrics["coleman_liau"] = textstat.coleman_liau_index(text)
        metrics["difficult_words"] = textstat.difficult_words(text)
        metrics["linsear_write"] = textstat.linsear_write_formula(text)
        metrics["gunning_fog"] = textstat.gunning_fog(text)
        metrics["text_standard"] = textstat.text_standard(text)
        metrics["sentence_count"] = textstat.sentence_count(text)
        metrics["avg_sentence_length"] = len(text.split()) / textstat.sentence_count(text) if textstat.sentence_count(text) > 0 else 0
    return metrics

def display_image_gallery(images, sample_size=10):
    """Display images in a responsive grid with details"""
    if not images:
        return
    
    # Show either sample_size or all images if less than sample_size
    display_images = images[:sample_size]
    
    # Display image grid with thumbnails
    st.markdown("<h4 style='color:#FF4B4B;'>📷 Image Gallery</h4>", unsafe_allow_html=True)
    
    image_html = "<div class='image-grid'>"
    for i, (img_url, alt) in enumerate(display_images):
        try:
            size_kb, dimensions = check_image_compression(img_url)
            size_status = ""
            if size_kb:
                if size_kb > 100:
                    size_status = "<span class='status-bad'>Heavy</span>"
                elif size_kb > 50:
                    size_status = "<span class='status-warning'>OK</span>"
                else:
                    size_status = "<span class='status-good'>Light</span>"
                
            alt_status = "✓" if alt and alt != "No Alt Text" else "✗"
            
            image_html += f"""
            <div class='image-card'>
                <img src="{img_url}" alt="{alt}" class="image-thumbnail" onerror="this.onerror=null;this.src='https://via.placeholder.com/150x100?text=Loading+Error';">
                <p style="margin:5px 0; font-size:0.8rem;">{alt_status} Alt: {alt[:20]}{'...' if len(alt) > 20 else ''}</p>
                <p style="margin:0; font-size:0.8rem;">{f"{size_kb:.1f}KB" if size_kb else "Size: Unknown"} {size_status}</p>
                <p style="margin:0; font-size:0.8rem;">{f"{dimensions[0]}x{dimensions[1]}" if dimensions else ""}</p>
            </div>
            """
        except Exception:
            # If error loading image
            image_html += f"""
            <div class='image-card'>
                <div style="height:100px;background:#333;display:flex;align-items:center;justify-content:center;border-radius:5px;">
                    <span style="color:#fff;">Error</span>
                </div>
                <p style="margin:5px 0; font-size:0.8rem;">Failed to load</p>
            </div>
            """
    
    image_html += "</div>"
    
    st.markdown(image_html, unsafe_allow_html=True)
    
    # Show view all button if there are more images
    if len(images) > sample_size:
        if st.button(f"View All {len(images)} Images", use_container_width=True):
            # Show full image table
            st.markdown("<h4 style='color:#FF4B4B;'>🖼️ All Images</h4>", unsafe_allow_html=True)
            image_data = []
            for i, (img_url, alt) in enumerate(images):
                size_kb, dimensions = check_image_compression(img_url)
                img_dimensions = f"{dimensions[0]}x{dimensions[1]}" if dimensions else "Unknown"
                img_size = f"{size_kb:.1f} KB" if size_kb else "Unknown"
                image_data.append([i+1, img_url, alt, img_size, img_dimensions])
            
            df = pd.DataFrame(image_data, columns=["#", "URL", "Alt Text", "Size", "Dimensions"])
            st.dataframe(df, use_container_width=True)

# --- Page Header with Animation ---
# Hero Section
st.markdown("""
<div class="header-container">
    <h1 style='text-align: center;'>🚀 Content Optimization</h1>
    <h5 style='text-align: center;'>🔍 Readability, keywords, and structure recommendations</h5>
</div>
""", unsafe_allow_html=True)

# --- Input URL Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='url-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>✨ Enter Your Website URL</h3>", unsafe_allow_html=True)
    
    url = st.text_input("", placeholder="https://www.example.com", key="url_input") 
    st.session_state.url = url
    
    audit = st.button("🚀 START COMPREHENSIVE SEO AUDIT", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("-----")
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# --- Progress Bar Animation ---
if audit and url:
    if not is_valid_url(url):
        st.error("❌ Please enter a valid URL including http:// or https://")
    else:
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
            
            # Wait for 0.05 seconds
            import time
            time.sleep(0.05)
        
        # Clear progress bar and status text after completion
        progress_bar.empty()
        status_text.empty()

# 🚀 **Audit Trigger**
if audit:
    if url and is_valid_url(url):
        with st.spinner("Analyzing your website..."):
            html_content = fetch_html(url)

            if html_content:
                title, description, keywords, headers, readability_score, word_count, paragraph_count, images, link_count, page_text, sentences, common_words = parse_html(html_content, url)
                
                # --- Key Metrics ---
                st.markdown("<h3 style='color:#FF4B4B; margin-top:20px;'>📌 Key Metrics at a Glance</h3>", unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown("""
                    <div class="metric-card">
                        <p class="metric-label">Title Length</p>
                        <p class="metric-value">{}</p>
                        <p class="{}">{}</p>
                    </div>
                    """.format(
                        len(title) if title else 0,
                        "status-good" if title and 50 <= len(title) <= 60 else "status-warning",
                        "Optimal" if title and 50 <= len(title) <= 60 else "Needs Improvement"
                    ), unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="metric-card">
                        <p class="metric-label">Word Count</p>
                        <p class="metric-value">{}</p>
                        <p class="{}">{}</p>
                    </div>
                    """.format(
                        word_count,
                        "status-good" if word_count >= 300 else "status-warning",
                        "Sufficient" if word_count >= 300 else "Too Short"
                    ), unsafe_allow_html=True)
                
                with col3:
                    if readability_score is not None:
                        st.markdown("""
                        <div class="metric-card">
                            <p class="metric-label">Readability</p>
                            <p class="metric-value">{:.1f}</p>
                            <p class="{}">{}</p>
                        </div>
                        """.format(
                            readability_score,
                            get_score_color(readability_score),
                            "Easy to Read" if readability_score >= 70 else "Moderate" if readability_score >= 50 else "Difficult"
                        ), unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="metric-card">
                            <p class="metric-label">Readability</p>
                            <p class="metric-value">N/A</p>
                            <p class="status-warning">No Content</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown("""
                    <div class="metric-card">
                        <p class="metric-label">Images</p>
                        <p class="metric-value">{}</p>
                        <p class="{}">{}</p>
                    </div>
                    """.format(
                        len(images) if images else 0,
                        "status-good" if images and len(images) >= 3 else "status-warning" if images else "status-bad",
                        "Sufficient" if images and len(images) >= 3 else "Add More" if images else "Missing"
                    ), unsafe_allow_html=True)

                # Create tabs for different analyses
                tab1, tab2, tab3 = st.tabs(["📑 Meta Info", "📝 Content Analysis", "🖼️ Media Analysis"])
                
                # ✅ **Basic SEO Overview**
                with tab1:
                    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("<h4 style='color:#FF4B4B;'>Title Tag</h4>", unsafe_allow_html=True)
                        st.code(title)
                        st.markdown(f"<p><strong>Length:</strong> {len(title)} characters {'(optimal)' if 50 <= len(title) <= 60 else '(not optimal)'}</p>", unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("<h4 style='color:#FF4B4B;'>Meta Description</h4>", unsafe_allow_html=True)
                        st.code(description)
                        st.markdown(f"<p><strong>Length:</strong> {len(description)} characters {'(optimal)' if 150 <= len(description) <= 160 else '(not optimal)'}</p>", unsafe_allow_html=True)
                    
                    st.markdown("<h4 style='color:#FF4B4B;'>Meta Keywords</h4>", unsafe_allow_html=True)
                    st.code(keywords)

                    st.markdown("<h4 style='color:#FF4B4B;'>Header Structure</h4>", unsafe_allow_html=True)
                    if headers:
                        # Display headers with hierarchy visualization
                        for header_type, header_content in headers:
                            indent = int(header_type[1]) * 20  # Indent based on header level
                            st.markdown(f"""
                            <div style="margin-left:{indent}px; padding:5px; border-left:3px solid #FF4B4B; margin-bottom:5px;">
                                <strong style="color:#FFBF00;">{header_type}:</strong> {header_content}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("❌ No Header Tags Found")
                    st.markdown("</div>", unsafe_allow_html=True)

                # 📝 **Content Analysis**
                with tab2:
                    st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
                    
                    # Content structure metrics
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Create a bar chart for content metrics
                        metrics_data = {
                            'Metric': ['Words', 'Paragraphs', 'Links', 'Images'],
                            'Count': [word_count, paragraph_count, link_count, len(images) if images else 0]
                        }
                        
                        fig = px.bar(
                            metrics_data, 
                            x='Metric', 
                            y='Count',
                            title='Content Structure',
                            color='Count',
                            color_continuous_scale='Reds',
                            height=300
                        )
                        fig.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font={"color": "white"},
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("<h4 style='color:#FF4B4B;'>📝 Content Details</h4>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <ul>
                            <li><strong>Total Words:</strong> {word_count} {'(Good)' if word_count >= 300 else '(Too short)'}</li>
                            <li><strong>Paragraphs:</strong> {paragraph_count}</li>
                            <li><strong>Avg Paragraph Length:</strong> {word_count / paragraph_count if paragraph_count > 0 else 0:.1f} words</li>
                            <li><strong>Links:</strong> {link_count}</li>
                            <li><strong>Link Density:</strong> {(link_count / word_count * 100) if word_count > 0 else 0:.1f}%</li>
                            <li><strong>Text-to-HTML Ratio:</strong> {word_count / (len(html_content) / 1000):.2f} words per KB</li>
                        </ul>
                        """, unsafe_allow_html=True)
                    
                    # Full readability analysis - using textstat (free)
                    st.markdown("<h4 style='color:#FF4B4B;'>📝 Comprehensive Readability Analysis</h4>", unsafe_allow_html=True)
                    
                    if page_text:
                        text_metrics = calculate_text_metrics(page_text)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("""
                            <div class="metric-card">
                                <p class="metric-label">Flesch Reading Ease</p>
                                <p class="metric-value">{:.1f}</p>
                                <p class="{}">Scale: 0-100 (Higher is easier)</p>
                            </div>
                            """.format(
                                text_metrics["reading_ease"],
                                get_score_color(text_metrics["reading_ease"]),
                            ), unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <div class="metric-card">
                                <p class="metric-label">Grade Level</p>
                                <p class="metric-value">{:.1f}</p>
                                <p class="{}">Years of education needed</p>
                            </div>
                            """.format(
                                text_metrics["grade_level"],
                                get_score_color(100 - text_metrics["grade_level"] * 10),
                            ), unsafe_allow_html=True)
                        
                        with col3:
                            st.markdown("""
                            <div class="metric-card">
                                <p class="metric-label">Sentence Complexity</p>
                                <p class="metric-value">{:.1f}</p>
                                <p class="{}">Avg. words per sentence</p>
                            </div>
                            """.format(
                                text_metrics["avg_sentence_length"],
                                get_score_color(100 - text_metrics["avg_sentence_length"] * 4),
                            ), unsafe_allow_html=True)
                        
                        # Additional readability metrics in expandable section
                        with st.expander("View All Readability Metrics"):
                            metrics_df = pd.DataFrame({
                                'Metric': [
                                    'Flesch Reading Ease',
                                    'Flesch-Kincaid Grade',
                                    'SMOG Index',
                                    'Coleman-Liau Index',
                                    'Automated Readability Index',
                                    'Gunning Fog',
                                    'Linsear Write Formula',
                                    'Text Standard',
                                    'Difficult Words',
                                    'Sentence Count',
                                    'Avg Sentence Length',
                                ],
                                'Value': [
                                    f"{text_metrics['reading_ease']:.1f} (Higher is easier)",
                                    f"{text_metrics['grade_level']:.1f} (Grade level)",
                                    f"{text_metrics['smog_index']:.1f} (Grade level)",
                                    f"{text_metrics['coleman_liau']:.1f} (Grade level)",
                                    f"{text_metrics['automated_readability']:.1f} (Grade level)",
                                    f"{text_metrics['gunning_fog']:.1f} (Grade level)",
                                    f"{text_metrics['linsear_write']:.1f} (Grade level)",
                                    text_metrics['text_standard'],
                                    text_metrics['difficult_words'],
                                    text_metrics['sentence_count'],
                                    f"{text_metrics['avg_sentence_length']:.1f} words",
                                ]
                            })
                            st.dataframe(metrics_df, use_container_width=True)

                        # Complex sentences analysis
                        st.markdown("<h4 style='color:#FF4B4B;'>Sentence Analysis</h4>", unsafe_allow_html=True)
                        complex_sentences = highlight_complex_sentences(page_text)
                        
                        if complex_sentences:
                            st.markdown(f"{len(complex_sentences)} complex sentences found that may be difficult to read.", unsafe_allow_html=True)
                            with st.expander(f"View {min(len(complex_sentences), 5)} Example Complex Sentences"):
                                for i, (sentence, score) in enumerate(complex_sentences[:5]):
                                    st.markdown(f"""
                                    <div style="background-color:#2D2D2D; padding:10px; border-radius:5px; margin-bottom:10px;">
                                        <p style="margin:0;">{i+1}. "{sentence}"</p>
                                        <p style="margin:0; color:#FF4B4B; font-size:0.8rem;">Readability Score: {score:.1f}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                        else:
                            st.success("No particularly complex sentences found.")
                        
                        # Keyword analysis
                        st.markdown("<h4 style='color:#FF4B4B;'>📝 Keyword Analysis</h4>", unsafe_allow_html=True)
                          
                                                
                        if common_words:
                            # Create keyword frequency chart
                            keywords_df = pd.DataFrame(common_words[:15], columns=['Keyword', 'Frequency'])
                            fig = px.bar(
                                keywords_df,
                                x='Keyword',
                                y='Frequency',
                                title='Top Keywords',
                                color='Frequency',
                                color_continuous_scale='Reds',)                   
                                # --- Media Analysis Tab ---
if 'images' in locals() and images:
    # Summary metrics
    total_images = len(images)
    images_with_alt = sum(1 for _, alt in images if alt and alt != "No Alt Text")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Total Images</p>
            <p class="metric-value">{}</p>
        </div>
        """.format(total_images), unsafe_allow_html=True)
    
    with col2:
        alt_percentage = (images_with_alt/total_images * 100) if total_images > 0 else 0
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Images with Alt Text</p>
            <p class="metric-value">{}</p>
            <p class="{}">{}% Coverage</p>
        </div>
        """.format(
            images_with_alt,
            "status-good" if alt_percentage >= 80 else "status-warning" if alt_percentage >= 50 else "status-bad",
            round(alt_percentage)
        ), unsafe_allow_html=True)
    
    with col3:
        # Calculate average image size
        sizes = [check_image_compression(img_url)[0] for img_url, _ in images]
        sizes = [s for s in sizes if s is not None]
        avg_size = sum(sizes) / len(sizes) if sizes else 0
        
        st.markdown("""
        <div class="metric-card">
            <p class="metric-label">Avg. Image Size</p>
            <p class="metric-value">{:.1f} KB</p>
            <p class="{}">Image Optimization</p>
        </div>
        """.format(
            avg_size,
            "status-good" if avg_size < 50 else "status-warning" if avg_size < 100 else "status-bad"
        ), unsafe_allow_html=True)
    
    # Display image gallery with sample
    st.markdown("<h4 style='color:#FF4B4B;'>📷 Image Gallery</h4>", unsafe_allow_html=True)
    
    # Show sample of images
    sample_size = min(6, len(images))
    display_images = images[:sample_size]
    
    # Display image grid with thumbnails
    image_html = "<div class='image-grid'>"
    for i, (img_url, alt) in enumerate(display_images):
        try:
            size_kb, dimensions = check_image_compression(img_url)
            size_status = ""
            if size_kb:
                if size_kb > 100:
                    size_status = "<span class='status-bad'>Heavy</span>"
                elif size_kb > 50:
                    size_status = "<span class='status-warning'>OK</span>"
                else:
                    size_status = "<span class='status-good'>Light</span>"
                
            alt_status = "✓" if alt and alt != "No Alt Text" else "✗"
            
            image_html += f"""
            <div class='image-card'>
                <img src="{img_url}" alt="{alt}" class="image-thumbnail" onerror="this.onerror=null;this.src='https://via.placeholder.com/150x100?text=Loading+Error';">
                <p style="margin:5px 0; font-size:0.8rem;">{alt_status} Alt: {alt[:20]}{'...' if len(alt) > 20 else ''}</p>
                <p style="margin:0; font-size:0.8rem;">{f"{size_kb:.1f}KB" if size_kb else "Size: Unknown"} {size_status}</p>
                <p style="margin:0; font-size:0.8rem;">{f"{dimensions[0]}x{dimensions[1]}" if dimensions else ""}</p>
            </div>
            """
        except Exception:
            # If error loading image
            image_html += f"""
            <div class='image-card'>
                <div style="height:100px;background:#333;display:flex;align-items:center;justify-content:center;border-radius:5px;">
                    <span style="color:#fff;">Error</span>
                </div>
                <p style="margin:5px 0; font-size:0.8rem;">Failed to load</p>
            </div>
            """
    
    image_html += "</div>"
    
    st.markdown(image_html, unsafe_allow_html=True)
    
    # Full image table
    with st.expander("View Complete Image Analysis"):
        image_data = []
        for i, (img_url, alt) in enumerate(images):
            size_kb, dimensions = check_image_compression(img_url)
            has_alt = "✓" if alt and alt != "No Alt Text" else "✗"
            size_status = "Good" if size_kb and size_kb < 50 else "Optimize" if size_kb and size_kb < 100 else "Heavy" if size_kb else "Unknown"
            image_data.append([
                i+1, 
                img_url, 
                has_alt,
                alt[:50] + ('...' if len(alt) > 50 else ''), 
                f"{size_kb:.1f} KB" if size_kb else "Unknown", 
                f"{dimensions[0]}x{dimensions[1]}" if dimensions else "Unknown",
                size_status
            ])
        
        df = pd.DataFrame(image_data, columns=["#", "URL", "Alt", "Alt Text", "Size", "Dimensions", "Status"])
        st.dataframe(df, use_container_width=True)
        



# Extract videos
videos = []
if 'html_content' in locals() and html_content:
    soup = BeautifulSoup(html_content, "html.parser")
    # Find iframe embeds (YouTube, Vimeo, etc.)
    iframe_videos = soup.find_all("iframe")
    for video in iframe_videos:
        src = video.get("src", "")
        if any(domain in src for domain in ["youtube", "vimeo", "wistia", "dailymotion"]):
            title = video.get("title", "No Title")
            width = video.get("width", "Unknown")
            height = video.get("height", "Unknown")
            videos.append((src, title, f"{width}x{height}" if width != "Unknown" else "Unknown"))
    
    # Find HTML5 video tags
    html5_videos = soup.find_all("video")
    for video in html5_videos:
        src = video.get("src", "")
        if not src:
            source = video.find("source")
            if source:
                src = source.get("src", "")
        
        width = video.get("width", "Unknown")
        height = video.get("height", "Unknown")
        title = video.get("title", "No Title")
        videos.append((src, title, f"{width}x{height}" if width != "Unknown" else "Unknown"))

if videos:
    st.markdown(f"<p>Found {len(videos)} video(s) on this page.</p>", unsafe_allow_html=True)
    
    # Create dataframe for videos
    video_data = []
    for i, (src, title, dimensions) in enumerate(videos):
        video_type = "YouTube" if "youtube" in src else "Vimeo" if "vimeo" in src else "HTML5" if src.endswith((".mp4", ".webm", ".ogg")) else "Other"
        video_data.append([i+1, src, title, dimensions, video_type])
    
    df = pd.DataFrame(video_data, columns=["#", "Source URL", "Title", "Dimensions", "Type"])
    st.dataframe(df, use_container_width=True)
   


if 'images' in locals() and images:
    # Generate recommendations based on image analysis
    recommendations = []
    
    # Check for missing alt text
    missing_alt = sum(1 for _, alt in images if not alt or alt == "No Alt Text")
    if missing_alt > 0:
        recommendations.append(
            create_recommendation_card(
                "Add Alt Text to Images", 
                f"Found {missing_alt} images without alt text. Adding descriptive alt text improves accessibility and SEO.",
                "high" if missing_alt > 5 else "medium"
            )
        )
    
    # Check for large images
    large_images = sum(1 for img_url, _ in images if check_image_compression(img_url)[0] and check_image_compression(img_url)[0] > 100)
    if large_images > 0:
        recommendations.append(
            create_recommendation_card(
                "Optimize Large Images", 
                f"Found {large_images} images larger than 100KB. Compress these images to improve page load time.",
                "high" if large_images > 3 else "medium"
            )
        )
    
    # Check for image format optimization
    non_next_gen = sum(1 for img_url, _ in images if img_url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')))
    if non_next_gen > 0:
        recommendations.append(
            create_recommendation_card(
                "Use Next-Gen Image Formats", 
                f"Consider converting {non_next_gen} images to WebP or AVIF format for better compression and quality.",
                "medium"
            )
        )
    
   
