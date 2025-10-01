#!/usr/bin/env python3
"""
Cold Calling Assistant - Standalone Streamlit App
A comprehensive tool for finding business contacts and generating cold calling scripts
"""

import streamlit as st
import pandas as pd
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import sys
import io
import base64
from dotenv import load_dotenv
import googlemaps
import requests
import openai

# Load environment variables
load_dotenv()

# Demo data for testing
DEMO_BUSINESSES = [
    {
        "name": "Demo Restaurant",
        "address": "123 Main St, New York, NY 10001",
        "phone": "+1-555-0123",
        "website": "https://demo-restaurant.com",
        "website_live": True,
        "rating": 4.5,
        "total_ratings": 120,
        "place_id": "demo_1",
        "google_url": "https://maps.google.com/?cid=demo1"
    },
    {
        "name": "Sample Marketing Agency",
        "address": "456 Business Ave, New York, NY 10002",
        "phone": "+1-555-0456",
        "website": "https://sample-agency.com",
        "website_live": True,
        "rating": 4.2,
        "total_ratings": 85,
        "place_id": "demo_2",
        "google_url": "https://maps.google.com/?cid=demo2"
    },
    {
        "name": "Local Coffee Shop",
        "address": "789 Coffee St, New York, NY 10003",
        "phone": "+1-555-0789",
        "website": "https://local-coffee.com",
        "website_live": False,
        "rating": 4.8,
        "total_ratings": 200,
        "place_id": "demo_3",
        "google_url": "https://maps.google.com/?cid=demo3"
    }
]

def get_demo_script(user_service: str, search_query: str, business_name: str) -> str:
    """Generate a demo script for testing"""
    return f"""Hi, this is [Your Name] calling from [Your Company]. 

I noticed {business_name} is a {search_query} business, and I specialize in {user_service}. 

Many {search_query} businesses like yours struggle with [specific pain point]. We've helped similar businesses increase their [specific benefit] by [percentage]%.

[PAUSE for response]

Would you be interested in a quick 5-minute conversation about how we could help {business_name} achieve similar results?"""

# API KEYS FROM ENVIRONMENT VARIABLES
GOOGLE_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

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
    """Rate limiting and bot avoidance with hardcoded limits"""
    
    # Hardcoded rate limits for public sharing
    MAX_DAILY_SEARCHES = 50  # Reduced for public sharing
    BOT_DETECTION_THRESHOLD = 30  # Lower threshold for public use
    MAX_CONCURRENT_REQUESTS = 3  # Reduced for stability
    
    @staticmethod
    def get_daily_key():
        """Get today's date key for rate limiting"""
        return datetime.now().strftime('%Y-%m-%d')
    
    @staticmethod
    def check_rate_limit(user_id: str, max_daily: int = None) -> tuple[bool, int]:
        """
        Check if user is within rate limits
        Returns: (is_allowed, remaining_searches)
        """
        if max_daily is None:
            max_daily = RateLimiter.MAX_DAILY_SEARCHES
            
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
        
        # Flag if user gets more than threshold contacts in a day (potential bot)
        return user_contacts > RateLimiter.BOT_DETECTION_THRESHOLD

class BusinessSearcher:
    """Standalone business searcher using Google Places API"""
    
    def __init__(self, api_key: str):
        """Initialize the business searcher"""
        self.api_key = api_key
        self.gmaps = googlemaps.Client(key=api_key)
    
    def search_businesses(self, location: str, business_type: str, radius: int = 3000) -> List[Dict]:
        """
        Search for businesses using Google Places API
        
        Args:
            location: Location to search (e.g., "New York, NY")
            business_type: Type of business to search for (e.g., "restaurant", "SEO agency", "plumber")
            radius: Search radius in meters (default 3000m = 3km)
        
        Returns:
            List of business dictionaries with basic info
        """
        try:
            # Geocode the location
            geocode_result = self.gmaps.geocode(location)
            if not geocode_result:
                st.error(f"Could not find location: {location}")
                return []
            
            lat = geocode_result[0]['geometry']['location']['lat']
            lng = geocode_result[0]['geometry']['location']['lng']
            
            # Search for places
            places_result = self.gmaps.places_nearby(
                location=(lat, lng),
                radius=radius,
                type='establishment',
                keyword=business_type
            )
            
            businesses = []
            for place in places_result.get('results', []):
                business = {
                    'name': place.get('name', 'Unknown'),
                    'place_id': place.get('place_id', ''),
                    'address': place.get('vicinity', ''),
                    'rating': place.get('rating', 0),
                    'total_ratings': place.get('user_ratings_total', 0),
                    'types': place.get('types', []),
                    'google_url': f"https://maps.google.com/?cid={place.get('place_id', '')}"
                }
                businesses.append(business)
            
            return businesses
            
        except Exception as e:
            st.error(f"Error searching businesses: {str(e)}")
            return []
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a specific place"""
        try:
            place_details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_address', 'formatted_phone_number', 'website', 'rating', 'user_ratings_total', 'types']
            )
            
            result = place_details.get('result', {})
            return {
                'name': result.get('name', ''),
                'address': result.get('formatted_address', ''),
                'phone': result.get('formatted_phone_number', ''),
                'website': result.get('website', ''),
                'rating': result.get('rating', 0),
                'total_ratings': result.get('user_ratings_total', 0),
                'types': result.get('types', [])
            }
        except Exception as e:
            st.error(f"Error getting place details: {str(e)}")
            return {}

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
            1. Keep it under 30 seconds when spoken (leave time for receiver to respond)
            2. Be extremely direct - get to the point immediately
            3. Start with a specific, relevant hook that grabs attention
            4. Include ONE clear value proposition - no fluff
            5. End with a simple question that requires a yes/no answer
            6. Sound like a real person, not a salesperson
            7. Address the most urgent pain point that {business_type} businesses face
            8. Include natural pauses for the receiver to speak
            9. Use conversational language, not corporate speak

            FORMAT: Write the script as a natural conversation with [PAUSE] markers where the caller should wait for a response. Make it sound like you're talking to a friend, not pitching a product.
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
    """Configure Streamlit page settings with system theme"""
    st.set_page_config(
        page_title="Cold Calling Assistant",
        page_icon="📞",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Clean, system-adaptive CSS
    st.markdown("""
    <style>
    /* System-adaptive styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1000px;
    }
    
    /* Clean header styling */
    .main h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    /* Intuitive card design */
    .business-card {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .business-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Clean button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
    }
    
    /* Input field improvements */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
    }
    
    /* Clean metrics */
    .metric-container {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    
    /* Status indicators */
    .status-success {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 0.5rem;
        color: #065f46;
    }
    
    .status-warning {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        padding: 0.5rem;
        color: #92400e;
    }
    
    .status-error {
        background: #fee2e2;
        border: 1px solid #ef4444;
        border-radius: 6px;
        padding: 0.5rem;
        color: #991b1b;
    }
    
    /* Clean dividers */
    .stDivider {
        margin: 1.5rem 0;
    }
    
    /* Step-by-step layout */
    .step-container {
        background: var(--background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .step-number {
        background: var(--primary-color);
        color: white;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 1rem;
    }
    
    /* Description styling */
    .description-box {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }
    
    .description-box h2 {
        color: #1e293b;
        margin-bottom: 1rem;
    }
    
    .description-box p {
        color: #475569;
        font-size: 1.1rem;
        line-height: 1.6;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def display_business_card(business: Dict, script_generator: Optional[ScriptGenerator], search_query: str):
    """Display an individual business card with calling functionality"""
    with st.container():
        # Create a card-like container
        st.markdown('<div class="business-card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
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
                st.markdown(f'<a href="{call_link}" target="_blank"><button style="background: #10b981; color: white; padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-weight: 500;">📞 Call</button></a>', unsafe_allow_html=True)
            
            # Google Maps link
            if business.get('google_url'):
                st.markdown(f"[🗺️ Maps]({business.get('google_url')})")
        
        with col3:
            # Generate script button
            if st.session_state.user_service:
                if st.button(f"📜 Script", key=f"script_{business.get('place_id', '')}"):
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
                            height=150,
                            key=f"script_text_{business.get('place_id', '')}"
                        )
            else:
                st.info("Set your service below to generate scripts")
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_download_link(df: pd.DataFrame, filename: str) -> str:
    """Create a download link for CSV data"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV</a>'
    return href

def search_businesses_sync(google_api_key: str, location: str, business_type: str, radius: int = 3000):
    """Synchronous wrapper for business search with phone number enrichment"""
    try:
        searcher = BusinessSearcher(api_key=google_api_key)
        businesses = searcher.search_businesses(
            location=location,
            business_type=business_type,
            radius=radius
        )
        
        if not businesses:
            return []
        
        # Enrich with detailed information including phone numbers
        enriched_businesses = []
        for i, business in enumerate(businesses):
            st.write(f"Getting details for business {i+1}/{len(businesses)}: {business.get('name', 'Unknown')}")
            
            if business.get('place_id'):
                details = searcher.get_place_details(business['place_id'])
                # Update business with detailed info
                business.update(details)
                
                # Check if website is live
                if business.get('website'):
                    try:
                        response = requests.head(business['website'], timeout=5)
                        business['website_live'] = response.status_code == 200
                    except:
                        business['website_live'] = False
                else:
                    business['website_live'] = False
                
                enriched_businesses.append(business)
        
        return enriched_businesses
            
    except Exception as e:
        st.error(f"Error searching businesses: {str(e)}")
        return []

def main():
    """Main application function"""
    configure_page()
    
    # Clean header
    st.title("📞 Cold Calling Assistant")
    
    # Description section
    st.markdown("""
    <div class="description-box">
        <h2>🚀 Built by Samer for Founders, Business Owners & Sales Teams</h2>
        <p><strong>Find businesses instantly and generate personalized cold calling scripts with AI.</strong></p>
        <p>Perfect for founders, business owners, salespeople, entrepreneurs, consultants, freelancers, and anyone doing outreach. 
        This tool helps you discover local businesses, get their contact details, and generate custom calling scripts tailored to each prospect.</p>
        <p><strong>How it works:</strong> Search for businesses → Get contact details → Generate AI scripts → Make calls → Close deals!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    st.markdown("### 📋 Quick Instructions")
    st.markdown("""
    1. **Search**: Enter a location and business type (e.g., "restaurants in New York")
    2. **Review**: Browse the results and filter by rating or website status
    3. **Generate Scripts**: Set your service below to get AI-powered calling scripts
    4. **Call**: Use the generated scripts to make personalized cold calls
    5. **Download**: Export all contacts to CSV for your CRM
    """)
    
    # API Status Check
    st.markdown("### 🔧 API Status")
    if GOOGLE_API_KEY:
        st.success("✅ Google Maps API: Configured")
    else:
        st.error("❌ Google Maps API: Missing - Add GOOGLE_MAPS_API_KEY to your environment")
    
    if OPENAI_API_KEY:
        st.success("✅ OpenAI API: Configured")
    else:
        st.warning("⚠️ OpenAI API: Missing - Add OPENAI_API_KEY to your environment")
    
    # Service selection for script generation
    st.markdown("### 🎯 What Do You Do? (Optional - for AI script generation)")
    
    # Predefined service options
    service_options = [
        "Select your service type...",
        "Digital Marketing Services",
        "Web Design & Development", 
        "SEO & Online Visibility",
        "Social Media Management",
        "Google Ads & PPC",
        "Email Marketing",
        "Content Creation",
        "Business Consulting",
        "Financial Services",
        "Insurance Services",
        "Real Estate Services",
        "Legal Services",
        "Accounting & Bookkeeping",
        "HR & Recruitment",
        "IT Support & Services",
        "Cleaning Services",
        "Landscaping & Maintenance",
        "Restaurant Services",
        "Healthcare Services",
        "Other (Custom)"
    ]
    
    selected_service = st.selectbox(
        "Choose your service type:",
        service_options,
        help="This helps generate relevant calling scripts for each business"
    )
    
    # Custom service input if "Other" is selected
    if selected_service == "Other (Custom)":
        custom_service = st.text_input(
            "Describe your service:",
            placeholder="e.g., We help restaurants increase online orders through social media advertising",
            help="Be specific about what you offer and who you help"
        )
        if custom_service:
            st.session_state.user_service = custom_service
    elif selected_service != "Select your service type...":
        st.session_state.user_service = selected_service
    
    # Initialize script generator
    script_generator = None
    if OPENAI_API_KEY:
        try:
            script_generator = ScriptGenerator(OPENAI_API_KEY)
        except Exception as e:
            st.error(f"Error initializing OpenAI: {str(e)}")
    else:
        st.info("💡 AI script generation is available with the pre-configured API key.")
    
    # Check if APIs are configured
    demo_mode = not GOOGLE_API_KEY
    if not GOOGLE_API_KEY:
        st.warning("⚠️ Running in demo mode. Add your Google Maps API key to the .env file for real searches.")
    
    # Step-by-step interface
    st.header("🔍 Step 1: Search for Businesses")
    
    # Search form in a clean container
    with st.container():
        st.markdown('<div class="step-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            location = st.text_input(
                "📍 Location",
                placeholder="e.g., New York, NY or London, UK",
                help="Where do you want to find businesses?"
            )
        
        with col2:
            business_type = st.text_input(
                "🏢 Business Type",
                placeholder="e.g., restaurant, dentist, marketing agency",
                help="What type of businesses are you looking for?"
            )
        
        with col3:
            radius = st.slider(
                "📏 Radius (km)",
                min_value=1,
                max_value=50,
                value=3,
                help="Search radius from the location"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Search button
    if st.button("🔍 Search Businesses", type="primary"):
        # Rate limiting check
        is_allowed, remaining = RateLimiter.check_rate_limit(st.session_state.user_id)
        
        if not is_allowed:
            st.error("❌ You have reached your daily limit of 50 contacts. Please try again tomorrow.")
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
                st.info("🎭 Demo mode: Showing sample data. Add API keys to .env file for real searches.")
            else:
                # Run synchronous search with phone number enrichment
                businesses = search_businesses_sync(
                    google_api_key=GOOGLE_API_KEY,
                    location=location,
                    business_type=business_type,
                    radius=radius * 1000  # Convert km to meters
                )
        
        if businesses:
            # Check if this would exceed contact limit
            contact_count = len(businesses)
            is_allowed_after, _ = RateLimiter.check_rate_limit(st.session_state.user_id, 50 - contact_count)
            
            if not is_allowed_after and not demo_mode:
                st.error(f"❌ This search would give you {contact_count} contacts, which would exceed your daily limit of 50. Please try a smaller search radius or wait until tomorrow.")
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
    
    # Display results section
    if st.session_state.search_completed and st.session_state.current_businesses:
        businesses = st.session_state.current_businesses
        
        st.header("📋 Step 2: Review & Download Results")
        
        # Download CSV option
        if not businesses:
            st.warning("No businesses to display.")
        else:
            df = pd.DataFrame(businesses)
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
        
        # Clear results button
        if st.button("🗑️ Clear Results"):
            st.session_state.current_businesses = []
            st.session_state.search_completed = False
            st.rerun()
        
        # Filter options
        st.subheader("🔍 Filter Results")
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
        
        # Display each business
        st.subheader("📞 Step 3: Generate Scripts & Call")
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
