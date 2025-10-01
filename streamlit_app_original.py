#!/usr/bin/env python3
"""
Cold Calling Assistant - Streamlit App
A comprehensive tool for finding business contacts and generating cold calling scripts
"""

import streamlit as st
import pandas as pd
import json
import time
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import sys
import io
import base64

# Import the existing business search functionality
sys.path.append('./coldcall_maps')
from business_search import BusinessSearcher
from csv_exporter import CSVExporter
from config import Config

# OpenAI for script generation
import openai

# Demo data for testing
from demo_data import DEMO_BUSINESSES, get_demo_script

# Session state management
if 'user_service' not in st.session_state:
    st.session_state.user_service = ""
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'daily_searches' not in st.session_state:
    st.session_state.daily_searches = {}
if 'user_id' not in st.session_state:
    # Create a simple user ID based on session
    st.session_state.user_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
if 'current_businesses' not in st.session_state:
    st.session_state.current_businesses = []
if 'search_completed' not in st.session_state:
    st.session_state.search_completed = False

class RateLimiter:
    """Rate limiting and bot avoidance"""
    
    @staticmethod
    def get_daily_key():
        """Get today's date key for rate limiting"""
        return datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def check_rate_limit(user_id: str, max_daily: int = 100) -> tuple[bool, int]:
        """
        Check if user is within rate limits
        Returns: (is_allowed, remaining_searches)
        """
        daily_key = RateLimiter.get_daily_key()
        
        if daily_key not in st.session_state.daily_searches:
            st.session_state.daily_searches[daily_key] = {}
        
        user_contacts = st.session_state.daily_searches[daily_key].get(user_id, 0)
        remaining = max_daily - user_contacts
        
        return remaining > 0, remaining
    
    @staticmethod
    def increment_contact_count(user_id: str, contact_count: int):
        """Increment user's daily contact count"""
        daily_key = RateLimiter.get_daily_key()
        
        if daily_key not in st.session_state.daily_searches:
            st.session_state.daily_searches[daily_key] = {}
        
        if user_id not in st.session_state.daily_searches[daily_key]:
            st.session_state.daily_searches[daily_key][user_id] = 0
        
        st.session_state.daily_searches[daily_key][user_id] += contact_count
    
    @staticmethod
    def detect_bot_behavior(user_id: str) -> bool:
        """Simple bot detection based on request patterns"""
        daily_key = RateLimiter.get_daily_key()
        
        if daily_key not in st.session_state.daily_searches:
            return False
        
        user_contacts = st.session_state.daily_searches[daily_key].get(user_id, 0)
        
        # Flag if user gets more than 200 contacts in a day (potential bot)
        return user_contacts > 200

class ScriptGenerator:
    """Generate cold calling scripts using OpenAI GPT-4o mini"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_script(self, user_service: str, search_query: str, business_info: Dict) -> str:
        """
        Generate a personalized cold calling script
        
        Args:
            user_service: Service the user provides
            search_query: What the user searched for
            business_info: Information about the business being called
        
        Returns:
            Generated cold calling script
        """
        try:
            business_name = business_info.get('name', 'the business')
            business_type = business_info.get('types', search_query)
            business_location = business_info.get('address', 'your area')
            
            prompt = f"""
            Generate a direct, effective cold calling script for the following scenario:

            CALLER INFORMATION:
            - Service provided: {user_service}
            - Target business type searched: {search_query}

            BUSINESS BEING CALLED:
            - Business name: {business_name}
            - Business type: {business_type}
            - Location: {business_location}
            - Rating: {business_info.get('rating', 'N/A')}

            REQUIREMENTS:
            1. Keep it under 45 seconds when spoken
            2. Be direct and specific - no generic fluff
            3. Immediately establish relevance between your service and their business type
            4. Include a clear, specific value proposition
            5. End with a simple, low-pressure call to action
            6. Sound natural and conversational, not scripted
            7. Address a real pain point that {business_type} businesses typically face

            Make this script results-oriented and practical. Focus on what the business owner cares about: saving time, making money, or solving problems.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert cold calling coach who writes scripts that actually get results. Focus on being direct, valuable, and respectful of the prospect's time."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating script: {str(e)}"

def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Cold Calling Assistant",
        page_icon="📞",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for serif fonts
    st.markdown("""
    <style>
    /* Import serif fonts */
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400&family=Playfair+Display:wght@400;600;700&display=swap');
    
    /* Apply serif fonts to all text elements */
    .main .block-container, 
    .stApp,
    .stMarkdown,
    .stText,
    div[data-testid="stMarkdownContainer"],
    .stSelectbox label,
    .stTextInput label,
    .stTextArea label,
    .stSlider label,
    .stCheckbox label,
    .stButton button,
    .stDownloadButton button,
    .element-container,
    p, h1, h2, h3, h4, h5, h6, span, div, label, input, textarea, select {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
    }
    
    /* Headers with more elegant serif font */
    h1, h2, h3, .stTitle {
        font-family: 'Playfair Display', 'Times New Roman', serif !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar fonts */
    .css-1d391kg,
    .stSidebar,
    .stSidebar .stMarkdown,
    .stSidebar .stText,
    .stSidebar div[data-testid="stMarkdownContainer"],
    .stSidebar .stSelectbox label,
    .stSidebar .stTextInput label,
    .stSidebar .stTextArea label,
    .stSidebar .stCheckbox label,
    .stSidebar p, 
    .stSidebar h1, 
    .stSidebar h2, 
    .stSidebar h3, 
    .stSidebar span, 
    .stSidebar div, 
    .stSidebar label {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
    }
    
    /* Button styling with serif fonts */
    .stButton > button,
    .stDownloadButton > button {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
    }
    
    /* Success/Error messages */
    .stSuccess,
    .stError,
    .stWarning,
    .stInfo {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
    }
    
    /* Metrics and data display */
    .metric-container,
    .stMetric,
    div[data-testid="metric-container"] {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
    }
    
    /* Dataframe and tables */
    .stDataFrame,
    .dataframe {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Crimson Text', 'Times New Roman', serif !important;
        font-weight: 600 !important;
    }
    
    /* Code blocks - keep monospace but serif-like */
    .stCode,
    code,
    pre {
        font-family: 'Courier New', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

def setup_sidebar():
    """Setup sidebar with configuration and service input"""
    st.sidebar.title("🔧 Configuration")
    
    # API Keys section
    st.sidebar.subheader("API Keys")
    
    google_api_key = st.sidebar.text_input(
        "Google Maps API Key",
        type="password",
        help="Required for business search functionality"
    )
    
    openai_api_key = st.sidebar.text_input(
        "OpenAI API Key", 
        type="password",
        help="Required for generating cold calling scripts"
    )
    
    # Service description
    st.sidebar.subheader("Your Service")
    user_service = st.sidebar.text_area(
        "What service do you provide?",
        value=st.session_state.user_service,
        height=100,
        help="Describe your service clearly. This will be used to generate relevant cold calling scripts.",
        placeholder="e.g., 'We provide digital marketing services for local restaurants, helping them increase online orders through social media advertising and Google Ads.'"
    )
    
    if user_service != st.session_state.user_service:
        st.session_state.user_service = user_service
    
    # Rate limiting info
    st.sidebar.subheader("📊 Usage")
    is_allowed, remaining = RateLimiter.check_rate_limit(st.session_state.user_id)
    
    if is_allowed:
        st.sidebar.success(f"✅ {remaining} contacts remaining today")
    else:
        st.sidebar.error("❌ Daily limit reached (100 contacts)")
    
    # Bot detection warning
    if RateLimiter.detect_bot_behavior(st.session_state.user_id):
        st.sidebar.warning("⚠️ High usage detected. Please use responsibly.")
    
    # Usage info
    st.sidebar.info("💡 Limit: 100 contacts per day\n📊 Contacts = total businesses found across all searches")
    
    return google_api_key, openai_api_key

def create_download_link(df: pd.DataFrame, filename: str) -> str:
    """Create a download link for CSV data"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV</a>'
    return href

async def search_businesses_async(google_api_key: str, location: str, business_type: str, radius: int = 3000):
    """Async wrapper for business search"""
    try:
        # Temporarily set the API key in config
        original_key = Config.GOOGLE_MAPS_API_KEY
        Config.GOOGLE_MAPS_API_KEY = google_api_key
        
        async with BusinessSearcher(api_key=google_api_key) as searcher:
            # Search for businesses
            businesses = searcher.search_businesses(
                location=location,
                business_type=business_type,
                radius=radius
            )
            
            if not businesses:
                return []
            
            # Enrich with detailed information
            enriched_businesses = await searcher.enrich_businesses_with_details(businesses)
            return enriched_businesses
            
    except Exception as e:
        st.error(f"Error searching businesses: {str(e)}")
        return []
    finally:
        # Restore original key
        Config.GOOGLE_MAPS_API_KEY = original_key

def display_business_card(business: Dict, script_generator: Optional[ScriptGenerator], search_query: str):
    """Display an individual business card with calling functionality"""
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader(f"📍 {business.get('name', 'Unknown Business')}")
            st.write(f"**Address:** {business.get('address', 'N/A')}")
            st.write(f"**Phone:** {business.get('phone', 'N/A')}")
            
            if business.get('website'):
                website_status = "🟢 Live" if business.get('website_live') else "🔴 Down"
                st.write(f"**Website:** [{business.get('website')}]({business.get('website')}) {website_status}")
            
            if business.get('rating'):
                st.write(f"**Rating:** ⭐ {business.get('rating')} ({business.get('total_ratings', 0)} reviews)")
        
        with col2:
            # Call button
            phone = business.get('phone', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if phone:
                call_link = f"tel:{phone}"
                st.markdown(f'<a href="{call_link}" target="_blank"><button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">📞 Call Now</button></a>', unsafe_allow_html=True)
            
            # Google Maps link
            if business.get('google_url'):
                st.markdown(f"[🗺️ View on Maps]({business.get('google_url')})")
        
        with col3:
            # Generate script button
            if st.session_state.user_service:
                if st.button(f"📜 Generate Script", key=f"script_{business.get('place_id', '')}"):
                    with st.spinner("Generating script..."):
                        if script_generator:
                            script = script_generator.generate_script(
                                st.session_state.user_service,
                                search_query,
                                business
                            )
                        else:
                            # Use demo script if no OpenAI key
                            script = get_demo_script(
                                st.session_state.user_service,
                                search_query,
                                business.get('name', 'the business')
                            )
                        st.text_area(
                            "Cold Calling Script:",
                            script,
                            height=200,
                            key=f"script_text_{business.get('place_id', '')}"
                        )
            else:
                st.info("Set your service in sidebar to generate scripts")
        
        st.divider()

def main():
    """Main application function"""
    configure_page()
    
    # Header
    st.title("📞 Cold Calling Assistant")
    st.markdown("Find businesses and generate personalized cold calling scripts with AI")
    
    # Sidebar configuration
    google_api_key, openai_api_key = setup_sidebar()
    
    # Demo mode toggle
    demo_mode = st.sidebar.checkbox("🎭 Demo Mode (Test without API keys)", value=not google_api_key)
    
    # Check if APIs are configured (unless in demo mode)
    if not google_api_key and not demo_mode:
        st.warning("⚠️ Please enter your Google Maps API key in the sidebar to start searching, or enable Demo Mode.")
        return
    
    # Initialize script generator if OpenAI key is provided
    script_generator = None
    if openai_api_key:
        script_generator = ScriptGenerator(openai_api_key)
    else:
        st.info("💡 Add your OpenAI API key in the sidebar to enable AI script generation.")
    
    # Main search interface
    st.header("🔍 Business Search")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        location = st.text_input(
            "Location",
            placeholder="e.g., New York, NY or London, UK",
            help="Enter the city or area where you want to find businesses"
        )
    
    with col2:
        business_type = st.text_input(
            "Business Type",
            placeholder="e.g., restaurant, dentist, marketing agency",
            help="What type of businesses are you looking for?"
        )
    
    with col3:
        radius = st.slider(
            "Radius (km)",
            min_value=1,
            max_value=50,
            value=3,
            help="Search radius from the location"
        )
    
    # Search button
    if st.button("🔍 Search Businesses", type="primary"):
        # Rate limiting check
        is_allowed, remaining = RateLimiter.check_rate_limit(st.session_state.user_id)
        
        if not is_allowed:
            st.error("❌ You have reached your daily limit of 100 contacts. Please try again tomorrow.")
            return
        
        if RateLimiter.detect_bot_behavior(st.session_state.user_id):
            st.error("❌ Suspicious activity detected. Please contact support if you believe this is an error.")
            return
        
        if not location or not business_type:
            st.error("Please enter both location and business type.")
            return
        
        # Perform search
        with st.spinner(f"Searching for {business_type} businesses near {location}..."):
            if demo_mode:
                # Use demo data
                import time
                time.sleep(1)  # Simulate API delay
                businesses = DEMO_BUSINESSES.copy()
                st.info("🎭 Demo mode: Showing sample data. Enable API keys for real searches.")
            else:
                # Run async search
                businesses = asyncio.run(search_businesses_async(
                    google_api_key=google_api_key,
                    location=location,
                    business_type=business_type,
                    radius=radius * 1000  # Convert km to meters
                ))
        
        if businesses:
            # Check if this would exceed contact limit
            contact_count = len(businesses)
            is_allowed_after, _ = RateLimiter.check_rate_limit(st.session_state.user_id, 100 - contact_count)
            
            if not is_allowed_after and not demo_mode:
                st.error(f"❌ This search would give you {contact_count} contacts, which would exceed your daily limit of 100. Please try a smaller search radius or wait until tomorrow.")
                return
            
            # Increment contact count (only for real searches, not demo)
            if not demo_mode:
                RateLimiter.increment_contact_count(st.session_state.user_id, contact_count)
            
            st.success(f"✅ Found {len(businesses)} businesses!")
            
            # Store search in session state for persistent display
            st.session_state.current_businesses = businesses
            st.session_state.search_completed = True
            
            # Also store in search history
            search_result = {
                'timestamp': datetime.now(),
                'location': location,
                'business_type': business_type,
                'radius': radius,
                'businesses': businesses,
                'count': len(businesses)
            }
            st.session_state.search_history.append(search_result)
            
        else:
            st.warning("No businesses found. Try adjusting your search terms or increasing the radius.")
    
    # Display results section (persistent - doesn't reset when buttons are clicked)
    if st.session_state.search_completed and st.session_state.current_businesses:
        businesses = st.session_state.current_businesses
        
        # Create DataFrame for CSV download
        df = pd.DataFrame(businesses)
        
        # Download CSV option
        if not df.empty:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"business_contacts_{timestamp}.csv"
            
            col1, col2 = st.columns([1, 3])
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv"
                )
            
            with col2:
                st.info(f"💾 Ready to download {len(businesses)} contacts as CSV")
        
        # Display businesses
        st.header("📋 Business Results")
        
        # Add clear results button
        if st.button("🗑️ Clear Results"):
            st.session_state.current_businesses = []
            st.session_state.search_completed = False
            st.rerun()
        
        # Filter options
        col1, col2 = st.columns([1, 1])
        with col1:
            show_only_websites = st.checkbox("Show only businesses with live websites")
        with col2:
            min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, 0.1)
        
        # Apply filters
        filtered_businesses = businesses
        if show_only_websites:
            filtered_businesses = [b for b in filtered_businesses if b.get('website_live', False)]
        if min_rating > 0:
            filtered_businesses = [b for b in filtered_businesses if b.get('rating', 0) >= min_rating]
        
        st.write(f"Showing {len(filtered_businesses)} of {len(businesses)} businesses")
        
        # Display each business - pass the last search query from history
        last_search_query = "business"
        if st.session_state.search_history:
            last_search_query = st.session_state.search_history[-1]['business_type']
        
        for business in filtered_businesses:
            display_business_card(business, script_generator, last_search_query)
    
    # Search history
    if st.session_state.search_history:
        st.header("📊 Search History")
        
        with st.expander("View Previous Searches"):
            for i, search in enumerate(reversed(st.session_state.search_history[-5:])):  # Show last 5
                st.write(f"**{search['timestamp'].strftime('%Y-%m-%d %H:%M')}** - "
                        f"{search['business_type']} near {search['location']} "
                        f"({search['count']} results)")

if __name__ == "__main__":
    main() 