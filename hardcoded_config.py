"""
Hardcoded API Keys for Public Sharing
Replace these with your actual API keys before sharing
"""

# Google Maps API Key
# Get from: https://developers.google.com/maps/gmp-get-started
# Enable: Places API, Geocoding API
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY_HERE"

# OpenAI API Key  
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"

# Rate Limiting Configuration for Public Use
RATE_LIMITS = {
    "MAX_DAILY_SEARCHES": 50,  # Reduced for public sharing
    "BOT_DETECTION_THRESHOLD": 30,  # Lower threshold for public use
    "MAX_CONCURRENT_REQUESTS": 3,  # Reduced for stability
}

# Usage Instructions for LinkedIn Sharing:
"""
1. Replace the API keys above with your actual keys
2. Update the rate limits if needed
3. The app will work immediately for your LinkedIn connections
4. Rate limiting prevents abuse while allowing legitimate use
5. Users get 50 contacts per day (adjustable)
"""
