import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
django.setup()

from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser
from services.views import services_list

# Create a fake request
request = HttpRequest()
request.method = 'GET'
request.GET = {}
request.user = AnonymousUser()

# Call the view
response = services_list(request)

html_content = response.content.decode('utf-8')

# Save to file for inspection
with open('debug_services_page.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Saved HTML to debug_services_page.html")
print(f"File size: {len(html_content)} bytes")

# Check for specific elements
if "Anti-Acne Treatment" in html_content:
    print("✅ Found 'Anti-Acne Treatment' in HTML")
if "₱1599" in html_content or "1599" in html_content:
    print("✅ Found price data in HTML")
if "Book Now" in html_content or "Register to Book" in html_content:
    print("✅ Found booking buttons in HTML")
    
# Count how many service cards
service_count = html_content.count('<div class="col-md-6 col-lg-4">')
print(f"\nFound {service_count} service card containers")
