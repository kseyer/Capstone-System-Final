import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
django.setup()

from services.models import Service
from products.models import Product
from packages.models import Package

print("=" * 60)
print("DIRECT DATABASE QUERY TEST")
print("=" * 60)

# Test Services
services = Service.objects.filter(archived=False)
print(f"\n✅ Services.objects.filter(archived=False).count(): {services.count()}")
print(f"   First service: {services.first().service_name if services.exists() else 'NONE'}")

# Test Products  
products = Product.objects.filter(archived=False)
print(f"\n✅ Products.objects.filter(archived=False).count(): {products.count()}")
print(f"   First product: {products.first().product_name if products.exists() else 'NONE'}")

# Test Packages
packages = Package.objects.filter(archived=False)
print(f"\n✅ Packages.objects.filter(archived=False).count(): {packages.count()}")
print(f"   First package: {packages.first().package_name if packages.exists() else 'NONE'}")

print("\n" + "=" * 60)
print("CONCLUSION: Data exists in database!")
print("=" * 60)
