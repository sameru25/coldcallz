# Configuration Template for Cold Calling Assistant
# Copy this file to config_local.py and add your actual API keys

class APIKeys:
    """API Key Configuration"""
    
    # Google Maps API Key (required)
    # Get from: https://developers.google.com/maps/gmp-get-started
    # Enable: Places API, Geocoding API
    GOOGLE_MAPS_API_KEY = "your_google_maps_api_key_here"
    
    # OpenAI API Key (optional, for script generation)
    # Get from: https://platform.openai.com/api-keys
    OPENAI_API_KEY = "your_openai_api_key_here"

# Rate Limiting Configuration
class RateLimits:
    """Rate limiting and security settings"""
    
    # Maximum searches per user per day
    MAX_DAILY_SEARCHES = 100
    
    # Bot detection threshold (searches per day)
    BOT_DETECTION_THRESHOLD = 50
    
    # Maximum concurrent API requests
    MAX_CONCURRENT_REQUESTS = 5

# Application Settings
class AppSettings:
    """General application settings"""
    
    # Default search radius in meters
    DEFAULT_SEARCH_RADIUS = 3000  # 3km
    
    # Maximum results per search
    MAX_RESULTS_PER_SEARCH = 20
    
    # Website verification timeout in seconds
    WEBSITE_TIMEOUT = 10 