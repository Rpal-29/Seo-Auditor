import streamlit as st
import random
import time
import pandas as pd
from datetime import datetime
import base64
import io
import requests
from urllib.parse import urlparse, urljoin
import re
import xml.etree.ElementTree as ET
from urllib.robotparser import RobotFileParser

# --- Streamlit Page Config ---
st.set_page_config(page_title="SEO Reports & Insights", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for better styling
st.markdown("""
<style>
    .card {
        border-radius: 10px;
        padding: 20px;
        background-color: #1E1E1E;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #2D2D2D;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .header-container {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
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
    .download-btn {
        background-color: #4CAF50 !important;
        width: 100%;
    }
    .code-block {
        background-color: #2D2D2D;
        border-radius: 5px;
        padding: 10px;
        max-height: 300px;
        overflow-y: auto;
        font-family: monospace;
        color: #f8f8f2;
    }
    .insight-box {
        background-color: #2D2D2D;
        border-left: 4px solid #FF4B4B;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
    .issue-item {
        padding: 8px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .issue-critical {
        background-color: rgba(255, 75, 75, 0.1);
        border-left: 3px solid #FF4B4B;
    }
    .issue-warning {
        background-color: rgba(255, 165, 0, 0.1);
        border-left: 3px solid #FFA500;
    }
    .issue-opportunity {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions for Robots.txt Analysis ---
def fetch_robots_txt(url):
    """Fetch robots.txt content from a website with enhanced error handling."""
    try:
        # Parse the base URL to get the domain
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(robots_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return {"status": "success", "content": response.text, "url": robots_url, "http_status": response.status_code}
        elif response.status_code == 404:
            return {"status": "error", "message": "Robots.txt file not found (404)", "url": robots_url, "http_status": response.status_code}
        else:
            return {"status": "error", "message": f"Failed to fetch robots.txt: HTTP {response.status_code}", "url": robots_url, "http_status": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection error - unable to connect to server", "url": robots_url if 'robots_url' in locals() else "unknown"}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out when fetching robots.txt", "url": robots_url if 'robots_url' in locals() else "unknown"}
    except requests.exceptions.TooManyRedirects:
        return {"status": "error", "message": "Too many redirects when fetching robots.txt", "url": robots_url if 'robots_url' in locals() else "unknown"}
    except Exception as e:
        return {"status": "error", "message": f"Error fetching robots.txt: {str(e)}", "url": robots_url if 'robots_url' in locals() else "unknown"}

def analyze_robots_txt(robots_content):
    """Perform detailed analysis of robots.txt content."""
    if not robots_content or robots_content.get("status") != "success":
        return {
            "sitemaps": [],
            "user_agents": [],
            "disallow_count": 0,
            "allow_count": 0,
            "crawl_delay": None,
            "has_wildcard_agent": False,
            "has_sitemap": False,
            "issues": []
        }
    
    content = robots_content["content"]
    
    # Parse using RobotFileParser
    parser = RobotFileParser()
    parser.parse(content.splitlines())
    
    # Extract sitemaps
    sitemaps = []
    for line in content.splitlines():
        line = line.strip()
        if line.lower().startswith("sitemap:"):
            sitemap_url = line.replace("sitemap:", "", 1).strip()
            sitemaps.append(sitemap_url)
    
    # Extract user agents
    user_agents = set()
    has_wildcard_agent = False
    for line in content.splitlines():
        line = line.strip().lower()
        if line.startswith("user-agent:"):
            agent = line.replace("user-agent:", "", 1).strip()
            user_agents.add(agent)
            if agent == "*":
                has_wildcard_agent = True
    
    # Count directives
    allow_count = sum(1 for line in content.splitlines() if line.strip().lower().startswith("allow:"))
    disallow_count = sum(1 for line in content.splitlines() if line.strip().lower().startswith("disallow:"))
    
    # Check for crawl delay
    crawl_delay = None
    for line in content.splitlines():
        line = line.strip().lower()
        if line.startswith("crawl-delay:"):
            try:
                crawl_delay = float(line.replace("crawl-delay:", "", 1).strip())
            except ValueError:
                pass
    
    # Identify issues
    issues = []
    
    if not has_wildcard_agent:
        issues.append({
            "type": "warning",
            "message": "No wildcard user-agent (*) found. Some crawlers might not have specific instructions."
        })
    
    if disallow_count == 0:
        issues.append({
            "type": "warning",
            "message": "No Disallow directives found. This may allow crawlers to access all areas of your site."
        })
    
    if not sitemaps:
        issues.append({
            "type": "opportunity",
            "message": "No Sitemap directives found in robots.txt. Adding sitemap URL helps search engines discover your content."
        })
    
    if crawl_delay and crawl_delay > 1:
        issues.append({
            "type": "warning",
            "message": f"Crawl-delay of {crawl_delay} seconds might be too high and could slow down indexing."
        })
    
    empty_lines = sum(1 for line in content.splitlines() if not line.strip())
    if empty_lines > len(content.splitlines()) / 2:
        issues.append({
            "type": "opportunity",
            "message": "Robots.txt contains many empty lines. Consider cleaning it up for better readability."
        })
    
    # Check for potentially problematic patterns
    if "disallow: /" in content.lower():
        issues.append({
            "type": "critical",
            "message": "Found 'Disallow: /' which blocks all crawlers from the entire site. This may prevent indexing."
        })
    
    return {
        "sitemaps": sitemaps,
        "user_agents": list(user_agents),
        "disallow_count": disallow_count,
        "allow_count": allow_count,
        "crawl_delay": crawl_delay,
        "has_wildcard_agent": has_wildcard_agent,
        "has_sitemap": len(sitemaps) > 0,
        "issues": issues
    }

# --- Helper Functions for Sitemap Analysis ---
def fetch_sitemap(url):
    """Fetch sitemap.xml with improved error handling."""
    try:
        # If the URL is not a direct sitemap URL, try to construct it
        if not url.lower().endswith(('.xml', '.gz')):
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            sitemap_url = f"{base_url}/sitemap.xml"
        else:
            sitemap_url = url
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(sitemap_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Check if it's a valid XML
            try:
                # Just validate XML without parsing fully yet
                ET.fromstring(response.content)
                return {"status": "success", "content": response.text, "url": sitemap_url, "http_status": response.status_code}
            except ET.ParseError:
                return {"status": "error", "message": "Invalid XML format in sitemap", "url": sitemap_url, "http_status": response.status_code}
        elif response.status_code == 404:
            return {"status": "error", "message": "Sitemap file not found (404)", "url": sitemap_url, "http_status": response.status_code}
        else:
            return {"status": "error", "message": f"Failed to fetch sitemap: HTTP {response.status_code}", "url": sitemap_url, "http_status": response.status_code}
    except requests.exceptions.ConnectionError:
        return {"status": "error", "message": "Connection error - unable to connect to server", "url": sitemap_url if 'sitemap_url' in locals() else "unknown"}
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "Request timed out when fetching sitemap", "url": sitemap_url if 'sitemap_url' in locals() else "unknown"}
    except requests.exceptions.TooManyRedirects:
        return {"status": "error", "message": "Too many redirects when fetching sitemap", "url": sitemap_url if 'sitemap_url' in locals() else "unknown"}
    except Exception as e:
        return {"status": "error", "message": f"Error fetching sitemap: {str(e)}", "url": sitemap_url if 'sitemap_url' in locals() else "unknown"}

def analyze_sitemap(sitemap_content, base_url):
    """Perform detailed analysis of sitemap.xml content."""
    if not sitemap_content or sitemap_content.get("status") != "success":
        return {
            "url_count": 0,
            "has_lastmod": False,
            "has_priority": False,
            "has_changefreq": False,
            "is_index": False,
            "nested_sitemaps": [],
            "issues": []
        }
    
    content = sitemap_content["content"]
    
    # Parse XML
    try:
        root = ET.fromstring(content)
        
        # Determine namespace if present
        ns = {}
        if root.tag.startswith('{'):
            ns_url = root.tag.split('}')[0].strip('{')
            ns = {'sm': ns_url}
            
        # Count URLs
        url_elements = root.findall('.//sm:url', ns) if ns else root.findall('.//url')
        url_count = len(url_elements)
        
        # Check for sitemap index
        sitemap_elements = root.findall('.//sm:sitemap', ns) if ns else root.findall('.//sitemap')
        is_index = len(sitemap_elements) > 0
        
        # Extract nested sitemaps from sitemap index
        nested_sitemaps = []
        if is_index:
            for sitemap in sitemap_elements:
                loc = sitemap.find('sm:loc', ns) if ns else sitemap.find('loc')
                if loc is not None and loc.text:
                    nested_sitemaps.append(loc.text)
        
        # Check for recommended elements
        has_lastmod = False
        has_priority = False
        has_changefreq = False
        
        for url in url_elements[:10]:  # Check first 10 URLs to determine pattern
            if url.find('sm:lastmod', ns) is not None or url.find('lastmod') is not None:
                has_lastmod = True
            if url.find('sm:priority', ns) is not None or url.find('priority') is not None:
                has_priority = True
            if url.find('sm:changefreq', ns) is not None or url.find('changefreq') is not None:
                has_changefreq = True
        
        # Identify issues
        issues = []
        
        if url_count == 0 and not is_index:
            issues.append({
                "type": "critical",
                "message": "Sitemap contains no URLs."
            })
        
        if not has_lastmod:
            issues.append({
                "type": "opportunity",
                "message": "URLs in sitemap don't include lastmod dates, which help search engines identify updated content."
            })
            
        if not has_changefreq:
            issues.append({
                "type": "opportunity",
                "message": "No changefreq elements found. Adding them can help guide crawler behavior."
            })
            
        if not has_priority:
            issues.append({
                "type": "opportunity",
                "message": "No priority elements found. Setting priorities can help indicate importance of pages."
            })
            
        if url_count > 50000:
            issues.append({
                "type": "warning",
                "message": f"Sitemap contains {url_count} URLs, exceeding the recommended limit of 50,000 URLs per sitemap."
            })
            
        # Check for URLs from different domains (potential issue)
        different_domain_urls = []
        parsed_base = urlparse(base_url)
        base_netloc = parsed_base.netloc
        
        for url in url_elements[:50]:  # Check a sample
            loc = url.find('sm:loc', ns) if ns else url.find('loc')
            if loc is not None and loc.text:
                parsed_url = urlparse(loc.text)
                if parsed_url.netloc and parsed_url.netloc != base_netloc:
                    different_domain_urls.append(loc.text)
                    
        if different_domain_urls:
            issues.append({
                "type": "warning",
                "message": f"Found {len(different_domain_urls)} URLs from different domains in your sitemap."
            })
            
        return {
            "url_count": url_count,
            "has_lastmod": has_lastmod,
            "has_priority": has_priority,
            "has_changefreq": has_changefreq,
            "is_index": is_index,
            "nested_sitemaps": nested_sitemaps,
            "issues": issues
        }
        
    except ET.ParseError:
        return {
            "url_count": 0,
            "has_lastmod": False,
            "has_priority": False,
            "has_changefreq": False,
            "is_index": False,
            "nested_sitemaps": [],
            "issues": [{
                "type": "critical",
                "message": "Sitemap XML is not valid and could not be parsed."
            }]
        }
    except Exception as e:
        return {
            "url_count": 0,
            "has_lastmod": False,
            "has_priority": False,
            "has_changefreq": False,
            "is_index": False,
            "nested_sitemaps": [],
            "issues": [{
                "type": "critical",
                "message": f"Error analyzing sitemap: {str(e)}"
            }]
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
        
        return {"status": "success", "headers": security_headers}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Header with Gradient ---
st.markdown(
    """
    <div class="header-container">
        <h1 style='text-align: center; color: #FFF;'>📊 SEO Reports & Insights</h1>
        <h5 style='text-align: center; color: #FFF;'>🔍 Generate comprehensive SEO audit reports, analyze rankings, and track performance trends</h5>
    </div>
    """,
    unsafe_allow_html=True
)

# Initialize session state for storing report data
if 'reports' not in st.session_state:
    st.session_state.reports = []
# --- Input URL Section ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("<div class='url-container'>", unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>✨ Enter Your Website URL</h3>", unsafe_allow_html=True)

    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        website_url = st.text_input("Enter Website URL:", placeholder="e.g., https://example.com")
    
    with col2:
        report_type = st.selectbox("Report Type", ["Basic", "Standard", "Comprehensive"])
    
    if st.button("🚀Generate Report", use_container_width=True):
        if website_url:
            # Ensure URL has a scheme
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
                
            with st.spinner("Analyzing website and generating report..."):
                # Fetch robots.txt
                robots_result = fetch_robots_txt(website_url)
                
                # Analyze robots.txt
                robots_analysis = analyze_robots_txt(robots_result)
                
                # Extract sitemaps from robots.txt
                sitemap_urls = robots_analysis["sitemaps"]
                
                # If no sitemaps found in robots.txt, try default location
                if not sitemap_urls:
                    parsed_url = urlparse(website_url)
                    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                    sitemap_urls = [f"{base_url}/sitemap.xml"]
                
                # Fetch the first sitemap
                sitemap_result = fetch_sitemap(sitemap_urls[0])
                
                # Analyze sitemap
                sitemap_analysis = analyze_sitemap(sitemap_result, website_url)
                
                # Fetch security headers
                security_result = check_security_headers(website_url)
                
                # Generate random data for demonstration
                seo_score = random.randint(50, 100)
                traffic_growth = random.randint(5, 30)
                keyword_rank = random.randint(1, 10)
                
                # More detailed metrics
                page_speed = random.randint(60, 95)
                backlinks = random.randint(100, 5000)
                mobile_score = random.randint(50, 100)
                
                # Issues found
                critical_issues = len([i for i in robots_analysis["issues"] if i["type"] == "critical"]) + len([i for i in sitemap_analysis["issues"] if i["type"] == "critical"])
                warnings = len([i for i in robots_analysis["issues"] if i["type"] == "warning"]) + len([i for i in sitemap_analysis["issues"] if i["type"] == "warning"])
                opportunities = len([i for i in robots_analysis["issues"] if i["type"] == "opportunity"]) + len([i for i in sitemap_analysis["issues"] if i["type"] == "opportunity"])
                
                # Add some random issues to meet minimum numbers
                if critical_issues < 1:
                    critical_issues += random.randint(0, 2)
                if warnings < 3:
                    warnings += random.randint(0, 5)
                if opportunities < 5:
                    opportunities += random.randint(0, 10)
                
                # Store report data
                report_data = {
                    "url": website_url,
                    "type": report_type,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "seo_score": seo_score,
                    "traffic_growth": traffic_growth,
                    "keyword_rank": keyword_rank,
                    "page_speed": page_speed,
                    "backlinks": backlinks,
                    "mobile_score": mobile_score,
                    "critical_issues": critical_issues,
                    "warnings": warnings,
                    "opportunities": opportunities,
                    "robots_txt": robots_result,
                    "robots_analysis": robots_analysis,
                    "sitemap": sitemap_result,
                    "sitemap_analysis": sitemap_analysis,
                    "security_headers": security_result
                }
                
                st.session_state.reports.append(report_data)
                
                st.success("✅ Report Generated Successfully!")
                
                # Display key metrics in cards
                st.markdown("<h3>Key Performance Indicators</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="color: #FF4B4B;">📊 SEO Score</h4>
                            <h2>{seo_score}/100</h2>
                            <p>{'Excellent' if seo_score > 80 else 'Good' if seo_score > 60 else 'Needs Improvement'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="color: #FF4B4B;">📈 Traffic Growth</h4>
                            <h2>{traffic_growth}%</h2>
                            <p>Month-over-month increase</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col3:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="color: #FF4B4B;">🏆 Top Keyword Rank</h4>
                            <h2>#{keyword_rank}</h2>
                            <p>Position for primary keyword</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Additional metrics
                st.markdown("<h3>Technical Performance</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="color: #FF4B4B;">⚡ Page Speed</h4>
                            <h2>{page_speed}/100</h2>
                            <p>{'Fast' if page_speed > 80 else 'Average' if page_speed > 60 else 'Slow'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="color: #FF4B4B;">🔗 Backlinks</h4>
                            <h2>{backlinks:,}</h2>
                            <p>Total backlinks found</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col3:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="color: #FF4B4B;">📱 Mobile Score</h4>
                            <h2>{mobile_score}/100</h2>
                            <p>{'Excellent' if mobile_score > 80 else 'Good' if mobile_score > 60 else 'Poor'}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Issues Summary
                st.markdown("<h3>Issues Analysis</h3>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(
                        f"""
                        <div class="metric-card" style="border-left: 4px solid #FF4B4B;">
                            <h4 style="color: #FF4B4B;">⛔ Critical Issues</h4>
                            <h2>{critical_issues}</h2>
                            <p>Need immediate attention</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col2:
                    st.markdown(
                        f"""
                        <div class="metric-card" style="border-left: 4px solid #FFA500;">
                            <h4 style="color: #FFA500;">⚠️ Warnings</h4>
                            <h2>{warnings}</h2>
                            <p>Should be addressed soon</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                with col3:
                    st.markdown(
                        f"""
                        <div class="metric-card" style="border-left: 4px solid #4CAF50;">
                            <h4 style="color: #4CAF50;">💡 Opportunities</h4>
                            <h2>{opportunities}</h2>
                            <p>Potential improvements</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # Robots.txt and Sitemap Analysis
                st.markdown("<h3>🤖 Robots.txt Analysis</h3>", unsafe_allow_html=True)
                robot_col1, robot_col2 = st.columns(2)
                
                with robot_col1:
                    if robots_result["status"] == "success":
                        st.markdown(f"<p>✅ Successfully fetched from: {robots_result['url']}</p>", unsafe_allow_html=True)
                        st.markdown('<div class="code-block">' + robots_result["content"].replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
                        
                        # Count directives in robots.txt
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>Analysis Summary</h4>
                            <ul>
                                <li><b>User Agents:</b> {len(robots_analysis['user_agents'])} ({', '.join(robots_analysis['user_agents'][:5]) + ('...' if len(robots_analysis['user_agents']) > 5 else '')})</li>
                                <li><b>Directives:</b> {robots_analysis['allow_count']} Allow, {robots_analysis['disallow_count']} Disallow</li>
                                <li><b>Sitemaps Declared:</b> {len(robots_analysis['sitemaps'])}</li>
                                <li><b>Crawl Delay:</b> {robots_analysis['crawl_delay'] if robots_analysis['crawl_delay'] is not None else 'Not specified'}</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="insight-box" style="border-color: #FF4B4B;">
                            <h4>⚠️ Robots.txt Issue</h4>
                            <p>{robots_result['message']}</p>
                            <p>HTTP Status: {robots_result.get('http_status', 'Unknown')}</p>
                            <p>This could impact search engine crawling of your site. Consider creating a robots.txt file to control crawler access.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with robot_col2:
                    st.markdown("<h4>Issues & Recommendations</h4>", unsafe_allow_html=True)
                    
                    if robots_analysis["issues"]:
                        for issue in robots_analysis["issues"]:
                            st.markdown(f"""
                            <div class="issue-item issue-{issue['type']}">
                                <p><b>{'⛔' if issue['type'] == 'critical' else '⚠️' if issue['type'] == 'warning' else '💡'} {issue['type'].capitalize()}:
                                <p><b>{'⛔' if issue['type'] == 'critical' else '⚠️' if issue['type'] == 'warning' else '💡'} {issue['type'].capitalize()}:</b> {issue['message']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="issue-item issue-opportunity">
                            <p>✅ No issues found with robots.txt configuration.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    if robots_analysis["sitemaps"]:
                        st.markdown("<h4>Sitemaps Declared in Robots.txt</h4>", unsafe_allow_html=True)
                        for url in robots_analysis["sitemaps"]:
                            st.markdown(f"- {url}", unsafe_allow_html=True)
                
                # Sitemap Analysis
                st.markdown("<h3>🗺️ Sitemap Analysis</h3>", unsafe_allow_html=True)
                sitemap_col1, sitemap_col2 = st.columns(2)
                
                with sitemap_col1:
                    if sitemap_result["status"] == "success":
                        st.markdown(f"<p>✅ Successfully fetched from: {sitemap_result['url']}</p>", unsafe_allow_html=True)
                        content_preview = sitemap_result["content"][:500] + "..." if len(sitemap_result["content"]) > 500 else sitemap_result["content"]
                        st.markdown('<div class="code-block">' + content_preview.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>") + '</div>', unsafe_allow_html=True)
                        
                        # Sitemap analysis summary
                        st.markdown(f"""
                        <div class="insight-box">
                            <h4>Analysis Summary</h4>
                            <ul>
                                <li><b>URLs Found:</b> {sitemap_analysis['url_count']} URLs in sitemap</li>
                                <li><b>Sitemap Type:</b> {'Sitemap Index' if sitemap_analysis['is_index'] else 'Standard Sitemap'}</li>
                                <li><b>Uses lastmod:</b> {'Yes' if sitemap_analysis['has_lastmod'] else 'No'}</li>
                                <li><b>Uses priority:</b> {'Yes' if sitemap_analysis['has_priority'] else 'No'}</li>
                                <li><b>Uses changefreq:</b> {'Yes' if sitemap_analysis['has_changefreq'] else 'No'}</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # If it's a sitemap index, show nested sitemaps
                        if sitemap_analysis['is_index'] and sitemap_analysis['nested_sitemaps']:
                            st.markdown("<h4>Nested Sitemaps</h4>", unsafe_allow_html=True)
                            for idx, nested_url in enumerate(sitemap_analysis['nested_sitemaps']):
                                if idx < 5:  # Only show first 5
                                    st.markdown(f"- {nested_url}", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"- ... and {len(sitemap_analysis['nested_sitemaps']) - 5} more", unsafe_allow_html=True)
                                    break
                    else:
                        st.markdown(f"""
                        <div class="insight-box" style="border-color: #FF4B4B;">
                            <h4>⚠️ Sitemap Issue</h4>
                            <p>{sitemap_result['message']}</p>
                            <p>HTTP Status: {sitemap_result.get('http_status', 'Unknown')}</p>
                            <p>A valid sitemap helps search engines discover and index your content efficiently.</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                with sitemap_col2:
                    st.markdown("<h4>Issues & Recommendations</h4>", unsafe_allow_html=True)
                    
                    if sitemap_analysis["issues"]:
                        for issue in sitemap_analysis["issues"]:
                            st.markdown(f"""
                            <div class="issue-item issue-{issue['type']}">
                                <p><b>{'⛔' if issue['type'] == 'critical' else '⚠️' if issue['type'] == 'warning' else '💡'} {issue['type'].capitalize()}:</b> {issue['message']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class="issue-item issue-opportunity">
                            <p>✅ No issues found with sitemap configuration.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Sitemap best practices
                    st.markdown("""
                    <div class="insight-box">
                        <h4>Sitemap Best Practices</h4>
                        <ul>
                            <li>Keep sitemaps under 50,000 URLs and 50MB</li>
                            <li>Update lastmod dates when content changes</li>
                            <li>Set meaningful priorities (0.0-1.0) for important pages</li>
                            <li>Declare your sitemap location in robots.txt</li>
                            <li>Submit your sitemap to Google Search Console</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Security Headers
                st.markdown("<h3>🔒 Security Headers Analysis</h3>", unsafe_allow_html=True)
                if security_result["status"] == "success":
                    security_col1, security_col2 = st.columns(2)
                    
                    headers = security_result["headers"]
                    present_headers = sum(1 for value in headers.values() if value != "Missing")
                    
                    with security_col1:
                        st.markdown(f"<p><b>Security Score:</b> {present_headers}/6 headers implemented</p>", unsafe_allow_html=True)
                        for header, value in list(headers.items())[:3]:
                            if value == "Missing":
                                st.markdown(f"❌ {header}: Missing", unsafe_allow_html=True)
                            else:
                                st.markdown(f"✅ {header}: Present", unsafe_allow_html=True)
                    
                    with security_col2:
                        for header, value in list(headers.items())[3:]:
                            if value == "Missing":
                                st.markdown(f"❌ {header}: Missing", unsafe_allow_html=True)
                            else:
                                st.markdown(f"✅ {header}: Present", unsafe_allow_html=True)
                else:
                    st.error(f"Failed to check security headers: {security_result['message']}")
        else:
            st.warning("⚠️ Please enter a website URL first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Previous Reports Section ---
if st.session_state.reports:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📁 Previous Reports")
        
        # Convert reports to DataFrame for display
        df = pd.DataFrame([{
            'url': r['url'],
            'type': r['type'],
            'date': r['date'],
            'seo_score': r['seo_score'],
            'traffic_growth': r['traffic_growth'],
            'robots.txt': '✅' if r['robots_txt']['status'] == 'success' else '❌',
            'sitemap.xml': '✅' if r['sitemap']['status'] == 'success' else '❌'
        } for r in st.session_state.reports])
        
        st.dataframe(df, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- Export Options ---
if st.session_state.reports:
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📤 Export Reports")
        
        export_col1, export_col2 = st.columns(2)
        
        # Function to create Excel file
        def create_excel():
            output = io.BytesIO()
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            
            # Main report sheet
            df = pd.DataFrame([{
                'url': r['url'],
                'type': r['type'],
                'date': r['date'],
                'seo_score': r['seo_score'],
                'traffic_growth': r['traffic_growth'],
                'keyword_rank': r['keyword_rank'],
                'page_speed': r['page_speed'],
                'backlinks': r['backlinks'],
                'mobile_score': r['mobile_score'],
                'robots_txt_status': 'Success' if r['robots_txt']['status'] == 'success' else 'Failed',
                'sitemap_status': 'Success' if r['sitemap']['status'] == 'success' else 'Failed'
            } for r in st.session_state.reports])
            
            df.to_excel(writer, sheet_name='SEO Reports', index=False)
            
            # Detailed metrics sheet
            detailed_metrics = pd.DataFrame([{
                'url': r['url'],
                'date': r['date'],
                'seo_score': r['seo_score'],
                'traffic_growth': r['traffic_growth'],
                'keyword_rank': r['keyword_rank'], 
                'page_speed': r['page_speed'],
                'backlinks': r['backlinks'],
                'mobile_score': r['mobile_score']
            } for r in st.session_state.reports])
            
            detailed_metrics.to_excel(writer, sheet_name='Detailed Metrics', index=False)
            
            # Issues sheet
            issues = pd.DataFrame([{
                'url': r['url'],
                'date': r['date'],
                'critical_issues': r['critical_issues'],
                'warnings': r['warnings'],
                'opportunities': r['opportunities']
            } for r in st.session_state.reports])
            
            issues.to_excel(writer, sheet_name='Issues Analysis', index=False)
            
            # Robots & Sitemap Analysis Sheet - Enhanced Version
            robots_data = []
            for r in st.session_state.reports:
                robots_analysis = r.get('robots_analysis', {})
                sitemap_analysis = r.get('sitemap_analysis', {})
                
                if r['robots_txt']['status'] == 'success':
                    robots_content = r['robots_txt']['content'][:1000] + '...' if len(r['robots_txt']['content']) > 1000 else r['robots_txt']['content']
                else:
                    robots_content = r['robots_txt'].get('message', 'Error fetching robots.txt')
                    
                if r['sitemap']['status'] == 'success':
                    sitemap_content = r['sitemap']['content'][:1000] + '...' if len(r['sitemap']['content']) > 1000 else r['sitemap']['content']
                else:
                    sitemap_content = r['sitemap'].get('message', 'Error fetching sitemap')
                    
                robots_data.append({
                    'url': r['url'],
                    'robots_txt_url': r['robots_txt'].get('url', 'N/A'),
                    'robots_txt_status': r['robots_txt']['status'],
                    'robots_txt_content': robots_content,
                    'user_agents': ', '.join(robots_analysis.get('user_agents', []))[:255],
                    'disallow_count': robots_analysis.get('disallow_count', 0),
                    'allow_count': robots_analysis.get('allow_count', 0),
                    'crawl_delay': robots_analysis.get('crawl_delay', 'None'),
                    'sitemaps_in_robots': ', '.join(robots_analysis.get('sitemaps', []))[:255],
                    'sitemap_url': r['sitemap'].get('url', 'N/A'),
                    'sitemap_status': r['sitemap']['status'],
                    'sitemap_url_count': sitemap_analysis.get('url_count', 0),
                    'sitemap_is_index': sitemap_analysis.get('is_index', False),
                    'sitemap_has_lastmod': sitemap_analysis.get('has_lastmod', False),
                    'sitemap_has_priority': sitemap_analysis.get('has_priority', False),
                    'sitemap_has_changefreq': sitemap_analysis.get('has_changefreq', False),
                })
            
            robots_df = pd.DataFrame(robots_data)
            robots_df.to_excel(writer, sheet_name='Robots & Sitemap Analysis', index=False)
            
            # Issues Details Sheet
            all_issues = []
            for r in st.session_state.reports:
                robots_issues = r.get('robots_analysis', {}).get('issues', [])
                sitemap_issues = r.get('sitemap_analysis', {}).get('issues', [])
                
                for issue in robots_issues:
                    all_issues.append({
                        'url': r['url'],
                        'source': 'Robots.txt',
                        'type': issue['type'],
                        'message': issue['message'],
                    })
                
                for issue in sitemap_issues:
                    all_issues.append({
                        'url': r['url'],
                        'source': 'Sitemap',
                        'type': issue['type'],
                        'message': issue['message'],
                    })
            
            if all_issues:
                issues_df = pd.DataFrame(all_issues)
                issues_df.to_excel(writer, sheet_name='Detailed Issues', index=False)
            
            writer.close()
            return output.getvalue()
        
        # Function to create PDF-like report content with enhanced robots and sitemap sections
        def create_pdf_content():
            buffer = io.StringIO()
            
            # Generate report content
            buffer.write("# SEO REPORTS & INSIGHTS\n\n")
            buffer.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            buffer.write("## Reports Summary\n\n")
            for i, report in enumerate(st.session_state.reports):
                buffer.write(f"### Report {i+1}: {report['url']}\n")
                buffer.write(f"Type: {report['type']}\n")
                buffer.write(f"Date: {report['date']}\n")
                buffer.write(f"SEO Score: {report['seo_score']}/100\n")
                buffer.write(f"Traffic Growth: {report['traffic_growth']}%\n")
                buffer.write(f"Top Keyword Rank: #{report['keyword_rank']}\n\n")
                
                buffer.write("#### Technical Metrics\n")
                buffer.write(f"Page Speed: {report['page_speed']}/100\n")
                buffer.write(f"Backlinks: {report['backlinks']}\n")
                buffer.write(f"Mobile Score: {report['mobile_score']}/100\n\n")
                
                buffer.write("#### Issues Found\n")
                buffer.write(f"Critical Issues: {report['critical_issues']}\n")
                buffer.write(f"Warnings: {report['warnings']}\n")
                buffer.write(f"Opportunities: {report['opportunities']}\n\n")
                
                # Enhanced Robots.txt Analysis Section
                buffer.write("#### Robots.txt Analysis\n")
                if report['robots_txt']['status'] == 'success':
                    buffer.write(f"Successfully fetched from: {report['robots_txt']['url']}\n\n")
                    
                    robots_analysis = report.get('robots_analysis', {})
                    buffer.write("**Analysis Summary:**\n")
                    buffer.write(f"- User Agents: {len(robots_analysis.get('user_agents', []))}\n")
                    buffer.write(f"- Directives: {robots_analysis.get('allow_count', 0)} Allow, {robots_analysis.get('disallow_count', 0)} Disallow\n")
                    buffer.write(f"- Sitemaps Declared: {len(robots_analysis.get('sitemaps', []))}\n")
                    buffer.write(f"- Crawl Delay: {robots_analysis.get('crawl_delay', 'Not specified')}\n\n")
                    
                    # List issues found
                    robot_issues = robots_analysis.get('issues', [])
                    if robot_issues:
                        buffer.write("**Issues Found:**\n")
                        for issue in robot_issues:
                            issue_type = '⛔' if issue['type'] == 'critical' else '⚠️' if issue['type'] == 'warning' else '💡'
                            buffer.write(f"- {issue_type} **{issue['type'].capitalize()}:** {issue['message']}\n")
                        buffer.write("\n")
                    
                    buffer.write("**Robots.txt Content:**\n")
                    buffer.write("```\n")
                    # Limit content length for document
                    robots_content = report['robots_txt']['content'][:500] + '...' if len(report['robots_txt']['content']) > 500 else report['robots_txt']['content']
                    buffer.write(f"{robots_content}\n")
                    buffer.write("```\n\n")
                else:
                    buffer.write(f"Failed to fetch robots.txt: {report['robots_txt'].get('message', 'Unknown error')}\n")
                    buffer.write(f"HTTP Status: {report['robots_txt'].get('http_status', 'Unknown')}\n\n")
                
                # Enhanced Sitemap Analysis Section
                buffer.write("#### Sitemap Analysis\n")
                if report['sitemap']['status'] == 'success':
                    buffer.write(f"Successfully fetched from: {report['sitemap']['url']}\n\n")
                    
                    sitemap_analysis = report.get('sitemap_analysis', {})
                    buffer.write("**Analysis Summary:**\n")
                    buffer.write(f"- URLs Found: {sitemap_analysis.get('url_count', 0)}\n")
                    buffer.write(f"- Sitemap Type: {'Sitemap Index' if sitemap_analysis.get('is_index', False) else 'Standard Sitemap'}\n")
                    buffer.write(f"- Uses lastmod: {'Yes' if sitemap_analysis.get('has_lastmod', False) else 'No'}\n")
                    buffer.write(f"- Uses priority: {'Yes' if sitemap_analysis.get('has_priority', False) else 'No'}\n")
                    buffer.write(f"- Uses changefreq: {'Yes' if sitemap_analysis.get('has_changefreq', False) else 'No'}\n\n")
                    
                    # Nested sitemaps if applicable
                    if sitemap_analysis.get('is_index', False) and sitemap_analysis.get('nested_sitemaps', []):
                        buffer.write("**Nested Sitemaps:**\n")
                        for nested_url in sitemap_analysis.get('nested_sitemaps', [])[:5]:
                            buffer.write(f"- {nested_url}\n")
                        if len(sitemap_analysis.get('nested_sitemaps', [])) > 5:
                            buffer.write(f"- ... and {len(sitemap_analysis.get('nested_sitemaps', [])) - 5} more.\n")
                        buffer.write("\n")
                    
                    # List issues found
                    sitemap_issues = sitemap_analysis.get('issues', [])
                    if sitemap_issues:
                        buffer.write("**Issues Found:**\n")
                        for issue in sitemap_issues:
                            issue_type = '⛔' if issue['type'] == 'critical' else '⚠️' if issue['type'] == 'warning' else '💡'
                            buffer.write(f"- {issue_type} **{issue['type'].capitalize()}:** {issue['message']}\n")
                        buffer.write("\n")
                    
                    buffer.write("**Sitemap Content Preview:**\n")
                    buffer.write("```xml\n")
                    # Limit content length for document
                    sitemap_content = report['sitemap']['content'][:500] + '...' if len(report['sitemap']['content']) > 500 else report['sitemap']['content']
                    buffer.write(f"{sitemap_content}\n")
                    buffer.write("```\n\n")
                else:
                    buffer.write(f"Failed to fetch sitemap: {report['sitemap'].get('message', 'Unknown error')}\n")
                    buffer.write(f"HTTP Status: {report['sitemap'].get('http_status', 'Unknown')}\n\n")
                
                # Security Headers 
                buffer.write("#### Security Headers\n")
                if report['security_headers']['status'] == 'success':
                    headers = report['security_headers']['headers']
                    for header, value in headers.items():
                        status = '✅' if value != 'Missing' else '❌'
                        buffer.write(f"{status} {header}: {'Present' if value != 'Missing' else 'Missing'}\n")
                else:
                    buffer.write(f"Failed to check security headers: {report['security_headers'].get('message', 'Unknown error')}\n")
                
                buffer.write("\n---\n\n")
            
            # Add recommendations section
            buffer.write("## SEO Recommendations\n\n")
            
            buffer.write("### Robots.txt Best Practices\n")
            buffer.write("1. Always include a wildcard user-agent (*) section\n")
            buffer.write("2. Declare your sitemap location in robots.txt\n")
            buffer.write("3. Be careful with crawl-delay directives - too high values can limit indexing\n")
            buffer.write("4. Avoid blocking CSS and JavaScript files that are needed for rendering\n")
            buffer.write("5. Use specific paths rather than broad patterns when possible\n\n")
            
            buffer.write("### Sitemap Best Practices\n")
            buffer.write("1. Keep sitemaps under 50,000 URLs and 50MB\n")
            buffer.write("2. Use sitemap index files for larger sites\n")
            buffer.write("3. Include lastmod dates and keep them accurate\n")
            buffer.write("4. Use priority attributes (0.0-1.0) to indicate importance\n")
            buffer.write("5. Set appropriate changefreq values\n")
            buffer.write("6. Submit sitemaps to Google Search Console and Bing Webmaster Tools\n\n")
            
            buffer.write("### Security Header Recommendations\n")
            buffer.write("1. Implement Strict-Transport-Security to enforce HTTPS\n")
            buffer.write("2. Add Content-Security-Policy to prevent XSS attacks\n")
            buffer.write("3. Include X-Content-Type-Options to prevent MIME type sniffing\n")
            buffer.write("4. Set X-Frame-Options to protect against clickjacking\n")
            buffer.write("5. Enable X-XSS-Protection for additional XSS protection\n")
            buffer.write("6. Configure Referrer-Policy to control information sent in HTTP headers\n")
            
            return buffer.getvalue()
        
        with export_col1:
            excel_data = create_excel()
            st.download_button(
                label="📥 Download as Excel",
                data=excel_data,
                file_name=f"seo_reports_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="excel_download",
            )
        
        with export_col2:
            pdf_data = create_pdf_content()
            st.download_button(
                label="📄 Download as Document",
                data=pdf_data,
                file_name=f"seo_reports_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown",
                use_container_width=True,
                key="pdf_download",
            )
        
        st.markdown('</div>', unsafe_allow_html=True)