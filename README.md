# 📞 Cold Calling Assistant

A powerful Streamlit application that helps you find business contacts and generate AI-powered cold calling scripts. Built with rate limiting, bot protection, and browser-based calling features.

## 🚀 Features

- **Business Search**: Find businesses using Google Places API with location and business type filters
- **AI Script Generation**: Generate personalized cold calling scripts using GPT-4o mini
- **Browser Calling**: Click-to-call functionality directly from the browser
- **CSV Export**: Download search results as CSV files for offline use
- **Rate Limiting**: Strict 100 contacts per user per day limit to control API costs
- **Bot Protection**: Automatic detection of suspicious usage patterns
- **Service Memory**: Remember your service description for consistent script generation
- **Website Verification**: Check if business websites are live and accessible
- **Search History**: Track your previous searches and results

## 📋 Requirements

- Python 3.8+
- Google Maps API Key (with Places API enabled)
- OpenAI API Key (for script generation)

## 🛠️ Installation

1. **Clone or download this repository**
```bash
git clone <repository-url>
cd Streamlit_cold_calling
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up API Keys**
   - Get a [Google Maps API Key](https://developers.google.com/maps/gmp-get-started) with Places API enabled
   - Get an [OpenAI API Key](https://platform.openai.com/api-keys)

## 🚀 Usage

1. **Start the Streamlit app**
```bash
streamlit run streamlit_app.py
```

2. **Configure API Keys**
   - Enter your Google Maps API key in the sidebar (required)
   - Enter your OpenAI API key in the sidebar (optional, for script generation)

3. **Set Your Service**
   - Describe your service in the sidebar text area
   - This will be used to generate relevant cold calling scripts

4. **Search for Businesses**
   - Enter a location (e.g., "New York, NY")
   - Enter a business type (e.g., "restaurant", "marketing agency")
   - Adjust the search radius (1-50 km)
   - Click "Search Businesses"

5. **Use the Results**
   - **Call Now**: Click the phone number to call directly from your browser
   - **Generate Script**: Click to create a personalized cold calling script
   - **Download CSV**: Export all results as a CSV file
   - **View on Maps**: Open the business location in Google Maps

## 🔒 Security & Rate Limiting

- **Daily Limit**: Maximum 100 contacts per user per day
- **Bot Detection**: Automatic flagging of suspicious activity patterns
- **API Cost Protection**: Built-in safeguards to prevent unexpected charges
- **Session Management**: User tracking without personal data collection

## 📊 Features Overview

### Business Search
- Powered by Google Places API
- Supports any business type
- Customizable search radius
- Live website verification
- Rating and review information

### AI Script Generation
- Uses GPT-4o mini for cost-effective generation
- Personalized based on your service and target business
- Direct, results-oriented scripts (under 45 seconds)
- Addresses real business pain points

### Export & Integration
- CSV download with all business details
- Browser-based calling (tel: links)
- Google Maps integration
- Search history tracking

## 💡 Usage Tips

1. **Be Specific**: Use specific business types for better results (e.g., "SEO agency" vs "agency")
2. **Adjust Radius**: Start with smaller radius (3-5km) for local businesses
3. **Filter Results**: Use the website and rating filters to find high-quality prospects
4. **Save Searches**: Download CSV files to build your prospect database
5. **Script Optimization**: Provide detailed service descriptions for better scripts

## 🔧 Configuration Options

### Search Settings
- **Location**: Any city, state, or country
- **Business Type**: Any industry or profession
- **Radius**: 1-50 kilometers from location
- **Filters**: Website status, minimum rating

### Rate Limiting
- **Daily Limit**: 100 contacts per user
- **Bot Detection**: Flags users with >200 contacts/day
- **API Protection**: Prevents runaway costs

## 📁 File Structure

```
Streamlit_cold_calling/
├── streamlit_app.py          # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── coldcall_maps/           # Business search engine
    ├── business_search.py   # Google Places API integration
    ├── config.py           # Configuration settings
    ├── csv_exporter.py     # CSV export functionality
    └── ...                 # Other support files
```

## 🚨 Important Notes

- **API Costs**: Monitor your Google Places API usage to avoid unexpected charges
- **Rate Limits**: The 100 contacts/day limit helps control costs - increase carefully
- **Data Privacy**: No personal information is stored permanently
- **Terms of Service**: Ensure compliance with Google Places API and OpenAI terms

## 🐛 Troubleshooting

### Common Issues

1. **"No businesses found"**
   - Try broader search terms
   - Increase search radius
   - Check location spelling

2. **API Key Errors**
   - Verify API keys are correct
   - Check API quotas and billing
   - Ensure required APIs are enabled

3. **Script Generation Fails**
   - Verify OpenAI API key
   - Check OpenAI account credits
   - Ensure service description is provided

### Error Messages

- **"Daily limit reached"**: Wait until tomorrow or contact admin
- **"Suspicious activity"**: Contact support if legitimate usage
- **"API quota exceeded"**: Check Google Cloud Console billing

## 📞 Support

For issues or questions:
1. Check this README for common solutions
2. Verify API key configuration
3. Monitor API usage and quotas
4. Review rate limiting settings

## 🔄 Updates & Maintenance

- Regularly monitor API usage and costs
- Update dependencies as needed
- Adjust rate limits based on usage patterns
- Back up important search results

---

**Happy Cold Calling! 📞** 