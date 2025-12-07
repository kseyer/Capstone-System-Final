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

print("=" * 60)
print("VIEW FUNCTION TEST")
print("=" * 60)
print(f"Response status code: {response.status_code}")
print(f"Response content length: {len(response.content)} bytes")

# Parse the HTML to see if services are there
html_content = response.content.decode('utf-8')
if "No services found" in html_content:
    print("\n❌ ERROR: 'No services found' message is in the HTML!")
elif "Anti-Acne" in html_content:
    print("\n✅ SUCCESS: Service data found in HTML!")
else:
    print("\n⚠️  WARNING: No clear indication either way")

# Check if the template received services
print(f"\nSearching for service cards...")
if 'card service-card' in html_content:
    print("✅ Service cards found in HTML")
else:
    print("❌ No service cards found")

print("=" * 60)
