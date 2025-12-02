"""
Diagnostic script to check date filtering issues in analytics
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'beauty_clinic_django.settings')
django.setup()

from django.utils import timezone
from appointments.models import Appointment
from django.db.models import Min, Max, Count
from django.db.models.functions import TruncWeek

# Get current system date
today = timezone.now().date()
print("=" * 80)
print("DATE FILTERING DIAGNOSTIC REPORT")
print("=" * 80)
print(f"\n1. CURRENT SERVER DATE: {today}")
print(f"   Day of week: {today.strftime('%A')}")

# Check appointment data
total_appointments = Appointment.objects.count()
print(f"\n2. TOTAL APPOINTMENTS IN DATABASE: {total_appointments}")

if total_appointments > 0:
    date_range = Appointment.objects.aggregate(
        min_date=Min('appointment_date'),
        max_date=Max('appointment_date')
    )
    print(f"\n3. APPOINTMENT DATE RANGE:")
    print(f"   Earliest: {date_range['min_date']}")
    print(f"   Latest: {date_range['max_date']}")
    
    # Simulate default filter (30 days)
    filter_start_date = today - timedelta(days=30)
    filter_end_date = today
    
    print(f"\n4. DEFAULT FILTER (30 DAYS):")
    print(f"   Start Date: {filter_start_date}")
    print(f"   End Date: {filter_end_date}")
    
    filtered_count = Appointment.objects.filter(
        appointment_date__gte=filter_start_date,
        appointment_date__lte=filter_end_date
    ).count()
    print(f"   Appointments in range: {filtered_count}")
    
    # Test each preset filter
    print(f"\n5. TESTING ALL PRESET FILTERS:")
    for days, label in [(7, "7 Days"), (30, "30 Days"), (90, "90 Days"), (365, "1 Year")]:
        start = today - timedelta(days=days)
        count = Appointment.objects.filter(
            appointment_date__gte=start,
            appointment_date__lte=today
        ).count()
        print(f"   {label:10} ({start} to {today}): {count} appointments")
    
    # Check for appointments by year
    print(f"\n6. APPOINTMENTS BY YEAR:")
    years = Appointment.objects.dates('appointment_date', 'year')
    for year in years:
        year_count = Appointment.objects.filter(
            appointment_date__year=year.year
        ).count()
        print(f"   {year.year}: {year_count} appointments")
    
    # Check chart data (last 12 weeks)
    chart_start_date = filter_end_date - timedelta(days=84)
    print(f"\n7. CHART DATA (LAST 12 WEEKS):")
    print(f"   Chart Start: {chart_start_date}")
    print(f"   Chart End: {filter_end_date}")
    
    weekly_data = Appointment.objects.filter(
        appointment_date__gte=chart_start_date,
        appointment_date__lte=filter_end_date
    ).annotate(
        week=TruncWeek('appointment_date')
    ).values('week').annotate(
        count=Count('id')
    ).order_by('week')
    
    print(f"   Weeks with data: {weekly_data.count()}")
    if weekly_data.exists():
        print(f"   Data points:")
        for item in weekly_data:
            print(f"      Week starting {item['week']}: {item['count']} appointments")
    
    # Sample appointments
    print(f"\n8. SAMPLE APPOINTMENTS (First 5):")
    sample = Appointment.objects.all().order_by('appointment_date')[:5]
    for apt in sample:
        print(f"   ID: {apt.id}, Date: {apt.appointment_date}, Status: {apt.status}")

else:
    print("\n⚠️  NO APPOINTMENTS FOUND IN DATABASE!")
    print("   This is why the charts show no data.")

print("\n" + "=" * 80)
print("END OF DIAGNOSTIC REPORT")
print("=" * 80)
