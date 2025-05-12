from django.urls import get_urlconf
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("Google_ApI_key")

# Function to fetch PageSpeed Insights Data
def fetch_pagespeed_data(url):
   
    API_URL = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={API_KEY}"
    
    try:
        response = requests.get(API_URL).json()
        
        # Check if 'lighthouseResult' exists in response
        if 'lighthouseResult' not in response:
            return {"Error": "Invalid response from PageSpeed API. Please check your API key or URL."}

        audits = response['lighthouseResult'].get('audits', {})
        
        # Extract performance score
        performance_score = response['lighthouseResult'].get('categories', {}).get('performance', {}).get('score', 0) * 100

        return {
            "Performance Score": performance_score,
            "LCP (Largest Contentful Paint)": round(audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000, 2),
            "CLS (Cumulative Layout Shift)": round(audits.get('cumulative-layout-shift', {}).get('numericValue', 0), 3),
            "FCP (First Contentful Paint)": round(audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000, 2),
            "Speed Index": round(audits.get('speed-index', {}).get('numericValue', 0) / 1000, 2),
            "Total Blocking Time": round(audits.get('total-blocking-time', {}).get('numericValue', 0), 2),
            "Render Blocking Resources": round(audits.get('render-blocking-resources', {}).get('numericValue', 0), 2),
            "Unused JavaScript": round(audits.get('unused-javascript', {}).get('numericValue', 0), 2),
            "Image Optimization": round(audits.get('uses-optimized-images', {}).get('numericValue', 0), 2),
            "Server Response Time": round(audits.get('server-response-time', {}).get('numericValue', 0) / 1000, 2),
        }
    except Exception as e:
        return {"Error": f"An error occurred: {str(e)}"}

# Get color based on performance score
def get_score_color(score):
    if score >= 90:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"

# Format metrics for display
def format_metric_value(metric, value):
    if isinstance(value, (int, float)):
        if "CLS" in metric:
            return f"{value:.3f}"
        elif "Score" in metric:
            return f"{value:.1f}%"
        else:
            return f"{value:.2f}s"
    return value

st.set_page_config(page_title="Site Performance", layout="wide") 
import streamlit as st

def main():
    url = get_urlconf()
        
    if url:
        # Use the stored URL for performance analysis
            data = fetch_pagespeed_data(url)
            # Rest of your existing code...
    
    if __name__ == "__main__":
        main()

# Hero Section
st.markdown("""
<div class="header-container">
    <h1 style='text-align: center;'>🚀 Site Performance & Web Vitals</h1>
    <h5 style='text-align: center;'>🔍 Analyze Site performance & web Vitals </h5>
</div>
""", unsafe_allow_html=True)

# --- Input URL Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='url-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>✨ Enter Your Website URL</h3>", unsafe_allow_html=True)
    
    url = st.text_input("", placeholder="https://www.example.com", key="url_input") 
    st.session_state.url = url
    
    audit = st.button("🚀 Analyze Site Performance", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    st.markdown("-----")
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
        color: white;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #dddddd;
    }
    .metric-card h3 {
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.5rem;
        font-weight: 600;
        color: #333333;
    }
    .metric-card p {
        margin-bottom: 0.5rem;
        font-size: 1rem;
        color: #666666;
    }
    .metric-value {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0.5rem 0 !important;
    }
    .good-metric {
        color: #2e7d32 !important;
        border-left-color: #2e7d32 !important;
    }
    .average-metric {
        color: #f57c00 !important;
        border-left-color: #f57c00 !important;
    }
    .poor-metric {
        color: #d32f2f !important;
        border-left-color: #d32f2f !important;
    }
    .metric-status {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.5rem;
    }
    .status-good {
        background-color: rgba(46, 125, 50, 0.1);
        color: #2e7d32;
    }
    .status-average {
        background-color: rgba(245, 124, 0, 0.1);
        color: #f57c00;
    }
    .status-poor {
        background-color: rgba(211, 47, 47, 0.1);
        color: #d32f2f;
    }
    .metric-description {
        margin-top: 0.5rem;
        font-size: 0.85rem;
        color: #666666;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #FFC107, #F44336);
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
</style>
""", unsafe_allow_html=True)
# Run analysis when button is clicked
if audit and url:
    with st.spinner("Analyzing website performance... This might take a moment."):
        data = fetch_pagespeed_data(url)
    
    # Check for errors
    if "Error" in data:
        st.error(data["Error"])
    else:
        # Create DataFrame
        df = pd.DataFrame(list(data.items()), columns=["Metric", "Value"])
        
        # Display Performance Score
        performance_score = data.get("Performance Score", 0)
        score_color = get_score_color(performance_score)
        
        # Define score emoji based on performance
        score_emoji = "🚀" if performance_score >= 90 else "⚠️" if performance_score >= 50 else "🚨"
        
        st.markdown(f"""
        <div style="padding: 1.5rem; background: linear-gradient(90deg, rgba(25,25,50,1) 0%, rgba(35,35,60,1) 100%); border-radius: 0.5rem; margin-bottom: 1.5rem; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            <h2 style="margin-bottom: 0.5rem; color: #7eb6ff;">Overall Performance Score</h2>
            <div style="display: flex; align-items: center; gap: 1.5rem;">
                <div style="width: 150px; height: 150px; border-radius: 50%; background: conic-gradient({score_color} 0% {performance_score}%, #3d4663 {performance_score}% 100%); display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                    <div style="width: 120px; height: 120px; border-radius: 50%; background: #1e2030; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 2rem; font-weight: bold; color: {score_color};">{score_emoji} {performance_score:.1f}%</span>
                    </div>
                </div>
                <div>
                    <p style="margin: 0; font-size: 1.4rem; font-weight: 600; color: #a0cfff;">
                        {"🚀 Excellent" if performance_score >= 90 else "⚠️ Needs Improvement" if performance_score >= 50 else "🚨 Poor"}
                    </p>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; color: #8bb8ff; max-width: 500px;">
                        {"Your site is performing well! Minor optimizations can still help." if performance_score >= 90 
                        else "Your site has some performance issues that should be addressed." if performance_score >= 50 
                        else "Your site has significant performance issues that need urgent attention."}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced Core Web Vitals Section
        st.markdown("<h2 style='margin-bottom: 1rem; color: #6cb6ff;'>Core Web Vitals</h2>", unsafe_allow_html=True)
        
        # Core Web Vitals explained
        st.markdown("""
        <div style="background-color: #1a2233; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; border-left: 4px solid #4285f4;">
            <p style="margin: 0; color: #a0cfff;">
                Core Web Vitals are a set of specific factors that Google considers important in a webpage's overall user experience. They're part of Google's page experience signals used for ranking in search results.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        
        # LCP
        lcp = data.get("LCP (Largest Contentful Paint)", 0)
        if lcp < 2.5:
            lcp_status = "good-metric"
            lcp_text_status = "status-good" 
            lcp_label = "Good"
            lcp_desc = "Great! Your LCP is fast, providing users with a quick visual feedback."
            lcp_emoji = "🚀"
        elif lcp < 4:
            lcp_status = "average-metric"
            lcp_text_status = "status-average"
            lcp_label = "Needs Improvement"
            lcp_desc = "Your LCP could be faster. Consider optimizing your largest page elements."
            lcp_emoji = "⚠️"
        else:
            lcp_status = "poor-metric"
            lcp_text_status = "status-poor"
            lcp_label = "Poor"
            lcp_desc = "Your LCP is too slow. Users may perceive your site as slow to load."
            lcp_emoji = "🚨"
            
        with cols[0]:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #4dabf7; background-color: #192235; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #4dabf7; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                <h3 style="color: #82bdff;">LCP {lcp_emoji}</h3>
                <p style="color: #a0cfff;">Largest Contentful Paint</p>
                <p class="metric-value" style="color: #4dabf7; font-weight: bold; font-size: 1.2rem;">{lcp:.2f}s</p>
                <div class="metric-status" style="display: inline-block; padding: 3px 8px; border-radius: 4px; background-color: rgba(77, 171, 247, 0.2); color: #4dabf7; font-weight: 600; margin: 0.5rem 0;">
                    {lcp_emoji} {lcp_label}
                </div>
                <p class="metric-description" style="color: #8bb8ff;">
                    {lcp_desc}
                </p>
                <p style="font-size: 0.75rem; color: #7eb6ff; margin-top: 0.5rem;">
                    🚀 Good: < 2.5s | ⚠️ Needs Improvement: 2.5s - 4s | 🚨 Poor: > 4s
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # CLS
        cls = data.get("CLS (Cumulative Layout Shift)", 0)
        if cls < 0.1:
            cls_status = "good-metric"
            cls_text_status = "status-good"
            cls_label = "Good"
            cls_desc = "Excellent! Your page has minimal visual layout shifts during loading."
            cls_emoji = "🚀"
        elif cls < 0.25:
            cls_status = "average-metric"
            cls_text_status = "status-average"
            cls_label = "Needs Improvement"
            cls_desc = "Your page has some layout shifts. Consider stabilizing your layout."
            cls_emoji = "⚠️"
        else:
            cls_status = "poor-metric"
            cls_text_status = "status-poor"
            cls_label = "Poor"
            cls_desc = "Your page has significant layout shifts that disrupt user experience."
            cls_emoji = "🚨"
            
        with cols[1]:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #4dabf7; background-color: #192235; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #4dabf7; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                <h3 style="color: #82bdff;">CLS {cls_emoji}</h3>
                <p style="color: #a0cfff;">Cumulative Layout Shift</p>
                <p class="metric-value" style="color: #4dabf7; font-weight: bold; font-size: 1.2rem;">{cls:.3f}</p>
                <div class="metric-status" style="display: inline-block; padding: 3px 8px; border-radius: 4px; background-color: rgba(77, 171, 247, 0.2); color: #4dabf7; font-weight: 600; margin: 0.5rem 0;">
                    {cls_emoji} {cls_label}
                </div>
                <p class="metric-description" style="color: #8bb8ff;">
                    {cls_desc}
                </p>
                <p style="font-size: 0.75rem; color: #7eb6ff; margin-top: 0.5rem;">
                    🚀 Good: < 0.1 | ⚠️ Needs Improvement: 0.1 - 0.25 | 🚨 Poor: > 0.25
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # FCP
        fcp = data.get("FCP (First Contentful Paint)", 0)
        if fcp < 1.8:
            fcp_status = "good-metric"
            fcp_text_status = "status-good"
            fcp_label = "Good"
            fcp_desc = "Excellent! Your page quickly delivers initial content to users."
            fcp_emoji = "🚀"
        elif fcp < 3:
            fcp_status = "average-metric"
            fcp_text_status = "status-average"
            fcp_label = "Needs Improvement"
            fcp_desc = "Your initial content load time could be faster for better user experience."
            fcp_emoji = "⚠️"
        else:
            fcp_status = "poor-metric"
            fcp_text_status = "status-poor"
            fcp_label = "Poor"
            fcp_desc = "Your page takes too long to show any content to users."
            fcp_emoji = "🚨"
            
        with cols[2]:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #4dabf7; background-color: #192235; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #4dabf7; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                <h3 style="color: #82bdff;">FCP {fcp_emoji}</h3>
                <p style="color: #a0cfff;">First Contentful Paint</p>
                <p class="metric-value" style="color: #4dabf7; font-weight: bold; font-size: 1.2rem;">{fcp:.2f}s</p>
                <div class="metric-status" style="display: inline-block; padding: 3px 8px; border-radius: 4px; background-color: rgba(77, 171, 247, 0.2); color: #4dabf7; font-weight: 600; margin: 0.5rem 0;">
                    {fcp_emoji} {fcp_label}
                </div>
                <p class="metric-description" style="color: #8bb8ff;">
                    {fcp_desc}
                </p>
                <p style="font-size: 0.75rem; color: #7eb6ff; margin-top: 0.5rem;">
                    🚀 Good: < 1.8s | ⚠️ Needs Improvement: 1.8s - 3s | 🚨 Poor: > 3s
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add Core Web Vitals Explanation
        st.markdown("""
        <div style="background-color: #19294d; padding: 1rem; border-radius: 0.5rem; margin: 1.5rem 0; border-left: 4px solid #4285f4;">
            <h4 style="margin-top: 0; color: #4dabf7;">What do Core Web Vitals mean?</h4>
            <ul style="margin-bottom: 0; padding-left: 1.5rem; color: #a0cfff;">
                <li><strong style="color: #82bdff;">LCP (Largest Contentful Paint) 🖼️</strong>: Measures loading performance - how quickly the largest content element becomes visible.</li>
                <li><strong style="color: #82bdff;">CLS (Cumulative Layout Shift) 📏</strong>: Measures visual stability - how much the page layout shifts during loading.</li>
                <li><strong style="color: #82bdff;">FCP (First Contentful Paint) ⏱️</strong>: Measures when the first content appears on screen - initial render time.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Other Metrics
        st.markdown("<h2 style='margin: 1.5rem 0 1rem 0; color: #6cb6ff;'>Additional Performance Metrics</h2>", unsafe_allow_html=True)
        
        # Filter core web vitals out
        other_metrics = df[~df['Metric'].isin(['Performance Score', 'LCP (Largest Contentful Paint)', 'CLS (Cumulative Layout Shift)', 'FCP (First Contentful Paint)'])]
        
        # Create better visualization for other metrics
        metric_cols = st.columns(2)
        
        for i, row in other_metrics.iterrows():
            metric = row['Metric']
            value = row['Value']
            
            # Determine status and color
            if "Speed Index" in metric:
                if value < 3.4:
                    status = "Good"
                    color = "#4dabf7"
                    metric_emoji = "🚀"
                elif value < 5.8:
                    status = "Needs Improvement"
                    color = "#3d96e0"
                    metric_emoji = "⚠️"
                else:
                    status = "Poor"
                    color = "#2e7fc9"
                    metric_emoji = "🚨"
                threshold = "🚀 Good: < 3.4s | ⚠️ Needs Improvement: 3.4s - 5.8s | 🚨 Poor: > 5.8s"
            elif "Total Blocking Time" in metric:
                if value < 200:
                    status = "Good"
                    color = "#4dabf7"
                    metric_emoji = "🚀"
                elif value < 600:
                    status = "Needs Improvement"
                    color = "#3d96e0"
                    metric_emoji = "⚠️"
                else:
                    status = "Poor"
                    color = "#2e7fc9"
                    metric_emoji = "🚨"
                threshold = "🚀 Good: < 200ms | ⚠️ Needs Improvement: 200ms - 600ms | 🚨 Poor: > 600ms"
            elif "Server Response Time" in metric:
                if value < 0.2:
                    status = "Good"
                    color = "#4dabf7"
                    metric_emoji = "🚀"
                elif value < 0.6:
                    status = "Needs Improvement"
                    color = "#3d96e0"
                    metric_emoji = "⚠️"
                else:
                    status = "Poor"
                    color = "#2e7fc9"
                    metric_emoji = "🚨"
                threshold = "🚀 Good: < 0.2s | ⚠️ Needs Improvement: 0.2s - 0.6s | 🚨 Poor: > 0.6s"
            else:
                # Generic status
                if value < 100:
                    status = "Good"
                    color = "#4dabf7"
                    metric_emoji = "🚀"
                elif value < 300:
                    status = "Needs Improvement" 
                    color = "#3d96e0"
                    metric_emoji = "⚠️"
                else:
                    status = "Poor"
                    color = "#2e7fc9"
                    metric_emoji = "🚨"
                threshold = ""
            
            # Normalize for progress bar (lower is better)
            if "Speed Index" in metric:
                normalized = min(value / 6, 1)  # 6s as max
                max_val = "6s"
            elif "Total Blocking Time" in metric:
                normalized = min(value / 600, 1)  # 600ms as max
                max_val = "600ms"
            elif "Server Response Time" in metric:
                normalized = min(value / 1, 1)  # 1s as max
                max_val = "1s"
            else:
                normalized = min(value / 500, 1)  # Generic scaling
                max_val = "500ms"
            
            # Display in alternating columns
            with metric_cols[i % 2]:
                st.markdown(f"""
                <div style="background-color: #192235; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid {color}; box-shadow: 0 2px 4px rgba(0,0,0,0.15);">
                    <h4 style="margin-top: 0; color: #82bdff;">{metric} {metric_emoji}</h4>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem; font-weight: 600; color: {color};">{format_metric_value(metric, value)}</span>
                        <span style="background-color: rgba(77, 171, 247, 0.2); color: {color}; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">{metric_emoji} {status}</span>
                    </div>
                    <div style="height: 6px; background-color: #2a3652; border-radius: 3px; margin: 0.5rem 0;">
                        <div style="height: 100%; width: {normalized * 100}%; background-color: {color}; border-radius: 3px;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #a0cfff;">
                        <span>0</span>
                        <span>{max_val}</span>
                    </div>
                    {f'<p style="font-size: 0.75rem; color: #7eb6ff; margin-top: 0.5rem;">{threshold}</p>' if threshold else ''}
                </div>
                """, unsafe_allow_html=True)
        
        # Interactive Chart
        st.markdown("<h2 style='margin: 1.5rem 0 1rem 0; color: #6cb6ff;'>Metrics Visualization</h2>", unsafe_allow_html=True)
        
        # Filter out performance score for chart
        chart_df = df[df['Metric'] != 'Performance Score'].copy()
        
        # Create a normalized column for better visualization
        chart_df['Normalized'] = chart_df.apply(
            lambda x: min(x['Value'] / 5, 1) if isinstance(x['Value'], (int, float)) else 0, 
            axis=1
        )
        
        # Create the chart
        fig = px.bar(
            chart_df,
            x="Metric",
            y="Value",
            title="PageSpeed Metrics Overview",
            text=chart_df['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else str(x)),
            color="Normalized",
            color_continuous_scale=["#4dabf7", "#74c0fc", "#a5d8ff"],
            labels={"Value": "Time (seconds)"}
        )
        
        fig.update_layout(
            height=500,
            xaxis_title="",
            yaxis_title="Value",
            coloraxis_showscale=False,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(tickangle=45),
            paper_bgcolor="#192235",
            plot_bgcolor="#192235",
            font=dict(color="#a0cfff")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Enhanced Recommendations
        st.markdown("<h2 style='margin: 1.5rem 0 1rem 0; color: #6cb6ff;'>Performance Recommendations</h2>", unsafe_allow_html=True)
        recommendations = []
        
        if data.get("LCP (Largest Contentful Paint)", 0) > 2.5:
            recommendations.append({
                "title": "Optimize Largest Contentful Paint (LCP)",
                "description": "Improve server response times, optimize resource loading, and prioritize visible content.",
                "steps": [
                    "Optimize your server response time through caching and CDN",
                    "Minimize CSS and JavaScript that blocks rendering",
                    "Optimize and compress images",
                    "Implement lazy loading for below-the-fold content"
                ],
                "emoji": "⚡"
            })
            
        if data.get("CLS (Cumulative Layout Shift)", 0) > 0.1:
            recommendations.append({
                "title": "Reduce Cumulative Layout Shift (CLS)",
                "description": "Prevent unexpected layout shifts that create a poor user experience.",
                "steps": [
                    "Always include width and height attributes on images and videos",
                    "Reserve space for ad elements and embeds",
                    "Avoid inserting new content above existing content",
                    "Use transform animations instead of animations that trigger layout changes"
                ],
                "emoji": "📏"
            })
            
        if data.get("FCP (First Contentful Paint)", 0) > 1.8:
            recommendations.append({
                "title": "Improve First Contentful Paint (FCP)",
                "description": "Speed up the time it takes for users to see the first content on your page.",
                "steps": [
                    "Eliminate render-blocking resources",
                    "Minimize critical CSS and inline it",
                    "Implement server-side rendering where possible",
                    "Optimize font loading with font-display: swap"
                ],
                "emoji": "⏱️"
            })
            
        if data.get("Render Blocking Resources", 0) > 0:
            recommendations.append({
                "title": "Reduce render-blocking resources",
                "description": "Minimize resources that prevent the page from rendering quickly.",
                "steps": [
                    "Defer non-critical JavaScript with async or defer attributes",
                    "Load CSS asynchronously for non-critical styles",
                    "Inline critical CSS",
                    "Remove unused CSS and JavaScript"
                ],
                "emoji": "🚧"
            })
            
        if data.get("Unused JavaScript", 0) > 0:
            recommendations.append({
                "title": "Remove unused JavaScript",
                "description": "Reduce JavaScript payload to improve load time and reduce CPU burden.",
                "steps": [
                    "Implement code splitting to load only what's needed",
                    "Use tree shaking to eliminate dead code",
                    "Audit and remove unused third-party scripts",
                    "Consider implementing lazy loading for non-critical JavaScript"
                ],
                "emoji": "🧹"
            })
            
        if data.get("Image Optimization", 0) > 0:
            recommendations.append({
                "title": "Optimize images",
                "description": "Properly format and compress images to reduce load time.",
                "steps": [
                    "Convert images to next-gen formats (WebP, AVIF)",
                    "Implement responsive images using srcset",
                    "Properly size images based on their display size",
                    "Use image CDNs for automatic optimization"
                ],
                "emoji": "🖼️"
            })
            
        if data.get("Server Response Time", 0) > 0.2:
            recommendations.append({
                "title": "Improve server response time",
                "description": "Optimize time to first byte (TTFB) for faster initial page load.",
                "steps": [
                    "Implement server-side caching",
                    "Optimize database queries",
                    "Use a CDN for static assets",
                    "Consider upgrading hosting or server infrastructure"
                ],
                "emoji": "🔌"
            })
            
        if recommendations:
            for i, rec in enumerate(recommendations):
                st.markdown(f"""
                <div style="background-color: #192235; padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    <h3 style="margin-top: 0; color: #4dabf7;">{i+1}. {rec['emoji']} {rec['title']}</h3>
                    <p style="color: #a0cfff;">{rec['description']}</p>
                    <h4 style="margin: 1rem 0 0.5rem 0; font-size: 1rem; color: #82bdff;">Recommended Actions:</h4>
                    <ul style="margin-bottom: 0; color: #a0cfff;">
                        {"".join([f'<li>✅ {step}</li>' for step in rec['steps']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 Your website is performing well! No major improvements needed.")

# Display explanation when no URL is entered
if not url:
    st.info("📝 Enter a URL above to analyze its performance metrics. The analysis will show you how your website performs according to Google's PageSpeed Insights.")
    
    # Add Core Web Vitals explanation
    st.markdown("""
    <div style="background-color: #192235; padding: 1.5rem; border-radius: 0.5rem; margin: 1.5rem 0; border-left: 4px solid #4285f4;">
        <h3 style="margin-top: 0; color: #4dabf7;">What are Core Web Vitals? 📊</h3>
        <p style="color: #a0cfff;">Core Web Vitals are a set of specific factors that Google considers important in a webpage's overall user experience. These metrics are critical for SEO and user experience:</p>
        <ul style="color: #a0cfff;">
            <li><strong style="color: #82bdff;">LCP (Largest Contentful Paint) 🖼️</strong>: Measures loading performance - how quickly the largest content element becomes visible.</li>
            <li><strong style="color: #82bdff;">CLS (Cumulative Layout Shift) 📏</strong>: Measures visual stability - how much the page layout shifts during loading.</li>
            <li><strong style="color: #82bdff;">FCP (First Contentful Paint) ⏱️</strong>: Measures when the first content appears on screen - initial render time.</li>
        </ul>
        <p style="color: #a0cfff;">Google uses these metrics as ranking signals, so optimizing them can improve your site's search performance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Placeholder visualization
    st.subheader("Sample Metrics Visualization")
    sample_data = {
        "Metric": ["LCP", "CLS", "FCP", "Speed Index", "TBT"],
        "Value": [2.5, 0.1, 1.8, 3.2, 200],
        "Category": ["Core Web Vital", "Core Web Vital", "Core Web Vital", "Performance", "Performance"]
    }
    sample_df = pd.DataFrame(sample_data)
    
    fig = px.bar(
        sample_df,
        x="Metric",
        y="Value",
        color="Category",
        title="Example PageSpeed Metrics",
        text=sample_df['Value'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else str(x)),
        color_discrete_map={"Core Web Vital": "#4dabf7", "Performance": "#74c0fc"}
    )
    
    fig.update_layout(
        height= 500,
        xaxis_title="",
        yaxis_title="Value",
        coloraxis_showscale=False,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(tickangle=45),
        paper_bgcolor="#192235",
        plot_bgcolor="#192235",
        font=dict(color="#a0cfff")
    )
    
    st.plotly_chart(fig, use_container_width=True)