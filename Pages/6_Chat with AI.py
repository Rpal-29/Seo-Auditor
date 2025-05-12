import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  # Updated import for the new OpenAI client
import pandas as pd
import io
import re
import base64
import time
import os
import traceback  # For detailed error logging
from typing import List, Dict, Any, Tuple

load_dotenv()
API_KEY = os.environ.get("OPENAI_API_KEY")
print(API_KEY)

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
        padding: 20px;
    }
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #ddd;
    }
    .stButton>button {
        background-color: #4B6BFF;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #3B5BE0;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
    }
    .chat-message.bot {
        background-color: #f6f6f6;
        border-left: 5px solid #4B6BFF;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex-grow: 1;
    }
    .highlight {
        background-color: rgba(75, 107, 255, 0.1);
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .file-summary {
        background-color: #f0f5ff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 4px solid #4B6BFF;
    }
    .recommendation-box {
        background-color: #f0fff5;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #28a745;
    }
    .upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        transition: all 0.3s;
    }
    .upload-area:hover {
        border-color: #4B6BFF;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Arial', sans-serif;
    }
    .tabs-container {
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: white;
        border-radius: 4px 4px 0px 0px;
        border: 1px solid #ddd;
        border-bottom: none;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4B6BFF !important;
        color: white !important;
    }
    .error-box {
        background-color: #fff0f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #dc3545;
    }
    .warning-box {
        background-color: #fff8e1;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #ffc107;
    }
    .info-box {
        background-color: #e6f7ff;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #1890ff;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def read_excel(uploaded_file) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Read and analyze Excel file"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Basic analysis
        analysis = {
            "columns": df.columns.tolist(),
            "shape": df.shape,
            "summary": df.describe().to_dict(),
            "missing_values": df.isna().sum().to_dict(),
            "preview": df.head(5).to_dict('records')
        }
        
        return df, analysis
    except Exception as e:
        st.error(f"Error reading Excel file: {str(e)}")
        return None, {"error": str(e)}

def read_markdown(uploaded_file) -> Tuple[str, Dict[str, Any]]:
    """Read and analyze Markdown file"""
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        
        # Extract basic structure
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        # Extract structure
        analysis = {
            "length": len(content),
            "headers": [(len(h[0]), h[1]) for h in headers],
            "structure": [f"{'#' * level} {title}" for level, title in [(len(h[0]), h[1]) for h in headers]],
            "preview": content[:500] + ("..." if len(content) > 500 else "")
        }
        
        return content, analysis
    except Exception as e:
        st.error(f"Error reading Markdown file: {str(e)}")
        return None, {"error": str(e)}

def get_api_key():
    """Get API key from various sources with proper error handling"""
    # Try to get API key from session state
    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        return st.session_state.openai_api_key
    
    # Try to get API key from secrets
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass
    
    # Try to get API key from environment variables
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # No API key found
    return None

def get_ai_response(prompt, file_content=None, file_type=None, history=None):
    """Get AI response based on user query and file content"""
    if history is None:
        history = []

    try:
        # Get API key
        api_key = get_api_key()

        if not api_key:
            return ("I cannot generate recommendations without an OpenAI API key. "
                    "Please enter your API key in the settings tab."), history

        # Build initial messages
        system_message = {
            "role": "system",
            "content": "You are a Project Insights AI Assistant that specializes in analyzing project reports and data..."
        }
        
        # Prepare messages
        messages = [system_message]
        
        # Add file context if available
        if file_content is not None and file_type is not None:
            file_context = (
                f"The following is information extracted from an Excel file:\n{file_content}"
                if file_type == "excel"
                else f"The following is content from a Markdown report:\n{file_content}"
            )
            messages.append({"role": "user", "content": file_context})
        
        # Add past API conversation history if available
        if history:
            for msg in history:
                messages.append(msg)

        # Add user prompt
        messages.append({"role": "user", "content": prompt})

        # Get selected model from session state or use default
        model_to_use = st.session_state.get("selected_model", "gpt-3.5-turbo")
        
        # Initialize OpenAI client with API key
        client = OpenAI(api_key=api_key)
        
        # Make API call
        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        ai_message = response.choices[0].message.content

        # Update history
        updated_history = history + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": ai_message}
        ]

        return ai_message, updated_history

    except Exception as e:
        error_message = f"Error: {str(e)}"
        st.error(f"API Error Details: {traceback.format_exc()}")  # Debug logging

        if "auth" in str(e).lower() or "api key" in str(e).lower():
            error_message = "Error: Invalid or missing OpenAI API key. Please check your API key in the settings tab."
        elif "quota" in str(e).lower() or "rate limit" in str(e).lower():
            error_message = "Error: OpenAI API rate limit exceeded or quota reached. Please try again later."

        return error_message, history
        
def display_chat_message(is_user, message, avatar_url=None):
    """Display a chat message with avatar"""
    message_class = "user" if is_user else "bot"
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="message">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def display_file_summary(file_name, file_type, analysis):
    """Display a summary of the uploaded file"""
    with st.expander(f"📄 File Summary: {file_name}", expanded=True):
        if file_type == "excel":
            st.write(f"**Rows x Columns:** {analysis['shape'][0]} x {analysis['shape'][1]}")
            st.write("**Columns:**", ", ".join(analysis['columns']))
            
            # Show preview
            if analysis.get('preview'):
                st.write("**Preview:**")
                st.dataframe(pd.DataFrame(analysis['preview']), height=200)
                
            # Show missing values if any
            missing_values = {k: v for k, v in analysis['missing_values'].items() if v > 0}
            if missing_values:
                st.write("**Missing Values:**")
                for col, count in missing_values.items():
                    st.write(f"- {col}: {count} missing values")
        
        elif file_type == "markdown":
            st.write(f"**Document Length:** {analysis['length']} characters")
            
            if analysis.get('structure'):
                st.write("**Document Structure:**")
                for header in analysis['structure']:
                    st.write(f"- {header}")
            
            if analysis.get('preview'):
                st.write("**Preview:**")
                st.text(analysis['preview'])

def generate_recommendations(file_content, file_type):
    """Generate AI recommendations based on file content"""
    if file_type == "excel":
        prompt = """
        Based on the Excel data provided, please:
        1. Identify key insights and patterns
        2. Provide specific recommendations to improve project outcomes
        3. Highlight any potential issues or areas that need attention
        4. Suggest next steps for the project
        
        Structure your response in a clear, actionable format.
        """
    else:  # markdown
        prompt = """
        Based on the project report provided, please:
        1. Summarize the key findings and current project status
        2. Identify strengths and weaknesses in the project
        3. Provide specific recommendations to improve outcomes
        4. Suggest next steps and areas for further investigation
        
        Structure your response in a clear, actionable format.
        """
    
    # Debug logging
    st.sidebar.write(f"Generating recommendations using model: {st.session_state.get('selected_model', 'gpt-3.5-turbo')}")
    
    recommendations, _ = get_ai_response(prompt, file_content, file_type)
    return recommendations

# --- Initialize Session State ---
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.api_history = []

if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = {}

if 'current_file' not in st.session_state:
    st.session_state.current_file = None

if 'recommendations' not in st.session_state:
    st.session_state.recommendations = {}

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = ""

if 'show_api_key' not in st.session_state:
    st.session_state.show_api_key = False

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "gpt-3.5-turbo"

# --- Main Page Content ---
st.markdown(
    "<h1 style='text-align: center; color: #4B6BFF;'>📊 Project Insights AI Assistant</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<h4 style='text-align: center; color: #555;'>Upload your files, get insights and recommendations</h4>",
    unsafe_allow_html=True,
)

# --- Create main tabs ---
main_tabs = st.tabs(["Upload & Analyze", "Settings", "Help"])

with main_tabs[0]:  # Upload & Analyze Tab
    # --- Sidebar ---
    with st.sidebar:
        st.image("https://api.dicebear.com/7.x/bottts/svg?seed=project-insights", width=120)
        st.title("Project Insights AI")
        st.markdown("---")
        
        st.subheader("About")
        st.write("This AI assistant analyzes your project files and provides recommendations to improve outcomes.")
        
        st.markdown("---")
        
        st.subheader("Supported Files")
        st.write("- Excel (.xlsx, .xls)")
        st.write("- Markdown (.md)")
    
    # --- File Upload Area ---
    with st.container():
        st.markdown("### Upload Files")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Upload Excel or Markdown files", 
                type=["xlsx", "xls", "md"], 
                accept_multiple_files=True,
                key="file_uploader"
            )
        
        with col2:
            if st.button("Process Files", use_container_width=True):
                # Check if API key is available
                api_key = get_api_key()
                if not api_key:
                    st.error("OpenAI API key is missing. Please enter your API key in the Settings tab.")
                elif uploaded_files:
                    with st.spinner("Processing files..."):
                        for uploaded_file in uploaded_files:
                            # Skip if already processed
                            if uploaded_file.name in st.session_state.uploaded_files:
                                continue
                            
                            file_type = uploaded_file.name.split('.')[-1].lower()
                            
                            if file_type in ['xlsx', 'xls']:
                                df, analysis = read_excel(uploaded_file)
                                if df is not None:
                                    file_content = analysis
                                    st.session_state.uploaded_files[uploaded_file.name] = {
                                        "type": "excel",
                                        "content": file_content,
                                        "analysis": analysis
                                    }
                                    
                                    try:
                                        # Generate recommendations with debugging
                                        st.info(f"Generating recommendations for {uploaded_file.name}...")
                                        st.session_state.recommendations[uploaded_file.name] = generate_recommendations(
                                            str(file_content), "excel"
                                        )
                                        st.success(f"Generated recommendations for {uploaded_file.name}")
                                    except Exception as e:
                                        st.error(f"Error generating recommendations: {str(e)}")
                                        st.error(f"Detailed error: {traceback.format_exc()}")
                            
                            elif file_type == 'md':
                                content, analysis = read_markdown(uploaded_file)
                                if content is not None:
                                    st.session_state.uploaded_files[uploaded_file.name] = {
                                        "type": "markdown",
                                        "content": content,
                                        "analysis": analysis
                                    }
                                    
                                    try:
                                        # Generate recommendations with debugging
                                        st.info(f"Generating recommendations for {uploaded_file.name}...")
                                        st.session_state.recommendations[uploaded_file.name] = generate_recommendations(
                                            content, "markdown"
                                        )
                                        st.success(f"Generated recommendations for {uploaded_file.name}")
                                    except Exception as e:
                                        st.error(f"Error generating recommendations: {str(e)}")
                                        st.error(f"Detailed error: {traceback.format_exc()}")
                        
                        # Set current file
                        if st.session_state.uploaded_files and not st.session_state.current_file:
                            st.session_state.current_file = list(st.session_state.uploaded_files.keys())[0]
                        
                        st.success(f"Processed {len(st.session_state.uploaded_files)} files")
                else:
                    st.warning("Please upload files first")
    
    st.markdown("---")
    
    # --- File Selection & Analysis ---
    if st.session_state.uploaded_files:
        analysis_tabs = st.tabs(["Analysis", "Chat"])
        
        with analysis_tabs[0]:  # Analysis Tab
            st.markdown("### File Analysis")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                file_list = list(st.session_state.uploaded_files.keys())
                selected_file = st.selectbox(
                    "Select a file to analyze",
                    file_list,
                    index=file_list.index(st.session_state.current_file) if st.session_state.current_file in file_list else 0
                )
                
                # Update current file
                st.session_state.current_file = selected_file
            
            with col2:
                if st.button("Regenerate Recommendations", use_container_width=True):
                    # Check if API key is available
                    api_key = get_api_key()
                    if not api_key:
                        st.error("OpenAI API key is missing. Please enter your API key in the Settings tab.")
                    else:
                        with st.spinner("Generating recommendations..."):
                            file_data = st.session_state.uploaded_files[selected_file]
                            file_content = file_data["content"]
                            file_type = file_data["type"]
                            
                            try:
                                # Generate recommendations
                                st.session_state.recommendations[selected_file] = generate_recommendations(
                                    str(file_content) if file_type == "excel" else file_content, 
                                    file_type
                                )
                                
                                st.success("Recommendations updated")
                            except Exception as e:
                                st.error(f"Error generating recommendations: {str(e)}")
                                st.error(f"Detailed error: {traceback.format_exc()}")
            
            # Display file summary
            selected_file_data = st.session_state.uploaded_files[selected_file]
            display_file_summary(selected_file, selected_file_data["type"], selected_file_data["analysis"])
            
            # Display recommendations
            if selected_file in st.session_state.recommendations:
                st.markdown("### 🔍 AI Recommendations")
                st.markdown(
                    f'<div class="recommendation-box">{st.session_state.recommendations[selected_file]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("No recommendations generated yet. Try regenerating recommendations.")
        
        with analysis_tabs[1]:  # Chat Tab
            st.markdown("### Chat with AI about your files")
            
            # Check if API key is available and show warning if not
            api_key = get_api_key()
            if not api_key:
                st.warning("OpenAI API key is missing. Please enter your API key in the Settings tab to use the chat feature.")
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.chat_history:
                    display_chat_message(chat["is_user"], chat["message"])
            
            # User input
            user_input = st.text_area(
                "Ask a question about your files",
                value=st.session_state.user_input,
                height=100,
                placeholder="e.g., What are the key trends in this data?",
                key="chat_input"
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Send", use_container_width=True, disabled=not api_key):
                    if user_input:
                        # Store user message
                        st.session_state.chat_history.append({
                            "is_user": True,
                            "message": user_input
                        })
                        
                        # Clear input
                        current_input = user_input
                        st.session_state.user_input = ""
                        
                        # Get current file data if available
                        file_content = None
                        file_type = None
                        if st.session_state.current_file:
                            file_data = st.session_state.uploaded_files[st.session_state.current_file]
                            file_content = file_data["content"]
                            file_type = file_data["type"]
                        
                        # Get AI response
                        with st.spinner("AI is thinking..."):
                            try:
                                ai_response, updated_history = get_ai_response(
                                    current_input, 
                                    file_content, 
                                    file_type,
                                    st.session_state.api_history
                                )
                                
                                # Update API history
                                st.session_state.api_history = updated_history
                                
                                # Store AI response
                                st.session_state.chat_history.append({
                                    "is_user": False,
                                    "message": ai_response
                                })
                            except Exception as e:
                                # Handle error
                                error_msg = f"Error: {str(e)}"
                                st.session_state.chat_history.append({
                                    "is_user": False,
                                    "message": error_msg
                                })
                                st.error(f"Detailed error: {traceback.format_exc()}")
                        
                        # Force rerun to update the chat container
                        st.experimental_rerun()
                    else:
                        st.warning("Please enter a question first")
            
            with col2:
                if st.button("Clear Chat", use_container_width=True):
                    st.session_state.chat_history = []
                    st.session_state.api_history = []
                    st.experimental_rerun()
    
    else:
        st.info("Please upload files to get started")

with main_tabs[1]:  # Settings Tab
    st.markdown("### Settings")
    
    st.markdown("#### OpenAI API Key")
    st.info("Your API key is required to generate recommendations and use the chat feature.")
    
    # API key input with toggle visibility
    col1, col2 = st.columns([3, 1])
    
    with col1:
        api_key_input_type = "password"
        if st.session_state.show_api_key:
            api_key_input_type = "default"
            
        api_key = st.text_input(
            "Enter your OpenAI API key",
            type=api_key_input_type,
            value=st.session_state.openai_api_key,
            help="You can get an API key from platform.openai.com"
        )
    
    with col2:
        if st.button("Show/Hide", use_container_width=True):
            st.session_state.show_api_key = not st.session_state.show_api_key
    
    if st.button("Save API Key", use_container_width=False):
        if api_key:
            # Test the API key validity
            try:
                client = OpenAI(api_key=api_key)
                # Simple test request
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                st.session_state.openai_api_key = api_key
                st.success("API key verified and saved successfully!")
            except Exception as e:
                st.error(f"Invalid API key: {str(e)}")
        else:
            st.error("Please enter a valid API key")
    
    st.markdown("---")
    
    st.markdown("#### Application Settings")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### AI Model")
        selected_model = st.selectbox(
            "Select OpenAI Model",
            ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=2,  # Default to gpt-3.5-turbo
            key="model_selector",
            help="Select the AI model to use for generating recommendations"
        )
        
        # Update the model in session state
        st.session_state.selected_model = selected_model
        
        if st.button("Apply Model Selection"):
            st.success(f"Model set to {selected_model}")
    
    with col2:
        st.markdown("##### File Export")
        st.checkbox(
            "Enable automatic export of recommendations",
            value=False,
            help="Automatically export recommendations to a file"
        )
    
    st.markdown("---")
    
    st.markdown("#### Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear All Data", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.api_history = []
            st.session_state.uploaded_files = {}
            st.session_state.current_file = None
            st.session_state.recommendations = {}
            st.success("All data cleared successfully!")

with main_tabs[2]:  # Help Tab
    st.markdown("### Help & Documentation")
    
    st.markdown("""
    #### Getting Started
    1. **Upload your files** - Use the 'Upload & Analyze' tab to upload Excel spreadsheets or Markdown reports
    2. **Process the files** - Click 'Process Files' to analyze the uploaded files
    3. **View recommendations** - The AI will automatically generate insights and recommendations
    4. **Chat with the AI** - Use the chat tab to ask specific questions about your data
    
    #### Supported File Types
    - **Excel files** (.xlsx, .xls) - For data analysis, tracking, and metrics
    - **Markdown files** (.md) - For project reports, documentation, and notes
    
    #### Tips for Better Analysis
    - Ensure your Excel files have clean, well-structured data
    - Include headers in your Excel files
    - Use proper formatting in your Markdown files
    - Be specific when asking questions in the chat
    
    #### Need More Help?
    If you encounter any issues or have questions, please contact support.
    """)

    # Add debug info toggle
    if st.checkbox("Show Debug Information"):
        st.subheader("Debug Information")
        st.write("Session State:")
        st.json({
            "current_file": st.session_state.get("current_file"),
            "selected_model": st.session_state.get("selected_model"),
            "has_api_key": bool(get_api_key()),
            "files_loaded": len(st.session_state.get("uploaded_files", {})),
            "chat_history_length": len(st.session_state.get("chat_history", [])),
        })

# Remove the duplicate get_ai_response function at the bottom of the original file