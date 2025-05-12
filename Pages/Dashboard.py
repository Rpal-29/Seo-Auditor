import streamlit as st

# Configure the page
st.set_page_config(
    page_title="Seo-Auditor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
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
     position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #357abd;
        transform: translateY(-1px);
    }
    .feature-card {
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #444;
        transition: transform 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .feature-card-content {
        background-color: #2b2b2b;
        color: white;
    }
    .feature-title {
        font-size: 24px;
        margin-bottom: 10px;
        font-weight: bold;
    }
    .feature-description {
        color: #e0e0e0;
        font-size: 16px;
    }
    .content-feature {
        background-color: #4CAF50;
        background: linear-gradient(135deg, #4CAF50, #2E7D32);
    }
    .content-title {
        color: #E8F5E9;
    }
    .backlinks-feature {
        background-color: #2196F3;
        background: linear-gradient(135deg, #2196F3, #1565C0);
    }
    .backlinks-title {
        color: #E3F2FD;
    }
    .performance-feature {
        background-color: #9C27B0;
        background: linear-gradient(135deg, #9C27B0, #6A1B9A);
    }
    .performance-title {
        color: #F3E5F5;
    }
    .technical-feature {
        background-color: #FF9800;
        background: linear-gradient(135deg, #FF9800, #E65100);
    }
    .technical-title {
        color: #FFF3E0;
    }
    .ai-feature {
        background-color: #F44336;
        background: linear-gradient(135deg, #F44336, #C62828);
    }
    .ai-title {
        color: #FFEBEE;
    }
    .reports-feature {
        background-color: #00BCD4;
        background: linear-gradient(135deg, #00BCD4, #00838F);
    }
    .reports-title {
        color: #E0F7FA;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 32px;
        font-weight: bold;
        color: #2F4F4F;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
    .header-container {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        color: white;
    }
    .input-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .results-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stExpander {
        border: none !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        border-radius: 10px !important;
        margin-bottom: 20px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th {
        background-color: #f2f2f2;
        padding: 8px;
        text-align: left;
        border: 1px solid #ddd;
    }
    td {
        padding: 8px;
        border: 1px solid #ddd;
    }
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    tr:hover {
        background-color: #f1f1f1;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-broken {
        color: #dc3545;
        font-weight: bold;
    }
    .status-redirect {
        color: #ffc107;
        font-weight: bold;
    }
    .gsc-connection {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
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
    .start-button {
      position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #4A90E2;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .start-button:hover {
        background-color: #357abd;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="header-container">
    <h1 style='text-align: center;'>🚀 Welcome To Seo-Auditor Dashboard</h1>
    <h5 style='text-align: center;'>🔍 Audit With Seo-Auditor</h5>
</div>
""", unsafe_allow_html=True)

# Main Features Grid
st.markdown("<h2 style='color: #FF4B4B;'>📌 Key Features</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)


with col1:
    st.markdown("""
    <div class="feature-card content-feature">
        <div class="feature-title content-title">📝 Content Optimization</div>
        <div class="feature-description">
            Optimize your web content to improve search engine 
            readability, keyword density and meta tags.
        </div>
    </div>
    """, unsafe_allow_html=True)
  

with col2:
    st.markdown("""
    <div class="feature-card backlinks-feature">
        <div class="feature-title backlinks-title">🔗 Backlinks & Authority</div>
        <div class="feature-description">
            Extract Backlinks from the website <br>
            Extract Do-follow , No-follow , Broken-links
        </div>
    </div>
    """, unsafe_allow_html=True)
   

with col3:
    st.markdown("""
    <div class="feature-card performance-feature">
        <div class="feature-title performance-title">📈 Site Performance</div>
        <div class="feature-description">
            Analyze and Visualize website-speed <br>
            Get Web Vitals and Performance metrics
        </div>
    </div>
    """, unsafe_allow_html=True)
    
st.markdown("---")
# Additional Features
st.markdown("<h2 style='color: #FF4B4B;'>🛠️ Advanced Features</h2>", unsafe_allow_html=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown("""
    <div class="feature-card technical-feature">
        <div class="feature-title technical-title">⚙️ Technical SEO</div>
        <div class="feature-description">
            Deep dive into technical SEO issues <br>
            canonical URLs,duplicate content, and security headers.
        </div>
    </div>
    """, unsafe_allow_html=True)
 

with col5:
    st.markdown("""
    <div class="feature-card ai-feature">
        <div class="feature-title ai-title">🤖 AI Assistant</div>
        <div class="feature-description">
            Get personalized SEO recommendations <br>
            content suggestions using advanced AI technology.
        </div>
    </div>
    """, unsafe_allow_html=True)
 
st.markdown("---")
# Reports & Insights
st.markdown("<h2 style='color: #FF4B4B;'>📊 Reports & Insights</h2>", unsafe_allow_html=True)

st.markdown("""
<div class="feature-card reports-feature">
    <div class="feature-title reports-title">🎯 Comprehensive Reports</div>
    <div class="feature-description">
        Generate detailed SEO reports <br>
        Get actionable insights for continuous improvement.
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("---")

# Let's Start button styled to match the image
if st.button("🚀 Let's Start", key="start_button"):
    st.switch_page("Pages/1_Home.py")




# Custom CSS for styling
st.markdown("""
<style>
    .sidebar .sidebar-content {
        background-color: #1e1e2d;
    }
    .sidebar-text {
        font-size: 12px;
        color: #a2a3b7;
    }
    .sidebar-title {
        font-weight: 600;
        color: white;
        font-size: 20px;
        margin-bottom: 0;
    }
    .sidebar-subtitle {
        font-size: 12px;
        color: #a2a3b7;
        margin-top: 0;
    }
    .stSelectbox label {
        color: #a2a3b7;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar with logo
with st.sidebar:
    # Logo and branding
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Option 1: Using a local image file
        # logo = Image.open("path_to_your_logo.png")
        # st.image(logo, width=50)
        
        # Option 2: Using a colored div with text as logo
        st.markdown("""
        <div style="background-color: #5d78ff; width: 40px; height: 40px; border-radius: 8px; 
                    display: flex; justify-content: center; align-items: center; text-align: center;">
            <span style="color: white; font-weight: bold; font-size: 16px;">SP</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<p class="sidebar-title">SEO-Auditor</p>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-subtitle">Analytics Dashboard</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    