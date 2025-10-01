# Replace these lines in streamlit_app.py:

# Instead of:
# HARDCODED_GOOGLE_API_KEY = "AIzaSyBvOkBwJcDdEfGhIjKlMnOpQrStUvWxYzA"
# HARDCODED_OPENAI_API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"

# Use:
import os
from dotenv import load_dotenv
load_dotenv()

HARDCODED_GOOGLE_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', 'your_fallback_key')
HARDCODED_OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_fallback_key')
