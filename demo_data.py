"""
Demo data for testing the Cold Calling Assistant without API keys
"""

DEMO_BUSINESSES = [
    {
        'name': 'Tony\'s Italian Bistro',
        'address': '123 Main Street, New York, NY 10001',
        'phone': '(555) 123-4567',
        'website': 'https://tonysitalianbistro.com',
        'website_live': True,
        'rating': 4.5,
        'total_ratings': 245,
        'google_url': 'https://maps.google.com/place/123',
        'business_status': 'OPERATIONAL',
        'types': 'restaurant, food, establishment',
        'place_id': 'demo_place_1'
    },
    {
        'name': 'Downtown Dental Care',
        'address': '456 Oak Avenue, New York, NY 10002',
        'phone': '(555) 234-5678',
        'website': 'https://downtowndental.com',
        'website_live': True,
        'rating': 4.8,
        'total_ratings': 89,
        'google_url': 'https://maps.google.com/place/456',
        'business_status': 'OPERATIONAL',
        'types': 'dentist, health, doctor',
        'place_id': 'demo_place_2'
    },
    {
        'name': 'Elite Marketing Solutions',
        'address': '789 Business District, New York, NY 10003',
        'phone': '(555) 345-6789',
        'website': 'https://elitemarketing.com',
        'website_live': False,
        'rating': 4.2,
        'total_ratings': 67,
        'google_url': 'https://maps.google.com/place/789',
        'business_status': 'OPERATIONAL',
        'types': 'marketing agency, advertising, business service',
        'place_id': 'demo_place_3'
    },
    {
        'name': 'Fresh Brew Coffee',
        'address': '321 Coffee Lane, New York, NY 10004',
        'phone': '(555) 456-7890',
        'website': 'https://freshbrewcoffee.com',
        'website_live': True,
        'rating': 4.6,
        'total_ratings': 156,
        'google_url': 'https://maps.google.com/place/321',
        'business_status': 'OPERATIONAL',
        'types': 'cafe, coffee shop, food',
        'place_id': 'demo_place_4'
    },
    {
        'name': 'Precision Auto Repair',
        'address': '654 Garage Street, New York, NY 10005',
        'phone': '(555) 567-8901',
        'website': '',
        'website_live': False,
        'rating': 4.3,
        'total_ratings': 78,
        'google_url': 'https://maps.google.com/place/654',
        'business_status': 'OPERATIONAL',
        'types': 'car repair, automotive, service',
        'place_id': 'demo_place_5'
    }
]

def get_demo_script(user_service: str, search_query: str, business_name: str) -> str:
    """Generate a demo script for testing"""
    return f"""Hi, this is [Your Name] from [Your Company]. I'm calling because I noticed {business_name} is a {search_query} in the area, and I wanted to reach out about our {user_service}.

I've helped other {search_query} businesses like yours increase their [specific benefit]. For example, we recently helped a similar business increase their monthly revenue by 30% through our targeted approach.

I'd love to show you how this could work for {business_name}. Do you have 2 minutes for a quick conversation about how we might be able to help you achieve similar results?

[Wait for response]

If not now, when would be a better time to chat briefly? I think you'd find our approach interesting, especially given your location and customer base.

Thank you for your time!

---
This is a demo script. Connect your OpenAI API key for personalized, AI-generated scripts.""" 