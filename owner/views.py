from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from accounts.models import User
from appointments.models import Appointment, ClosedDay
from services.models import Service, ServiceImage, ServiceCategory, HistoryLog
from products.models import Product, ProductImage
from packages.models import Package
from analytics.models import PatientAnalytics, ServiceAnalytics, BusinessAnalytics, TreatmentCorrelation, PatientSegment


def log_history(item_type, item_name, action, performed_by, details='', related_id=None):
    """Helper function to log history and notify owner"""
    from appointments.models import Notification
    from accounts.models import User
    
    # Create history log
    HistoryLog.objects.create(
        type=item_type,
        name=item_name,
        action=action,
        performed_by=performed_by,
        details=details,
        related_id=related_id
    )
    
    # Notify owner when staff performs actions
    owner_users = User.objects.filter(user_type='owner', is_active=True)
    for owner in owner_users:
        Notification.objects.create(
            type='system',
            title=f'{action}: {item_type} - {item_name}',
            message=f'{performed_by} {action.lower()} {item_type.lower()} "{item_name}". {details}',
            patient=None  # Owner notification
        )


def is_owner(user):
    """Check if user is owner or admin (staff)"""
    return user.is_authenticated and user.user_type in ('owner', 'admin')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_dashboard(request):
    """Owner comprehensive dashboard with advanced analytics"""
    from analytics.services import AnalyticsService
    from appointments.models import Notification, Appointment
    from accounts.models import Attendant
    from django.db.models import Q, Count, Sum
    from datetime import timedelta
    from django.utils import timezone
    
    analytics_service = AnalyticsService()
    
    # Get filter parameters from request
    date_range = request.GET.get('date_range', '30')
    status_filter = request.GET.get('status', '')
    service_type_filter = request.GET.get('service_type', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Calculate date range
    today = timezone.now().date()
    if date_range == '7':
        filter_start_date = today - timedelta(days=7)
    elif date_range == '90':
        filter_start_date = today - timedelta(days=90)
    elif date_range == '365':
        filter_start_date = today - timedelta(days=365)
    else:
        filter_start_date = today - timedelta(days=30)
    
    # Use custom date range if provided
    if start_date:
        try:
            from datetime import datetime
            filter_start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if end_date:
        try:
            from datetime import datetime
            filter_end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            filter_end_date = today
    else:
        filter_end_date = today
    
    # Get comprehensive analytics data
    business_overview = analytics_service.get_business_overview()
    revenue_analytics = analytics_service.get_revenue_analytics()
    patient_analytics = analytics_service.get_patient_analytics()
    service_analytics = analytics_service.get_service_analytics()
    treatment_correlations = analytics_service.get_treatment_correlations()
    business_insights = analytics_service.get_business_insights()
    diagnostic_metrics = analytics_service.get_diagnostic_metrics()
    
    # Get filtered appointments for status breakdown
    appointments_qs = Appointment.objects.filter(
        appointment_date__gte=filter_start_date,
        appointment_date__lte=filter_end_date
    )
    
    if status_filter:
        appointments_qs = appointments_qs.filter(status=status_filter)
    
    if service_type_filter == 'service':
        appointments_qs = appointments_qs.exclude(service__isnull=True)
    elif service_type_filter == 'product':
        appointments_qs = appointments_qs.exclude(product__isnull=True)
    elif service_type_filter == 'package':
        appointments_qs = appointments_qs.exclude(package__isnull=True)
    
    # Status breakdown
    status_breakdown = appointments_qs.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get notification count (owner notifications are where patient is null)
    notification_count = Notification.objects.filter(
        patient__isnull=True,
        is_read=False
    ).count()
    
    # Get attendants for filter dropdown (if needed in future)
    try:
        attendants = Attendant.objects.all().order_by('first_name', 'last_name')
    except Exception:
        attendants = []
    
    context = {
        'business_overview': business_overview,
        'revenue_analytics': revenue_analytics,
        'patient_analytics': patient_analytics,
        'service_analytics': service_analytics,
        'treatment_correlations': treatment_correlations,
        'business_insights': business_insights,
        'diagnostic_metrics': diagnostic_metrics,
        'notification_count': notification_count,
        'status_breakdown': status_breakdown,
        'attendants': attendants,
        # Filter values for template
        'date_range': date_range,
        'status_filter': status_filter,
        'service_type_filter': service_type_filter,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'owner/dashboard.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_patients(request):
    """Owner patients overview"""
    # Get all patients with analytics
    patients = User.objects.filter(user_type='patient').prefetch_related('analytics', 'segments')
    
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
    
    # Get notification count
    from appointments.models import Notification
    notification_count = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()
    
    context = {
        'patient_analytics': patient_analytics_list,
        'notification_count': notification_count,
    }
    
    return render(request, 'owner/patients.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_appointments(request):
    """Owner appointments overview"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Start with all appointments - latest bookings first (by creation time, then appointment date/time)
    appointments = Appointment.objects.all().order_by('-created_at', '-appointment_date', '-appointment_time')
    
    # Apply filters
    if status_filter:
        appointments = appointments.filter(status=status_filter)
    
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    
    if search_query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(service__service_name__icontains=search_query) |
            Q(product__product_name__icontains=search_query) |
            Q(package__package_name__icontains=search_query)
        )
    
    context = {
        'appointments': appointments,
        'status_filter': status_filter,
        'date_filter': date_filter,
        'search_query': search_query,
    }
    
    return render(request, 'owner/appointments.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_cancel_appointment(request, appointment_id):
    """Owner cancel an appointment"""
    from appointments.models import Notification, CancellationRequest
    from services.utils import send_appointment_sms
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Cancellation reason is required.')
            return redirect('owner:appointments')
    
    if appointment.status in ['pending', 'confirmed']:
        # Get reason from POST or set default
        reason = request.POST.get('reason', '').strip() if request.method == 'POST' else 'Cancelled by owner'
        
        appointment.status = 'cancelled'
        appointment.save()
        
        # Create cancellation request record with reason
        appointment_type = 'package' if appointment.package else 'regular'
        CancellationRequest.objects.create(
            appointment_id=appointment.id,
            appointment_type=appointment_type,
            patient=appointment.patient,
            reason=reason,
            status='approved'  # Auto-approved since owner is cancelling
        )
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Appointment Cancelled',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled. Please contact us to reschedule.',
            patient=appointment.patient
        )
        
        # Notify owner of appointment cancellation (self-notification)
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Appointment Cancelled',
            message=f'Appointment for {appointment.patient.get_full_name()} - {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled.',
            patient=None  # Owner notification
        )
        
        # Send SMS cancellation notification
        sms_result = send_appointment_sms(appointment, 'cancellation')
        if sms_result['success']:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been cancelled. SMS sent.')
        else:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been cancelled. (SMS failed)')
    else:
        messages.error(request, 'Only pending or confirmed appointments can be cancelled.')
    
    return redirect('owner:appointments')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_reschedule_appointment(request, appointment_id):
    """Owner reschedule an appointment"""
    from appointments.models import Notification, RescheduleRequest
    from services.utils import send_appointment_sms
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        new_date = request.POST.get('new_appointment_date')
        new_time = request.POST.get('new_appointment_time')
        reason = request.POST.get('reason', '').strip()
        
        if not new_date or not new_time:
            messages.error(request, 'Please provide both new date and time.')
            return redirect('owner:appointments')
        
        # Check if appointment can be rescheduled
        if appointment.status not in ['pending', 'confirmed']:
            messages.error(request, 'This appointment cannot be rescheduled.')
            return redirect('owner:appointments')
        
        # Check if the new date is a closed clinic day
        new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
        if ClosedDay.objects.filter(date=new_date_obj).exists():
            closed_day = ClosedDay.objects.get(date=new_date_obj)
            reason_text = f" ({closed_day.reason})" if closed_day.reason else ""
            messages.error(request, f'Cannot reschedule: The clinic is closed on {new_date_obj.strftime("%B %d, %Y")}{reason_text}.')
            return redirect('owner:appointments')
        
        # Create reschedule request (mark as approved since owner is rescheduling)
        reschedule_request = RescheduleRequest.objects.create(
            appointment_id=appointment.id,
            new_appointment_date=new_date,
            new_appointment_time=new_time,
            patient=appointment.patient,
            reason=reason or 'Rescheduled by owner',
            status='approved'  # Auto-approve owner reschedules
        )
        
        # Update appointment
        old_date = appointment.appointment_date
        old_time = appointment.appointment_time
        appointment.appointment_date = new_date
        appointment.appointment_time = new_time
        appointment.status = 'pending'  # Set to pending after reschedule
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Appointment Rescheduled',
            message=f'Your appointment for {appointment.get_service_name()} has been rescheduled from {old_date} at {old_time} to {new_date} at {new_time}. Reason: {reason or "Rescheduled by clinic"}.',
            patient=appointment.patient
        )
        
        # Notify owner (self-notification)
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Appointment Rescheduled',
            message=f'Appointment for {appointment.patient.get_full_name()} - {appointment.get_service_name()} has been rescheduled from {old_date} at {old_time} to {new_date} at {new_time}.',
            patient=None  # Owner notification
        )
        
        # Send SMS notification
        sms_result = send_appointment_sms(appointment, 'reschedule')
        if sms_result['success']:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been rescheduled. SMS sent.')
        else:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been rescheduled. (SMS failed)')
        
        return redirect('owner:appointments')
    
    # GET request - show reschedule form
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'owner/reschedule_appointment.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_services(request):
    """Owner services overview"""
    services = Service.objects.filter(archived=False).annotate(
        total_bookings=Count('appointments'),
        completed_bookings=Count('appointments', filter=Q(appointments__status='completed')),
        cancelled_bookings=Count('appointments', filter=Q(appointments__status='cancelled')),
        total_revenue=Sum('appointments__service__price', filter=Q(appointments__status='completed')),
        avg_rating=Avg('appointments__feedback__rating', filter=Q(appointments__feedback__isnull=False))
    ).order_by('-total_revenue')
    
    context = {
        'services': services,
    }
    
    return render(request, 'owner/services.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_packages(request):
    """Owner packages overview"""
    packages = Package.objects.filter(archived=False).annotate(
        total_bookings=Count('package_bookings'),
        total_revenue=Sum('package_bookings__price'),
        avg_rating=Avg('package_bookings__feedback__rating', filter=Q(package_bookings__feedback__isnull=False))
    ).order_by('-total_revenue')
    
    # Add pagination
    paginator = Paginator(packages, 15)  # 15 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'packages': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'owner/packages.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_products(request):
    """Owner products overview"""
    products = Product.objects.annotate(
        total_bookings=Count('appointments'),
        completed_bookings=Count('appointments', filter=Q(appointments__status='completed')),
        total_revenue=Sum('appointments__product__price', filter=Q(appointments__status='completed'))
    ).order_by('-total_revenue')
    
    context = {
        'products': products,
    }
    
    return render(request, 'owner/products.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_analytics(request):
    """Owner comprehensive analytics dashboard"""
    from analytics.services import AnalyticsService
    
    analytics_service = AnalyticsService()
    
    # Get comprehensive analytics data
    business_overview = analytics_service.get_business_overview()
    revenue_analytics = analytics_service.get_revenue_analytics()
    patient_analytics = analytics_service.get_patient_analytics()
    service_analytics = analytics_service.get_service_analytics()
    treatment_correlations = analytics_service.get_treatment_correlations()
    business_insights = analytics_service.get_business_insights()
    diagnostic_metrics = analytics_service.get_diagnostic_metrics()
    
    # Get filter parameters
    date_range = request.GET.get('date_range', '30')
    view_type = request.GET.get('view_type', 'overview')
    
    # Adjust date ranges based on filter
    if date_range == '7':
        days = 7
    elif date_range == '90':
        days = 90
    elif date_range == '365':
        days = 365
    else:
        days = 30
    
    context = {
        'business_overview': business_overview,
        'revenue_analytics': revenue_analytics,
        'patient_analytics': patient_analytics,
        'service_analytics': service_analytics,
        'treatment_correlations': treatment_correlations,
        'business_insights': business_insights,
        'diagnostic_metrics': diagnostic_metrics,
        'date_range': date_range,
        'view_type': view_type,
        'days': days,
    }
    
    return render(request, 'owner/analytics.html', context)


# Owner Management Functions

@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_services(request):
    """Owner manage services"""
    services = Service.objects.filter(archived=False).order_by('service_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            service_name = request.POST.get('service_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            duration = request.POST.get('duration')
            category_id = request.POST.get('category')
            
            if service_name and price and duration:
                try:
                    service = Service.objects.create(
                        service_name=service_name,
                        description=description,
                        price=price,
                        duration=duration,
                        category_id=category_id
                    )
                    log_history('Service', service_name, 'Added', request.user.get_full_name() or request.user.username, 
                               f'Price: {price}, Duration: {duration}', service.id)
                    messages.success(request, 'Service added successfully!')
                except Exception as e:
                    messages.error(request, f'Error adding service: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        elif action == 'edit':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            old_name = service.service_name
            service.service_name = request.POST.get('service_name', service.service_name)
            service.description = request.POST.get('description', service.description)
            price = request.POST.get('price')
            if price:
                service.price = price
            duration = request.POST.get('duration')
            if duration:
                service.duration = duration
            category_id = request.POST.get('category')
            if category_id:
                service.category_id = category_id
            service.save()
            log_history('Service', service.service_name, 'Edited', request.user.get_full_name() or request.user.username,
                       f'Updated: {old_name} -> {service.service_name}', service.id)
            messages.success(request, 'Service updated successfully!')
        
        elif action == 'delete' or action == 'archive':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            service_name = service.service_name
            service.archived = True
            service.save()
            log_history('Service', service_name, 'Deleted', request.user.get_full_name() or request.user.username,
                       f'Service archived', service.id)
            messages.success(request, 'Service archived successfully!')
        
        return redirect('owner:manage_services')
    
    # Add pagination
    paginator = Paginator(services, 15)  # 15 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ServiceCategory.objects.all()
    context = {
        'services': page_obj,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'owner/manage_services.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_packages(request):
    """Owner manage packages"""
    packages = Package.objects.filter(archived=False).order_by('package_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            package_name = request.POST.get('package_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            sessions = request.POST.get('sessions')
            duration_days = request.POST.get('duration_days')
            grace_period_days = request.POST.get('grace_period_days')
            
            if package_name and price and sessions:
                try:
                    package = Package.objects.create(
                        package_name=package_name,
                        description=description,
                        price=price,
                        sessions=sessions,
                        duration_days=duration_days or 0,
                        grace_period_days=grace_period_days or 0
                    )
                    log_history('Package', package_name, 'Added', request.user.get_full_name() or request.user.username,
                               f'Price: {price}, Sessions: {sessions}', package.id)
                    messages.success(request, 'Package added successfully!')
                except Exception as e:
                    messages.error(request, f'Error adding package: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        elif action == 'edit':
            package_id = request.POST.get('package_id')
            package = get_object_or_404(Package, id=package_id)
            old_name = package.package_name
            package.package_name = request.POST.get('package_name', package.package_name)
            package.description = request.POST.get('description', package.description)
            price = request.POST.get('price')
            if price:
                package.price = price
            sessions = request.POST.get('sessions')
            if sessions:
                package.sessions = sessions
            duration_days = request.POST.get('duration_days')
            if duration_days:
                package.duration_days = duration_days
            grace_period_days = request.POST.get('grace_period_days')
            if grace_period_days:
                package.grace_period_days = grace_period_days
            package.save()
            log_history('Package', package.package_name, 'Edited', request.user.get_full_name() or request.user.username,
                       f'Updated: {old_name} -> {package.package_name}', package.id)
            messages.success(request, 'Package updated successfully!')
        
        elif action == 'delete' or action == 'archive':
            package_id = request.POST.get('package_id')
            package = get_object_or_404(Package, id=package_id)
            package_name = package.package_name
            package.archived = True
            package.save()
            log_history('Package', package_name, 'Deleted', request.user.get_full_name() or request.user.username,
                       f'Package archived', package.id)
            messages.success(request, 'Package archived successfully!')
        
        return redirect('owner:manage_packages')
    
    # Add pagination
    paginator = Paginator(packages, 15)  # 15 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'packages': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'owner/manage_packages.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_products(request):
    """Owner manage products"""
    products = Product.objects.filter(archived=False).order_by('product_name')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            stock = request.POST.get('stock') or request.POST.get('stock_quantity')
            
            if product_name and price:
                try:
                    Product.objects.create(
                        product_name=product_name,
                        description=description,
                        price=price,
                        stock=stock or 0
                    )
                    messages.success(request, 'Product added successfully!')
                except Exception as e:
                    messages.error(request, f'Error adding product: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')
        
        elif action == 'edit':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            old_name = product.product_name
            product.product_name = request.POST.get('product_name', product.product_name)
            product.description = request.POST.get('description', product.description)
            price = request.POST.get('price')
            if price:
                product.price = price
            stock = request.POST.get('stock') or request.POST.get('stock_quantity')
            if stock is not None:
                product.stock = stock
            product.save()
            log_history('Product', product.product_name, 'Edited', request.user.get_full_name() or request.user.username,
                       f'Updated: {old_name} -> {product.product_name}', product.id)
            messages.success(request, 'Product updated successfully!')
        
        elif action == 'delete' or action == 'archive':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product_name = product.product_name
            product.archived = True
            product.save()
            log_history('Product', product_name, 'Deleted', request.user.get_full_name() or request.user.username,
                       f'Product archived', product.id)
            messages.success(request, 'Product archived successfully!')
        
        return redirect('owner:manage_products')
    
    # Add pagination
    paginator = Paginator(products, 15)  # 15 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'owner/manage_products.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_view_inventory(request):
    """Owner view inventory levels (view-only, no stock management)"""
    products = Product.objects.filter(archived=False).order_by('product_name')
    
    # Add pagination
    paginator = Paginator(products, 15)  # 15 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'owner/inventory.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_patient_profiles(request):
    """Owner manage patient profiles"""
    patients = User.objects.filter(user_type='patient').order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'edit':
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(User, id=patient_id, user_type='patient')
            patient.first_name = request.POST.get('first_name', patient.first_name)
            patient.last_name = request.POST.get('last_name', patient.last_name)
            patient.email = request.POST.get('email', patient.email)
            patient.phone = request.POST.get('phone', patient.phone)
            patient.address = request.POST.get('address', patient.address)
            patient.gender = request.POST.get('gender', patient.gender)
            patient.civil_status = request.POST.get('civil_status', patient.civil_status)
            patient.birthday = request.POST.get('birthday', patient.birthday)
            patient.occupation = request.POST.get('occupation', patient.occupation)
            patient.save()
            messages.success(request, 'Patient profile updated successfully!')
        
        elif action == 'delete':
            patient_id = request.POST.get('patient_id')
            patient = get_object_or_404(User, id=patient_id, user_type='patient')
            patient.delete()
            messages.success(request, 'Patient deleted successfully!')
        
        return redirect('owner:manage_patient_profiles')
    
    context = {
        'patients': patients,
    }
    return render(request, 'owner/manage_patient_profiles.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_view_history_log(request):
    """Owner view history log with filtering"""
    from services.models import HistoryLog
    from django.db.models import Q
    from accounts.models import User, Attendant
    
    # Get filter parameters
    patient_filter = request.GET.get('patient', '')
    treatment_filter = request.GET.get('treatment', '')
    attendant_filter = request.GET.get('attendant', '')
    year_filter = request.GET.get('year', '')
    type_filter = request.GET.get('type', '')
    
    history_logs = HistoryLog.objects.all()
    
    # Filter by patient (search in details or performed_by)
    if patient_filter:
        history_logs = history_logs.filter(
            Q(details__icontains=patient_filter) |
            Q(performed_by__icontains=patient_filter)
        )
    
    # Filter by treatment/service (search in name or details)
    if treatment_filter:
        history_logs = history_logs.filter(
            Q(name__icontains=treatment_filter) |
            Q(details__icontains=treatment_filter)
        )
    
    # Filter by attendant (search in details or performed_by)
    if attendant_filter:
        history_logs = history_logs.filter(
            Q(details__icontains=attendant_filter) |
            Q(performed_by__icontains=attendant_filter)
        )
    
    # Filter by year
    if year_filter:
        history_logs = history_logs.filter(datetime__year=year_filter)
    
    # Filter by type (Service, Product, Package)
    if type_filter:
        history_logs = history_logs.filter(type=type_filter)
    
    history_logs = history_logs.order_by('-datetime')
    
    # Get unique years for filter dropdown
    years = HistoryLog.objects.dates('datetime', 'year', order='DESC').values_list('datetime__year', flat=True).distinct()
    
    # Get unique patients for filter (from details)
    patients = User.objects.filter(user_type='patient').order_by('first_name', 'last_name')
    
    # Get unique attendants for filter
    attendants = Attendant.objects.all().order_by('first_name', 'last_name')
    
    context = {
        'history_logs': history_logs,
        'patient_filter': patient_filter,
        'treatment_filter': treatment_filter,
        'attendant_filter': attendant_filter,
        'year_filter': year_filter,
        'type_filter': type_filter,
        'years': years,
        'patients': patients,
        'attendants': attendants,
    }
    return render(request, 'owner/history_log.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_service_images(request):
    """Owner view to manage service images"""
    services = Service.objects.all().order_by('service_name')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        if service_id:
            service = get_object_or_404(Service, id=service_id)
            # Handle image upload
            if 'image' in request.FILES:
                image = request.FILES['image']
                alt_text = request.POST.get('alt_text', '')
                is_primary = request.POST.get('is_primary') == 'on'
                
                # If this is set as primary, unset other primary images for this service
                if is_primary:
                    ServiceImage.objects.filter(service=service, is_primary=True).update(is_primary=False)
                
                ServiceImage.objects.create(
                    service=service,
                    image=image,
                    alt_text=alt_text,
                    is_primary=is_primary
                )
                messages.success(request, f'Image uploaded successfully for {service.service_name}')
            else:
                messages.error(request, 'Please select an image to upload')
    
    context = {
        'services': services,
    }
    return render(request, 'owner/manage_service_images.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_product_images(request):
    """Owner view to manage product images"""
    products = Product.objects.all().order_by('product_name')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            # Handle image upload
            if 'image' in request.FILES:
                image = request.FILES['image']
                alt_text = request.POST.get('alt_text', '')
                is_primary = request.POST.get('is_primary') == 'on'
                
                # If this is set as primary, unset other primary images for this product
                if is_primary:
                    ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
                
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    alt_text=alt_text,
                    is_primary=is_primary
                )
                messages.success(request, f'Image uploaded successfully for {product.product_name}')
            else:
                messages.error(request, 'Please select an image to upload')
    
    context = {
        'products': products,
    }
    return render(request, 'owner/manage_product_images.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_delete_service_image(request, image_id):
    """Delete a service image"""
    image = get_object_or_404(ServiceImage, id=image_id)
    service_name = image.service.service_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {service_name}')
    return redirect('owner:manage_service_images')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_delete_product_image(request, image_id):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_name = image.product.product_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {product_name}')
    return redirect('owner:manage_product_images')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_set_primary_service_image(request, image_id):
    """Set a service image as primary"""
    image = get_object_or_404(ServiceImage, id=image_id)
    # Unset other primary images for this service
    ServiceImage.objects.filter(service=image.service, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.service.service_name}')
    return redirect('owner:manage_service_images')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_set_primary_product_image(request, image_id):
    """Set a product image as primary"""
    image = get_object_or_404(ProductImage, id=image_id)
    # Unset other primary images for this product
    ProductImage.objects.filter(product=image.product, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.product.product_name}')
    return redirect('owner:manage_product_images')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_attendants(request):
    """Owner manage attendants page - same functionality as admin_settings"""
    from appointments.models import ClosedDay
    from accounts.models import Attendant, AttendantProfile
    
    attendants = Attendant.objects.all()
    closed_days = ClosedDay.objects.all()
    attendant_users = User.objects.filter(user_type='attendant').order_by('-is_active', 'first_name', 'last_name')
    
    # Get attendant profiles - create list of tuples for easier template access
    attendant_users_with_profiles = []
    for user in attendant_users:
        try:
            profile = user.attendant_profile
            attendant_users_with_profiles.append((user, profile))
        except AttendantProfile.DoesNotExist:
            attendant_users_with_profiles.append((user, None))
    
    # Create a list of hours for the schedule
    hours = ['10', '11', '12', '13', '14', '15', '16', '17', '18']
    
    context = {
        'attendants': attendants,
        'closed_days': closed_days,
        'hours': hours,
        'attendant_users': attendant_users,
        'attendant_users_with_profiles': attendant_users_with_profiles,
        'is_owner': True,  # Flag to indicate this is owner view
    }
    
    return render(request, 'owner/manage_attendants.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_create_attendant_user(request):
    """Create a new attendant user account (owner version)"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        
        if not all([username, password, first_name, last_name]):
            messages.error(request, 'Username, password, first name, and last name are required.')
            return redirect('owner:manage_attendants')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken. Please choose another one.')
            return redirect('owner:manage_attendants')
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            user_type='attendant',
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        messages.success(request, f'Attendant account {username} created successfully. Temporary password: {password}')
    
    return redirect('owner:manage_attendants')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_edit_attendant_user(request, user_id):
    """Edit attendant user account (owner version)"""
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        
        if not all([first_name, last_name, username]):
            messages.error(request, 'First name, last name, and username are required.')
            return redirect('owner:manage_attendants')
        
        # Check if username is taken by another user
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, 'That username is already taken. Please choose another one.')
            return redirect('owner:manage_attendants')
        
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email if email else user.email
        user.middle_name = middle_name if middle_name else user.middle_name
        user.save()
        
        messages.success(request, f'Attendant account {username} has been updated successfully.')
        return redirect('owner:manage_attendants')
    
    return render(request, 'owner/edit_attendant_user.html', {'attendant_user': user, 'is_owner': True})


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_toggle_attendant_user(request, user_id):
    """Activate or deactivate an attendant user account (owner version)"""
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    user.is_active = not user.is_active
    user.archived = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'Attendant account {user.username} has been {status}.')
    return redirect('owner:manage_attendants')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_reset_attendant_password(request, user_id):
    """Reset attendant account password and provide a temporary one (owner version)"""
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    temp_password = User.objects.make_random_password(length=10)
    user.set_password(temp_password)
    user.save()
    
    messages.success(
        request,
        f'Password for {user.username} has been reset. Temporary password: {temp_password}'
    )
    return redirect('owner:manage_attendants')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_attendant_profile(request, user_id):
    """Manage attendant profile (work days and hours) (owner version)"""
    from accounts.models import AttendantProfile
    
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    
    if request.method == 'POST':
        work_days = request.POST.getlist('work_days')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if not work_days:
            messages.error(request, 'Please select at least one work day.')
            return redirect('owner:manage_attendants')
        
        if not start_time or not end_time:
            messages.error(request, 'Please provide both start and end times.')
            return redirect('owner:manage_attendants')
        
        # Get or create profile
        profile, created = AttendantProfile.objects.get_or_create(user=user)
        profile.work_days = work_days
        profile.start_time = start_time
        profile.end_time = end_time
        profile.save()
        
        if created:
            messages.success(request, f'Profile created for {user.get_full_name()}.')
        else:
            messages.success(request, f'Profile updated for {user.get_full_name()}.')
        
        return redirect('owner:manage_attendants')
    
    return redirect('owner:manage_attendants')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_add_attendant(request):
    """Add new attendant (owner version)"""
    from accounts.models import Attendant
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        shift_date = request.POST.get('shift_date')
        shift_time = request.POST.get('shift_time')
        
        if first_name and last_name:
            try:
                # Create attendant
                Attendant.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    shift_date=shift_date if shift_date else None,
                    shift_time=shift_time if shift_time else None
                )
                
                messages.success(request, f'Attendant {first_name} {last_name} added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding attendant: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return redirect('owner:manage_attendants')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_delete_attendant(request, attendant_id):
    """Delete attendant (owner version)"""
    from accounts.models import Attendant
    
    attendant = get_object_or_404(Attendant, id=attendant_id)
    attendant_name = f"{attendant.first_name} {attendant.last_name}"
    attendant.delete()
    
    messages.success(request, f'Attendant {attendant_name} deleted successfully.')
    return redirect('owner:manage_attendants')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_notifications(request):
    """Owner notifications view - shows all notifications without auto-marking as read"""
    from appointments.models import Notification, CancellationRequest, Appointment
    
    # Show all system notifications (where patient is null) - both read and unread
    notifications = Notification.objects.filter(patient__isnull=True).order_by('-created_at')
    
    # Get cancellation requests for notifications that mention cancellation
    notifications_with_actions = []
    for notification in notifications:
        notification_data = {
            'notification': notification,
            'cancellation_request': None,
            'appointment': None,
        }
        
        # Check if notification is about cancellation and has appointment_id
        if notification.appointment_id and ('cancellation' in notification.title.lower() or 'cancellation' in notification.message.lower()):
            try:
                # Try to find the appointment
                appointment = Appointment.objects.filter(id=notification.appointment_id).first()
                if appointment:
                    notification_data['appointment'] = appointment
                    # Try to find pending cancellation request
                    cancellation_request = CancellationRequest.objects.filter(
                        appointment_id=notification.appointment_id,
                        status='pending'
                    ).first()
                    if cancellation_request:
                        notification_data['cancellation_request'] = cancellation_request
            except Exception:
                pass
        
        notifications_with_actions.append(notification_data)
    
    # Count unread notifications
    unread_count = notifications.filter(is_read=False).count()
    total_count = notifications.count()
    
    context = {
        'notifications_with_actions': notifications_with_actions,
        'notifications': notifications,
        'unread_count': unread_count,
        'total_count': total_count,
    }
    
    return render(request, 'owner/notifications.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_delete_notification(request, notification_id):
    """Delete notification (owner version)"""
    from appointments.models import Notification
    
    notification = get_object_or_404(Notification, id=notification_id, patient__isnull=True)
    notification.delete()
    
    messages.success(request, 'Notification deleted successfully.')
    return redirect('owner:notifications')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_mark_notification_read(request, notification_id):
    """Mark notification as read (owner version)"""
    from appointments.models import Notification
    
    notification = get_object_or_404(Notification, id=notification_id, patient__isnull=True)
    notification.is_read = True
    notification.save()
    
    messages.success(request, 'Notification marked as read.')
    return redirect('owner:notifications')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_approve_cancellation(request, cancellation_request_id):
    """Owner approve cancellation request"""
    from appointments.models import CancellationRequest, Notification, Appointment
    from services.models import HistoryLog
    
    cancellation_request = get_object_or_404(CancellationRequest, id=cancellation_request_id)
    appointment = get_object_or_404(Appointment, id=cancellation_request.appointment_id)
    
    if cancellation_request.status == 'pending':
        # Update cancellation request status
        cancellation_request.status = 'approved'
        cancellation_request.save()
        
        # Cancel the appointment
        appointment.status = 'cancelled'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Cancellation Approved',
            message=f'Your cancellation request for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been approved.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Cancellation request approved for {appointment.patient.full_name}.')
        
        # Log cancellation approval
        HistoryLog.objects.create(
            type='Service',  # Using Service as closest match
            name=f"Cancellation Request #{cancellation_request.id}",
            action='Edited',  # Using Edited as closest match
            performed_by=request.user.get_full_name() or request.user.username,
            details=f'Cancellation approved - Appointment ID: {appointment.id}, Patient: {appointment.patient.full_name}',
            related_id=cancellation_request.id
        )
    else:
        messages.error(request, 'This cancellation request has already been processed.')
    
    return redirect('owner:notifications')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_reject_cancellation(request, cancellation_request_id):
    """Owner reject cancellation request"""
    from appointments.models import CancellationRequest, Notification, Appointment
    from services.models import HistoryLog
    
    cancellation_request = get_object_or_404(CancellationRequest, id=cancellation_request_id)
    appointment = get_object_or_404(Appointment, id=cancellation_request.appointment_id)
    
    if cancellation_request.status == 'pending':
        # Update cancellation request status
        cancellation_request.status = 'rejected'
        cancellation_request.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Cancellation Rejected',
            message=f'Your cancellation request for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been rejected. Please contact us for more information.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Cancellation request rejected for {appointment.patient.full_name}.')
        
        # Log cancellation rejection
        HistoryLog.objects.create(
            type='Service',  # Using Service as closest match
            name=f"Cancellation Request #{cancellation_request.id}",
            action='Edited',  # Using Edited as closest match
            performed_by=request.user.get_full_name() or request.user.username,
            details=f'Cancellation rejected - Appointment ID: {appointment.id}, Patient: {appointment.patient.full_name}',
            related_id=cancellation_request.id
        )
    else:
        messages.error(request, 'This cancellation request has already been processed.')
    
    return redirect('owner:notifications')


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_manage_clinic_hours(request):
    """Owner manage clinic hours"""
    from accounts.models import StoreHours
    
    if request.method == 'POST':
        # Update store hours for each day
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in days:
            open_time = request.POST.get(f'{day.lower()}_open_time', '')
            close_time = request.POST.get(f'{day.lower()}_close_time', '')
            is_closed = request.POST.get(f'{day.lower()}_closed', '') == 'on'
            
            store_hours, created = StoreHours.objects.get_or_create(
                day_of_week=day,
                defaults={
                    'open_time': open_time if open_time else '09:00:00',
                    'close_time': close_time if close_time else '17:00:00',
                    'is_closed': is_closed
                }
            )
            
            if not created:
                if open_time:
                    store_hours.open_time = open_time
                if close_time:
                    store_hours.close_time = close_time
                store_hours.is_closed = is_closed
                store_hours.save()
        
        messages.success(request, 'Clinic hours updated successfully.')
        return redirect('owner:manage_clinic_hours')
    
    # GET request - show current clinic hours
    store_hours = StoreHours.objects.all().order_by('day_of_week')
    store_hours_dict = {sh.day_of_week: sh for sh in store_hours}
    
    # Ensure all days are present
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days:
        if day not in store_hours_dict:
            store_hours_dict[day] = StoreHours(
                day_of_week=day,
                open_time='09:00:00',
                close_time='17:00:00',
                is_closed=(day == 'Sunday')
            )
    
    context = {
        'store_hours': [store_hours_dict[day] for day in days],
    }
    
    return render(request, 'owner/manage_clinic_hours.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_backup_database(request):
    """Owner database backup management page"""
    import os
    import subprocess
    from django.conf import settings
    from django.contrib import messages
    from pathlib import Path
    
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)
    
    # Handle backup creation
    if request.method == 'POST' and 'create_backup' in request.POST:
        try:
            compress = request.POST.get('compress', 'off') == 'on'
            
            # Call the management command
            cmd = ['python', 'manage.py', 'backup_database', '--output-dir', str(backup_dir)]
            if compress:
                cmd.append('--compress')
            
            result = subprocess.run(
                cmd,
                cwd=settings.BASE_DIR,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                messages.success(request, 'Database backup created successfully!')
            else:
                messages.error(request, f'Backup failed: {result.stderr}')
        except subprocess.TimeoutExpired:
            messages.error(request, 'Backup operation timed out. Please try again.')
        except Exception as e:
            messages.error(request, f'Error creating backup: {str(e)}')
    
    # Handle backup deletion
    if request.method == 'POST' and 'delete_backup' in request.POST:
        backup_filename = request.POST.get('backup_filename')
        if backup_filename:
            backup_path = backup_dir / backup_filename
            if backup_path.exists() and backup_path.is_file():
                try:
                    backup_path.unlink()
                    messages.success(request, f'Backup {backup_filename} deleted successfully.')
                except Exception as e:
                    messages.error(request, f'Error deleting backup: {str(e)}')
            else:
                messages.error(request, 'Backup file not found.')
    
    # Get list of backup files
    backup_files = []
    if backup_dir.exists():
        for file in backup_dir.iterdir():
            if file.is_file() and (file.name.startswith('db_backup_') and 
                                   (file.suffix in ['.sqlite3', '.sql'] or file.suffix == '.gz')):
                file_stat = file.stat()
                backup_files.append({
                    'filename': file.name,
                    'size': file_stat.st_size,
                    'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                    'created': datetime.fromtimestamp(file_stat.st_mtime),
                    'is_compressed': file.suffix == '.gz',
                })
    
    # Sort by creation time (newest first)
    backup_files.sort(key=lambda x: x['created'], reverse=True)
    
    # Get database info
    db_config = settings.DATABASES['default']
    db_engine = db_config['ENGINE']
    db_name = db_config.get('NAME', 'Unknown')
    
    context = {
        'backup_files': backup_files,
        'backup_dir': backup_dir,
        'db_engine': db_engine,
        'db_name': str(db_name),
        'backup_count': len(backup_files),
    }
    
    return render(request, 'owner/backup_database.html', context)


@login_required(login_url='/accounts/login/owner/')
@user_passes_test(is_owner, login_url='/accounts/login/owner/')
def owner_download_backup(request, filename):
    """Download a backup file"""
    from django.http import FileResponse, Http404
    from django.conf import settings
    from pathlib import Path
    import os
    
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    backup_path = backup_dir / filename
    
    # Security check: ensure file is in backup directory and is a backup file
    if not backup_path.exists() or not backup_path.is_file():
        raise Http404("Backup file not found.")
    
    if not (filename.startswith('db_backup_') and 
            (filename.endswith('.sqlite3') or filename.endswith('.sql') or 
             filename.endswith('.sqlite3.gz') or filename.endswith('.sql.gz'))):
        raise Http404("Invalid backup file.")
    
    # Ensure the file is within the backup directory (prevent directory traversal)
    try:
        backup_path.resolve().relative_to(backup_dir.resolve())
    except ValueError:
        raise Http404("Invalid backup file path.")
    
    response = FileResponse(
        open(backup_path, 'rb'),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
