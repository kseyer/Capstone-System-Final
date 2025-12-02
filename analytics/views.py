from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta
from .models import PatientAnalytics, ServiceAnalytics, BusinessAnalytics, TreatmentCorrelation, PatientSegment
from accounts.models import User
from appointments.models import Appointment
from services.models import Service
from products.models import Product
from packages.models import Package


def is_owner_or_admin(user):
    """Check if user is owner or admin"""
    return user.is_authenticated and user.user_type in ['owner', 'admin']


@login_required
@user_passes_test(is_owner_or_admin)
def analytics_dashboard(request):
    """Comprehensive analytics dashboard with filtering"""
    # Get filter parameters from request
    year_filter = request.GET.get('year', '')
    status_filter = request.GET.get('status', '')
    service_type_filter = request.GET.get('service_type', '')
    attendant_filter = request.GET.get('attendant', '')
    patient_search = request.GET.get('patient_search', '')
    
    # Calculate date range
    today = timezone.now().date()
    
    # Handle year filter
    if year_filter:
        try:
            year = int(year_filter)
            filter_start_date = datetime(year, 1, 1).date()
            filter_end_date = datetime(year, 12, 31).date()
        except ValueError:
            # Default to current year if invalid
            current_year = today.year
            filter_start_date = datetime(current_year, 1, 1).date()
            filter_end_date = datetime(current_year, 12, 31).date()
            year_filter = str(current_year)
    else:
        # Default to current year
        current_year = today.year
        filter_start_date = datetime(current_year, 1, 1).date()
        filter_end_date = datetime(current_year, 12, 31).date()
        year_filter = str(current_year)
    
    # Base queryset for appointments
    appointments_qs = Appointment.objects.filter(
        appointment_date__gte=filter_start_date,
        appointment_date__lte=filter_end_date
    )
    
    # Apply filters
    if status_filter:
        appointments_qs = appointments_qs.filter(status=status_filter)
    
    if service_type_filter == 'service':
        appointments_qs = appointments_qs.exclude(service__isnull=True)
    elif service_type_filter == 'product':
        appointments_qs = appointments_qs.exclude(product__isnull=True)
    elif service_type_filter == 'package':
        appointments_qs = appointments_qs.exclude(package__isnull=True)
    
    if attendant_filter:
        appointments_qs = appointments_qs.filter(attendant_id=attendant_filter)
    
    if patient_search:
        appointments_qs = appointments_qs.filter(
            Q(patient__first_name__icontains=patient_search) |
            Q(patient__last_name__icontains=patient_search) |
            Q(patient__email__icontains=patient_search)
        )
    
    # Basic statistics (filtered)
    total_appointments_filtered = appointments_qs.count()
    total_revenue_filtered = appointments_qs.filter(
        status='completed'
    ).aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    # Add product and package revenue
    product_revenue = appointments_qs.filter(
        status='completed',
        product__isnull=False
    ).aggregate(
        total=Sum('product__price')
    )['total'] or 0
    
    package_revenue = appointments_qs.filter(
        status='completed',
        package__isnull=False
    ).aggregate(
        total=Sum('package__price')
    )['total'] or 0
    
    total_revenue_filtered += product_revenue + package_revenue
    
    # Overall statistics (unfiltered)
    total_patients = User.objects.filter(user_type='patient').count()
    total_appointments = Appointment.objects.count()
    total_revenue = Appointment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('service__price'))['total'] or 0
    
    # Recent activity (filtered)
    recent_appointments = appointments_qs.order_by('-appointment_date')[:20]
    
    # Patient analytics (filtered)
    active_patients = appointments_qs.values('patient').distinct().count()
    
    # Get new patients within the year filter
    new_patients = User.objects.filter(
        user_type='patient',
        created_at__gte=filter_start_date,
        created_at__lte=filter_end_date
    ).count()
    
    # Get at_risk patients count safely
    try:
        at_risk_count = PatientSegment.objects.filter(segment='at_risk').count()
    except Exception:
        at_risk_count = 0
    
    patient_stats = {
        'new_patients_30_days': new_patients,
        'active_patients': active_patients,
        'at_risk_patients': at_risk_count,
    }
    
    # Service popularity (filtered)
    if appointments_qs.exists():
        popular_services = Service.objects.filter(
            appointments__in=appointments_qs
        ).annotate(
            booking_count=Count('appointments')
        ).order_by('-booking_count')[:10]
    else:
        popular_services = Service.objects.none()
    
    # Monthly trends (filtered)
    monthly_appointments = appointments_qs.annotate(
        month=TruncMonth('appointment_date')
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('service__price')
    ).order_by('month')
    
    # Status breakdown
    status_breakdown = appointments_qs.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Treatment correlations
    try:
        correlations = TreatmentCorrelation.objects.filter(
            correlation_strength__gte=0.5
        ).order_by('-correlation_strength')[:10]
    except Exception:
        correlations = TreatmentCorrelation.objects.none()
    
    # Patient segments
    try:
        segments = PatientSegment.objects.values('segment').annotate(
            count=Count('id')
        ).order_by('-count')
    except Exception:
        segments = []
    
    # Weekly appointment trends for chart
    from django.db.models.functions import TruncWeek, TruncDay
    import logging
    logger = logging.getLogger(__name__)
    
    # For yearly view, show all 12 months of the selected year
    chart_end_date = filter_end_date
    chart_start_date = filter_start_date
    
    weekly_trends = appointments_qs.filter(
        appointment_date__gte=chart_start_date,
        appointment_date__lte=chart_end_date
    ).annotate(
        week=TruncWeek('appointment_date')
    ).values('week').annotate(
        count=Count('id')
    ).order_by('week')
    
    # Debug logging
    logger.info(f"Chart date range: {chart_start_date} to {chart_end_date}")
    logger.info(f"Total appointments in range: {appointments_qs.filter(appointment_date__gte=chart_start_date, appointment_date__lte=chart_end_date).count()}")
    logger.info(f"Weekly trends count: {weekly_trends.count()}")
    
    # Format chart data - show 12 months for yearly view
    chart_labels = []
    chart_data = []
    
    # Create monthly data points for the selected year
    from datetime import datetime as dt
    for month in range(1, 13):
        try:
            month_start = datetime(int(year_filter), month, 1).date()
            # Get last day of month
            if month == 12:
                month_end = datetime(int(year_filter), 12, 31).date()
            else:
                month_end = datetime(int(year_filter), month + 1, 1).date() - timedelta(days=1)
            
            # Count appointments in this month
            month_count = appointments_qs.filter(
                appointment_date__gte=month_start,
                appointment_date__lte=month_end
            ).count()
            
            chart_labels.append(month_start.strftime('%b %Y'))
            chart_data.append(month_count)
        except ValueError:
            # Handle invalid dates
            continue
    
    # Log final chart data
    logger.info(f"Chart Labels: {chart_labels}")
    logger.info(f"Chart Data: {chart_data}")
    logger.info(f"Total data points: {sum(chart_data)}")
    
    # Patient segment data for donut chart
    segment_labels = []
    segment_data = []
    for segment in segments:
        segment_name = segment['segment'].replace('_', ' ').title()
        segment_labels.append(segment_name)
        segment_data.append(segment['count'])
    
    # If no segments, provide default data
    if not segment_labels:
        segment_labels = ['No Data']
        segment_data = [1]
    
    # Ensure chart data has minimum structure
    if not chart_labels or len(chart_labels) == 0:
        logger.warning("No chart labels generated, using default empty state")
        chart_labels = ['No Data']
        chart_data = [0]
    
    # Monthly revenue data for bar chart (for the selected year)
    revenue_start_date = filter_start_date
    revenue_end_date = filter_end_date
    monthly_revenue_data = appointments_qs.filter(
        status='completed',
        appointment_date__gte=revenue_start_date,
        appointment_date__lte=revenue_end_date
    ).annotate(
        month=TruncMonth('appointment_date')
    ).values('month').annotate(
        revenue=Sum('service__price')
    ).order_by('month')
    
    # Format monthly revenue data
    revenue_labels = []
    revenue_data = []
    
    # Create a complete 12-month range for the selected year
    for month in range(1, 13):
        try:
            month_date = datetime(int(year_filter), month, 1).date()
            
            # Find matching data for this month
            month_revenue = 0
            for rev_data in monthly_revenue_data:
                if rev_data['month']:
                    # rev_data['month'] is already a datetime object, extract the date
                    rev_date = rev_data['month'].date() if hasattr(rev_data['month'], 'date') else rev_data['month']
                    if rev_date.year == month_date.year and rev_date.month == month_date.month:
                        month_revenue = float(rev_data['revenue'] or 0)
                        break
            
            revenue_labels.append(month_date.strftime('%b %Y'))
            revenue_data.append(month_revenue)
        except ValueError:
            # Handle invalid dates
            continue
    
    # Get attendants for filter dropdown
    from accounts.models import Attendant
    try:
        attendants = Attendant.objects.all().order_by('first_name', 'last_name')
    except Exception:
        attendants = []
    
    # Get available years for filter dropdown
    available_years = Appointment.objects.dates('appointment_date', 'year', order='DESC')
    years = [year.year for year in available_years]
    if not years:
        years = [today.year]  # Default to current year if no appointments
    
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'total_revenue': total_revenue,
        'total_appointments_filtered': total_appointments_filtered,
        'total_revenue_filtered': total_revenue_filtered,
        'patient_stats': patient_stats,
        'popular_services': popular_services,
        'monthly_appointments': monthly_appointments,
        'correlations': correlations,
        'segments': segments,
        'recent_appointments': recent_appointments,
        'status_breakdown': status_breakdown,
        'attendants': attendants,
        'years': years,
        # Chart data
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'segment_labels': segment_labels,
        'segment_data': segment_data,
        'revenue_labels': revenue_labels,
        'revenue_data': revenue_data,
        # Filter values for template
        'year_filter': year_filter,
        'status_filter': status_filter,
        'service_type_filter': service_type_filter,
        'attendant_filter': attendant_filter,
        'patient_search': patient_search,
    }
    
    # For staff (admin) users, use the staff analytics layout with sidebar
    if request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'admin':
        return render(request, 'analytics/admin_dashboard.html', context)

    return render(request, 'analytics/dashboard.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def patient_analytics(request):
    """Detailed patient analytics"""
    # Get filter parameters
    segment_filter = request.GET.get('segment', '')
    search_query = request.GET.get('search', '')
    
    # Get patients with analytics
    patients = User.objects.filter(user_type='patient').prefetch_related('analytics')
    
    # Apply filters
    if segment_filter:
        patients = patients.filter(segments__segment=segment_filter)
    
    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Calculate analytics for each patient
    patient_analytics_list = []
    for patient in patients:
        appointments = Appointment.objects.filter(patient=patient)
        analytics_data = {
            'patient': patient,
            'total_appointments': appointments.count(),
            'completed_appointments': appointments.filter(status='completed').count(),
            'cancelled_appointments': appointments.filter(status='cancelled').count(),
            'total_spent': sum([app.service.price for app in appointments.filter(status='completed') if app.service]),
            'last_visit': appointments.filter(status='completed').order_by('-appointment_date').first(),
            'segment': patient.segments.first().segment if patient.segments.exists() else 'unclassified',
        }
        patient_analytics_list.append(analytics_data)
    
    # Sort by total spent
    patient_analytics_list.sort(key=lambda x: x['total_spent'], reverse=True)
    
    context = {
        'patient_analytics': patient_analytics_list,
        'segment_filter': segment_filter,
        'search_query': search_query,
    }
    
    return render(request, 'analytics/patient_analytics.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def service_analytics(request):
    """Service performance analytics"""
    # Service performance metrics
    services = Service.objects.annotate(
        total_bookings=Count('appointments'),
        completed_bookings=Count('appointments', filter=Q(appointments__status='completed')),
        cancelled_bookings=Count('appointments', filter=Q(appointments__status='cancelled')),
        total_revenue=Sum('appointments__service__price', filter=Q(appointments__status='completed')),
        avg_rating=Avg('appointments__feedback__rating', filter=Q(appointments__feedback__isnull=False))
    ).order_by('-total_bookings')
    
    # Service categories performance
    category_stats = Service.objects.values('category__name').annotate(
        service_count=Count('id'),
        total_bookings=Count('appointments'),
        total_revenue=Sum('appointments__service__price', filter=Q(appointments__status='completed'))
    ).order_by('-total_revenue')
    
    # Seasonal trends
    seasonal_data = Appointment.objects.filter(
        appointment_date__gte=timezone.now().date() - timedelta(days=365)
    ).annotate(
        month=Extract('appointment_date', 'month')
    ).values('month').annotate(
        count=Count('id'),
        revenue=Sum('service__price')
    ).order_by('month')
    
    context = {
        'services': services,
        'category_stats': category_stats,
        'seasonal_data': seasonal_data,
    }
    
    return render(request, 'analytics/service_analytics.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def treatment_correlations(request):
    """Treatment correlation analysis"""
    correlations = TreatmentCorrelation.objects.select_related(
        'primary_service', 'secondary_service'
    ).order_by('-correlation_strength')
    
    # Filter by strength
    min_strength = request.GET.get('min_strength', 0.3)
    correlations = correlations.filter(correlation_strength__gte=min_strength)
    
    context = {
        'correlations': correlations,
        'min_strength': min_strength,
    }
    
    return render(request, 'analytics/treatment_correlations.html', context)


@login_required
@user_passes_test(is_owner_or_admin)
def business_insights(request):
    """Business insights and recommendations"""
    # Calculate key metrics
    total_patients = User.objects.filter(user_type='patient').count()
    total_appointments = Appointment.objects.count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancellation_rate = (Appointment.objects.filter(status='cancelled').count() / total_appointments * 100) if total_appointments > 0 else 0
    
    # Revenue trends
    revenue_trend = Appointment.objects.filter(
        status='completed',
        appointment_date__gte=timezone.now().date() - timedelta(days=90)
    ).annotate(
        week=TruncWeek('appointment_date')
    ).values('week').annotate(
        revenue=Sum('service__price')
    ).order_by('week')
    
    # Patient retention
    retention_data = []
    for i in range(1, 13):  # Last 12 months
        month_start = timezone.now().date().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        new_patients = User.objects.filter(
            user_type='patient',
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        
        returning_patients = User.objects.filter(
            user_type='patient',
            appointments__appointment_date__gte=month_start,
            appointments__appointment_date__lt=month_end
        ).distinct().count()
        
        retention_data.append({
            'month': month_start.strftime('%Y-%m'),
            'new_patients': new_patients,
            'returning_patients': returning_patients,
            'retention_rate': (returning_patients / new_patients * 100) if new_patients > 0 else 0
        })
    
    # Generate insights
    insights = []
    
    if cancellation_rate > 20:
        insights.append({
            'type': 'warning',
            'title': 'High Cancellation Rate',
            'message': f'Your cancellation rate is {cancellation_rate:.1f}%. Consider improving appointment reminders and customer service.',
        })
    
    if completed_appointments < total_appointments * 0.7:
        insights.append({
            'type': 'info',
            'title': 'Appointment Completion Rate',
            'message': f'Your completion rate is {(completed_appointments/total_appointments*100):.1f}%. Focus on reducing cancellations.',
        })
    
    # Top performing services
    top_services = Service.objects.annotate(
        booking_count=Count('appointments', filter=Q(appointments__status='completed'))
    ).order_by('-booking_count')[:3]
    
    if top_services:
        insights.append({
            'type': 'success',
            'title': 'Top Performing Services',
            'message': f'Your most popular services are: {", ".join([s.service_name for s in top_services])}. Consider promoting these further.',
        })
    
    context = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancellation_rate': cancellation_rate,
        'revenue_trend': revenue_trend,
        'retention_data': retention_data,
        'insights': insights,
    }
    
    return render(request, 'analytics/business_insights.html', context)
