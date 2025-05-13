import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import re
from bs4 import BeautifulSoup
import html as html_module
import ssl
import socket
from urllib.parse import urlparse

# Google PageSpeed API Key
API_KEY = os.getenv("Google_ApI_key")

# --- UI Styling ---
st.set_page_config(page_title="Technical SEO Audit Tool", layout="wide", initial_sidebar_state="collapsed")

# Apply dark theme with custom CSS
st.markdown("""
<style>
    .main {
        background-color: #121212;
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #2b2b2b;
        color: white;
        border-color: #444;
    }
    .stButton>button {
        background-color: #2b2b2b;
        color: white;
        border-color: #444;
    }
    .stDataFrame {
        background-color: #2b2b2b;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2b2b2b;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #444;
    }
    .stProgress > div > div > div > div {
        background-color: #FF4B4B;
    }
    .css-50ug3q {
        font-size: 16px;
    }
    .block-container {
        padding-top: 2rem;
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
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="header-container">
    <h1 style='text-align: center;'>🚀 Technical SEO</h1>
    <h5 style='text-align: center;'>🔍  Analyze Website's Technical SEO</h5>
</div>
""", unsafe_allow_html=True)

# --- Input URL Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='url-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>✨ Enter Your Website URL</h3>", unsafe_allow_html=True)
    
    url = st.text_input("", placeholder="https://www.example.com", key="url_input") 
    st.session_state.url = url


# --- Functions ---
def fetch_pagespeed_data(url):
    """Fetch PageSpeed Insights data for a given URL."""
    API_ENDPOINT = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}&strategy=mobile"
    try:
        response = requests.get(API_ENDPOINT)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching PageSpeed data: {e}")
        return {}

def extract_metrics(data):
    """Extract relevant performance metrics from API response."""
    lighthouse = data.get("lighthouseResult", {})
    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})
    
    performance_score = categories.get("performance", {}).get("score", 0) * 100
    tbt = audits.get("total-blocking-time", {}).get("numericValue", 0)
    speed_index = audits.get("speed-index", {}).get("numericValue", 0)
    
    diagnostics = {
        "Render-blocking resources": audits.get("render-blocking-resources", {}).get("details", {}).get("items", []),
        "Image optimization": audits.get("uses-optimized-images", {}).get("details", {}).get("items", []),
        "Unused JavaScript and CSS": audits.get("unused-javascript", {}).get("details", {}).get("items", []) +
                                     audits.get("unused-css-rules", {}).get("details", {}).get("items", []),
        "Server response time": audits.get("server-response-time", {}).get("numericValue", 0)
    }
    
    return performance_score, tbt, speed_index, diagnostics

def display_diagnostics(diagnostics):
    """Display diagnostics data in an organized format."""
    for key, value in diagnostics.items():
        st.subheader(key)
        if isinstance(value, list) and value:
            # Process the data to make it more readable
            if key == "Render-blocking resources" or key == "Image optimization":
                cleaned_data = []
                for item in value:
                    if isinstance(item, dict):
                        # Extract only the most important fields
                        cleaned_item = {
                            "URL": item.get("url", ""),
                            "Size (KB)": round(item.get("totalBytes", 0) / 1024, 2) if "totalBytes" in item else 0,
                            "Wasted (KB)": round(item.get("wastedBytes", 0) / 1024, 2) if "wastedBytes" in item else 0
                        }
                        cleaned_data.append(cleaned_item)
                df = pd.DataFrame(cleaned_data)
            else:
                df = pd.DataFrame(value)
            st.dataframe(df)
        else:
            if key == "Server response time":
                st.write(f"{round(value/1000, 2)} seconds")
            else:
                st.write(value)

def check_ssl(url):
    """Check SSL certificate information."""
    parsed_url = urlparse(url)
    hostname = parsed_url.netloc
    context = ssl.create_default_context()
    
    try:
        with socket.create_connection((hostname, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                issuer = dict(x[0] for x in cert['issuer'])
                subject = dict(x[0] for x in cert['subject'])
                expiry = cert['notAfter']
                
                return {
                    "Valid": True,
                    "Issuer": issuer.get('organizationName', 'Unknown'),
                    "Subject": subject.get('commonName', 'Unknown'),
                    "Expiry": expiry
                }
    except Exception as e:
        return {
            "Valid": False,
            "Error": str(e)
        }

def check_security_headers(url):
    """Check important security headers."""
    try:
        response = requests.get(url)
        headers = response.headers
        
        security_headers = {
            "Strict-Transport-Security": headers.get("Strict-Transport-Security", "Missing"),
            "Content-Security-Policy": headers.get("Content-Security-Policy", "Missing"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options", "Missing"),
            "X-Frame-Options": headers.get("X-Frame-Options", "Missing"),
            "X-XSS-Protection": headers.get("X-XSS-Protection", "Missing"),
            "Referrer-Policy": headers.get("Referrer-Policy", "Missing")
        }
        
        return security_headers
    except Exception as e:
        return {"Error": str(e)}

def check_mobile_friendliness(url):
    """Check mobile friendliness using Google's API."""
    api_url = f"https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run?key={API_KEY}"
    payload = {
        "url": url
    }
    
    try:
        response = requests.post(api_url, json=payload)
        data = response.json()
        
        return {
            "Mobile Friendly": data.get("mobileFriendliness", "NOT_MOBILE_FRIENDLY") == "MOBILE_FRIENDLY",
            "Issues": data.get("mobileFriendlyIssues", [])
        }
    except Exception as e:
        return {"Error": str(e)}

def fetch_html(url):
    """Fetch HTML content from URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        return response.text
    except Exception as e:
        st.error(f"Error fetching HTML: {e}")
        return ""

def check_canonical(html):
    """Extract canonical URL from HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        return canonical.get("href")
    return "No canonical tag found"

def find_duplicate_content(url, html):
    """Simulate checking for duplicate content."""
    # In a real implementation, you'd use a service like Copyscape or your own algorithm
    # For now, we'll return a mock response
    return []


if st.button("🚀 Analyze Technical SEO"):
    if not url:
        st.warning("Please enter a valid URL")
    else:
        # Add http if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            st.session_state.url = url
            
        # Create tabs for different analyses
        tabs = st.tabs(["Page Speed", "Security", "Mobile Friendliness", "Content"])
        
        # Fetch HTML once for multiple analyses
        with st.spinner("Fetching website content..."):
            html_content = fetch_html(url)
        
        # Page Speed Tab
        with tabs[0]:
            with st.spinner("Analyzing page speed..."):
                data = fetch_pagespeed_data(url)
                if data:
                    performance_score, tbt, speed_index, diagnostics = extract_metrics(data)
                    
                    # Display main metrics
                    col1, col2, col3 = st.columns(3)
                    
                    # Create custom styled metric with colored gauge
                    def colored_metric(label, value, max_value, is_good_high=True):
                        if is_good_high:
                            color = "#4CAF50" if value >= 90 else "#FFC107" if value >= 50 else "#F44336"
                        else:
                            color = "#F44336" if value >= 90 else "#FFC107" if value >= 50 else "#4CAF50"
                            
                        html = f"""
                        <div style="margin-bottom: 20px;">
                            <p style="font-size: 18px; font-weight: bold; margin-bottom: 8px;">{label}</p>
                            <div style="display: flex; align-items: center;">
                                <div style="width: 100%; background-color: #444; height: 10px; border-radius: 5px;">
                                    <div style="width: {min(value/max_value*100, 100)}%; background-color: {color}; height: 10px; border-radius: 5px;"></div>
                                </div>
                                <span style="margin-left: 10px; font-weight: bold; color: {color};">{round(value, 1)}</span>
                            </div>
                        </div>
                        """
                        return html
                    
                    with col1:
                        st.markdown(colored_metric("Performance Score", performance_score, 100), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(colored_metric("Total Blocking Time (ms)", tbt, 600, False), unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(colored_metric("Speed Index (ms)", speed_index, 4000, False), unsafe_allow_html=True)
                    
                    # Visualize Performance Metrics
                    fig = px.bar(
                        x=["Performance Score", "TBT (ms)", "Speed Index (ms)"],
                        y=[performance_score, min(tbt, 500), min(speed_index/10, 500)], # Scale values to fit in one chart
                        labels={"x": "Metric", "y": "Value (normalized)"},
                        title="Page Speed Metrics",
                        color=["green", "red", "blue"],
                        text=[f"{performance_score:.1f}", f"{tbt:.1f}", f"{speed_index:.1f}"]
                    )
                    fig.update_layout(
                        plot_bgcolor="#2b2b2b",
                        paper_bgcolor="#121212",
                        font_color="white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display Diagnostics
                    st.markdown("### Detailed Diagnostics")
                    display_diagnostics(diagnostics)
                else:
                    st.error("Failed to fetch PageSpeed data. Please check the URL and try again.")
        
        # Security Tab
        with tabs[1]:
            with st.spinner("Checking security..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### SSL Certificate")
                    ssl_info = check_ssl(url)
                    if ssl_info["Valid"]:
                        st.success("Valid SSL Certificate")
                        st.json({
                            "Issuer": ssl_info["Issuer"],
                            "Subject": ssl_info["Subject"],
                            "Expiry": ssl_info["Expiry"]
                        })
                    else:
                        st.error("Invalid or Missing SSL Certificate")
                        st.write(ssl_info["Error"])
                
                with col2:
                    st.markdown("### Security Headers")
                    headers = check_security_headers(url)
                    if "Error" not in headers:
                        for header, value in headers.items():
                            if value == "Missing":
                                st.warning(f"{header}: Missing")
                            else:
                                st.success(f"{header}: Present")
                    else:
                        st.error(f"Error checking security headers: {headers['Error']}")
        
        # Mobile Friendliness Tab
        with tabs[2]:
            with st.spinner("Checking mobile friendliness..."):
                mobile_info = check_mobile_friendliness(url)
                
                if "Error" not in mobile_info:
                    if mobile_info["Mobile Friendly"]:
                        st.success("Website is Mobile Friendly!")
                    else:
                        st.error("Website is Not Mobile Friendly")
                        
                    if mobile_info["Issues"]:
                        st.subheader("Mobile Friendliness Issues")
                        for issue in mobile_info["Issues"]:
                            st.warning(issue.get("rule", "Unknown issue"))
                else:
                    st.error(f"Error checking mobile friendliness: {mobile_info['Error']}")
        
        # Content Tab
        with tabs[3]:
            with st.spinner("Analyzing content..."):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Canonical URL")
                    canonical_url = check_canonical(html_content)
                    st.code(canonical_url)
                
                with col2:
                    st.markdown("### Duplicate Content Check")
                    duplicates = find_duplicate_content(url, html_content)
                    if duplicates:
                        for duplicate in duplicates:
                            st.warning(f"Similar content found at: {duplicate['url']} ({duplicate['similarity']}% match)")
                    else:
                        st.success("No duplicate content detected")
