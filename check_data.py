import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
django.setup()

from services.models import Service, ServiceCategory
from products.models import Product
from packages.models import Package

print("=" * 60)
print("DATABASE CHECK")
print("=" * 60)

# Check Services
print("\n📋 SERVICES:")
services = Service.objects.filter(archived=False)
print(f"Total: {services.count()}")
if services.exists():
    print("\nFirst 5 services:")
    for s in services[:5]:
        print(f"  - {s.service_name} (₱{s.price}) - Category: {s.category.name if s.category else 'None'}")

# Check Service Categories
print("\n📁 SERVICE CATEGORIES:")
categories = ServiceCategory.objects.all()
print(f"Total: {categories.count()}")
for cat in categories:
    service_count = Service.objects.filter(category=cat, archived=False).count()
    print(f"  - {cat.name}: {service_count} services")

# Check Products
print("\n🧴 PRODUCTS:")
products = Product.objects.filter(archived=False)
print(f"Total: {products.count()}")
if products.exists():
    print("\nAll products:")
    for p in products:
        print(f"  - {p.product_name} (₱{p.price}) - Stock: {p.stock}")

# Check Packages
print("\n📦 PACKAGES:")
packages = Package.objects.filter(archived=False)
print(f"Total: {packages.count()}")
if packages.exists():
    print("\nFirst 5 packages:")
    for pkg in packages[:5]:
        print(f"  - {pkg.package_name} (₱{pkg.package_price}) - Sessions: {pkg.sessions}")

print("\n" + "=" * 60)
