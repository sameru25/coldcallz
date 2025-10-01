# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. NumPy/Pandas Compatibility Error

**Error:** `ValueError: numpy.dtype size changed, may indicate binary incompatibility`

**Solution:**
```bash
# Remove old virtual environment
rm -rf venv

# Create new environment
python3 -m venv venv
source venv/bin/activate

# Install numpy first with specific version
pip install --upgrade pip
pip install numpy==1.25.2

# Then install other requirements
pip install -r requirements.txt
```

### 2. Import Errors

**Error:** `ModuleNotFoundError: No module named 'business_search'`

**Solution:**
Make sure you're in the correct directory and the `coldcall_maps` folder exists:
```bash
cd /Users/samer/Downloads/OdjoAI/Outreach_Projects/Streamlit_cold_calling
ls -la coldcall_maps/  # Should show business_search.py and other files
```

### 3. API Key Issues

**Error:** Google Places API errors or OpenAI errors

**Solution:**
1. Verify API keys are correct
2. Check API quotas and billing in respective consoles
3. For Google Places API, ensure these APIs are enabled:
   - Places API
   - Geocoding API
   - Maps JavaScript API

### 4. Port Already in Use

**Error:** `OSError: [Errno 48] Address already in use`

**Solution:**
```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or use a different port
streamlit run streamlit_app.py --server.port 8504
```

### 5. Demo Mode Not Working

**Issue:** Demo mode doesn't show sample data

**Solution:**
Make sure `demo_data.py` exists and enable demo mode in the sidebar checkbox.

### 6. Website Verification Timeout

**Issue:** Website verification takes too long or fails

**Solution:**
This is normal - some websites are slow or block automated requests. The app will continue to work.

### 7. Rate Limiting Too Strict

**Issue:** Hit rate limit too quickly

**Solution:**
You can modify the limits in the app by changing these values:
- Line ~50 in `streamlit_app.py`: `max_daily: int = 100`
- Line ~75 in `streamlit_app.py`: `return user_searches > 50`

## Quick Restart

If you encounter any issues, try this complete restart:
```bash
cd /Users/samer/Downloads/OdjoAI/Outreach_Projects/Streamlit_cold_calling
./run.sh
```

## Getting Help

1. Check this troubleshooting guide
2. Review the main README.md
3. Check Streamlit logs in the terminal
4. Verify API key configuration

## Performance Tips

1. **Use Demo Mode** for testing without API costs
2. **Start with small radius** (3-5km) for faster searches
3. **Filter results** to reduce processing time
4. **Monitor API usage** in Google Cloud Console 