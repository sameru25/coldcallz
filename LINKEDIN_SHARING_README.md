# Cold Calling Assistant - LinkedIn Sharing Version

## 🚀 Ready to Share on LinkedIn!

This version is optimized for sharing with your LinkedIn connections. It includes:

### ✅ Pre-configured Features
- **Hardcoded API Keys**: No setup required for users
- **Rate Limiting**: 50 contacts per day per user
- **Enhanced UI**: Beautiful, modern design
- **AI Script Generation**: Powered by OpenAI GPT-4o mini
- **Business Search**: Google Maps integration

### 🔧 Setup Instructions

1. **Replace API Keys** in `streamlit_app.py`:
   ```python
   HARDCODED_GOOGLE_API_KEY = "your_actual_google_maps_key"
   HARDCODED_OPENAI_API_KEY = "your_actual_openai_key"
   ```

2. **Deploy to Streamlit Cloud**:
   - Push to GitHub
   - Connect to Streamlit Cloud
   - Add your API keys as secrets

3. **Share the Link**:
   - Your LinkedIn connections can use it immediately
   - No registration or setup required

### 🛡️ Built-in Protection
- **Rate Limiting**: Prevents abuse (50 contacts/day per user)
- **Bot Detection**: Flags suspicious usage patterns
- **Cost Control**: Limits API usage to protect your budget

### 💡 LinkedIn Post Template

```
🚀 I've built a Cold Calling Assistant that finds businesses and generates AI-powered scripts!

✅ Find local businesses instantly
✅ Generate personalized calling scripts
✅ Export contacts to CSV
✅ No setup required - just use it!

Try it here: [YOUR_STREAMLIT_URL]

Perfect for sales teams, entrepreneurs, and anyone doing outreach. 

#SalesTools #ColdCalling #AI #BusinessDevelopment
```

### 📊 Usage Analytics
- Monitor daily usage in Streamlit Cloud logs
- Adjust rate limits as needed
- Track which features are most popular

### 🔄 Updates
- Easy to update and redeploy
- Add new features without user setup
- Maintain rate limits for cost control

---

**Ready to share? Just replace the API keys and deploy! 🚀**
