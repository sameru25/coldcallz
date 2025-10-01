# Replace these lines in streamlit_app.py:


# Use:
import os
from dotenv import load_dotenv
load_dotenv()

HARDCODED_GOOGLE_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'your_fallback_key')
HARDCODED_OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_fallback_key')
