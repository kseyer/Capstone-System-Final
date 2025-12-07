from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum
from django.http import JsonResponse
from .models import Appointment, Notification, ClosedDay
from accounts.models import User, Attendant, AttendantProfile
from services.models import Service, ServiceImage
from products.models import Product, ProductImage
from services.utils import send_appointment_sms

def is_admin(user):
    """Check if user is staff/admin"""
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Staff dashboard - shows appointments, pre-orders, and patient list"""
    # Get today's date
    today = timezone.now().date()
    
    # Get all appointments (services and packages)
    all_appointments = Appointment.objects.filter(
        Q(service__isnull=False) | Q(package__isnull=False)
    ).order_by('-appointment_date', '-appointment_time')[:10]
    
    # Get pre-orders (product appointments)
    pre_orders = Appointment.objects.filter(
        product__isnull=False
    ).order_by('-appointment_date', '-appointment_time')[:10]
    
    # Get patient list
    patients = User.objects.filter(user_type='patient').order_by('-date_joined')[:10]
    
    # Get statistics
    total_appointments = Appointment.objects.filter(
        Q(service__isnull=False) | Q(package__isnull=False)
    ).count()
    pending_count = Appointment.objects.filter(
        status='pending',
        product__isnull=True
    ).count()
    confirmed_count = Appointment.objects.filter(
        status='confirmed',
        product__isnull=True
    ).count()
    pre_order_count = Appointment.objects.filter(product__isnull=False).count()
    total_patients = User.objects.filter(user_type='patient').count()
    
    context = {
        'all_appointments': all_appointments,
        'pre_orders': pre_orders,
        'patients': patients,
        'total_appointments': total_appointments,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'pre_order_count': pre_order_count,
        'total_patients': total_patients,
        'today': today,
    }
    
    return render(request, 'appointments/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def admin_appointments(request):
    """Admin view for all appointments"""
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
    
    return render(request, 'appointments/admin_appointments.html', context)

@login_required
@user_passes_test(is_admin)
def admin_appointment_detail(request, appointment_id):
    """Admin view for appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    context = {
        'appointment': appointment,
        'attendants': Attendant.objects.all().order_by('first_name', 'last_name'),
    }
    
    return render(request, 'appointments/admin_appointment_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_mark_attendant_unavailable(request, appointment_id):
    """Mark attendant as unavailable - triggers patient 3-option flow"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        
        if not reason:
            messages.error(request, 'Please provide a reason for unavailability.')
            return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
        
        # Create unavailability request
        from .models import AttendantUnavailabilityRequest
        unavailability_request = AttendantUnavailabilityRequest.objects.create(
            appointment=appointment,
            reason=reason,
            status='pending'
        )
        
        # Create notification for patient with 3 options
        Notification.objects.create(
            type='appointment',
            appointment_id=appointment.id,
            title='Attendant Unavailable - Please Choose an Option',
            message=f'Your assigned attendant {appointment.attendant.first_name} {appointment.attendant.last_name} is unavailable for your appointment on {appointment.appointment_date} at {appointment.appointment_time}. Reason: {reason}. Please choose one of the following options: 1) Choose another attendant, 2) Reschedule with same attendant, or 3) Cancel appointment.',
            patient=appointment.patient
        )
        
        # Send SMS notification
        sms_result = send_appointment_sms(
            appointment,
            'unavailable',
            reason=reason,
            unavailability_request_id=unavailability_request.id
        )
        
        messages.success(request, f'Patient has been notified. They will receive options to choose another attendant, reschedule, or cancel.')
        return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)


@login_required
@user_passes_test(is_admin)
def admin_reassign_attendant(request, appointment_id):
    """Reassign an appointment to a different attendant and notify the patient"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method != 'POST':
        messages.error(request, 'Invalid request method for reassigning attendants.')
        return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
    
    attendant_id = request.POST.get('attendant_id')
    note = request.POST.get('note', '').strip()
    
    if not attendant_id:
        messages.error(request, 'Please select a staff member to assign.')
        return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
    
    try:
        new_attendant = Attendant.objects.get(id=attendant_id)
    except Attendant.DoesNotExist:
        messages.error(request, 'Selected staff member does not exist.')
        return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
    
    previous_attendant = appointment.attendant
    if previous_attendant == new_attendant:
        messages.info(request, f'{new_attendant.first_name} {new_attendant.last_name} is already assigned to this appointment.')
        return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
    
    appointment.attendant = new_attendant
    appointment.save()
    
    # Create a notification for the patient
    message_body = (
        f'Your appointment on {appointment.appointment_date} at {appointment.appointment_time} '
        f'will now be handled by {new_attendant.first_name} {new_attendant.last_name}.'
    )
    if note:
        message_body += f' Note from staff: {note}'
    
    Notification.objects.create(
        type='appointment',
        appointment_id=appointment.id,
        title='Appointment Staff Updated',
        message=message_body,
        patient=appointment.patient
    )
    
    # Send SMS notification
    sms_result = send_appointment_sms(
        appointment,
        'reassignment',
        previous_attendant=previous_attendant
    )
    
    if sms_result.get('success'):
        messages.success(
            request,
            f'Appointment reassigned to {new_attendant.first_name} {new_attendant.last_name}. Patient notified via SMS.'
        )
    else:
        messages.warning(
            request,
            f'Appointment reassigned to {new_attendant.first_name} {new_attendant.last_name}, '
            'but SMS notification could not be sent.'
        )
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_confirm_appointment(request, appointment_id):
    """Admin confirm an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status == 'pending':
        appointment.status = 'confirmed'
        appointment.save()
        
        # If this is a product pre-order, deduct stock
        if appointment.product:
            product = appointment.product
            if product.stock > 0:
                product.stock -= 1
                product.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='confirmation',
            appointment_id=appointment.id,
            title='Appointment Confirmed',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed.',
            patient=appointment.patient
        )
        
        # Notify owner of appointment confirmation (single notification for all owners)
        Notification.objects.create(
            type='confirmation',
            appointment_id=appointment.id,
            title='Appointment Confirmed',
            message=f'Appointment for {appointment.patient.get_full_name()} - {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed.',
            patient=None  # Owner notification
        )
        
        # Send SMS confirmation
        sms_result = send_appointment_sms(appointment, 'confirmation')
        if sms_result['success']:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been confirmed. SMS sent.')
        else:
            messages.success(request, f'Appointment for {appointment.patient.full_name} has been confirmed. (SMS failed)')
        
        # Log appointment confirmation
        log_appointment_history('confirm', appointment, request.user)
    else:
        messages.error(request, 'Only pending appointments can be confirmed.')
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_complete_appointment(request, appointment_id):
    """Admin mark appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status in ['pending', 'confirmed']:
        appointment.status = 'completed'
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='appointment',
            appointment_id=appointment.id,
            title='Appointment Completed',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} has been completed. Thank you for choosing Skinovation Beauty Clinic!',
            patient=appointment.patient
        )
        
        messages.success(request, f'Appointment for {appointment.patient.full_name} has been marked as completed.')
        
        # Log appointment completion
        log_appointment_history('complete', appointment, request.user)
    else:
        messages.error(request, 'Only pending or confirmed appointments can be completed.')
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_cancel_appointment(request, appointment_id):
    """Admin cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'Cancellation reason is required.')
            return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)
    
    if appointment.status in ['pending', 'confirmed']:
        # Get reason from POST or set default
        reason = request.POST.get('reason', '').strip() if request.method == 'POST' else 'Cancelled by admin'
        
        appointment.status = 'cancelled'
        appointment.save()
        
        # Create cancellation request record with reason
        from .models import CancellationRequest
        appointment_type = 'package' if appointment.package else 'regular'
        CancellationRequest.objects.create(
            appointment_id=appointment.id,
            appointment_type=appointment_type,
            patient=appointment.patient,
            reason=reason,
            status='approved'  # Auto-approved since admin is cancelling
        )
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Appointment Cancelled',
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been cancelled. Please contact us to reschedule.',
            patient=appointment.patient
        )
        
        # Notify owner of appointment cancellation (single notification for all owners)
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
        
        # Log appointment cancellation
        log_appointment_history('cancel', appointment, request.user)
    else:
        messages.error(request, 'Only pending or confirmed appointments can be cancelled.')
    
    return redirect('appointments:admin_appointment_detail', appointment_id=appointment_id)

@login_required
@user_passes_test(is_admin)
def admin_maintenance(request):
    """Admin maintenance page"""
    from services.models import Service
    from packages.models import Package
    from products.models import Product
    
    services_count = Service.objects.count()
    packages_count = Package.objects.count()
    products_count = Product.objects.count()
    
    # Get recent activity (example - you can expand this)
    recent_services = Service.objects.all().order_by('-id')[:5]
    
    context = {
        'services_count': services_count,
        'packages_count': packages_count,
        'products_count': products_count,
        'recent_services': recent_services,
    }
    
    return render(request, 'appointments/admin_maintenance.html', context)

@login_required
@user_passes_test(is_admin)
def admin_patients(request):
    """Admin patients management page"""
    from accounts.models import User
    
    # Get all patients (non-admin users)
    patients = User.objects.filter(user_type='patient').order_by('-id')
    
    # Get statistics for each patient
    patient_stats = []
    for patient in patients:
        appointments = Appointment.objects.filter(patient=patient)
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        
        # Count packages (you might need to adjust this based on your model)
        packages_count = appointments.filter(package__isnull=False).count()
        
        # Get last visit
        last_visit = appointments.filter(status='completed').order_by('-appointment_date').first()
        last_visit_date = last_visit.appointment_date if last_visit else None
        
        patient_stats.append({
            'patient': patient,
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'packages_count': packages_count,
            'last_visit': last_visit_date,
        })
    
    context = {
        'patient_stats': patient_stats,
    }
    
    return render(request, 'appointments/admin_patients.html', context)

@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    """Admin notifications management page"""
    notifications = Notification.objects.all().order_by('-created_at')
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'appointments/admin_notifications.html', context)

def get_attendant_display_name(user):
    """Get formatted display name for attendant: 'Attendant X - First Last'"""
    # Extract number from username (e.g., 'attendant1' -> 1)
    import re
    match = re.search(r'attendant(\d+)', user.username.lower())
    if match:
        number = match.group(1)
        name = user.get_full_name() or user.username
        return f"Attendant {number} - {name}"
    # Fallback if username doesn't match pattern
    return user.get_full_name() or user.username


@login_required
@user_passes_test(is_admin)
def admin_settings(request):
    """Admin settings page"""
    from .models import ClosedDay
    
    closed_days = ClosedDay.objects.all()
    # Get all attendant users for the table (both active and inactive)
    attendant_users = User.objects.filter(user_type='attendant').order_by('username')
    # Get only active attendant users for the calendar view
    active_attendant_users = User.objects.filter(user_type='attendant', is_active=True).order_by('username')
    
    # Get attendant profiles - create list of tuples for easier template access
    attendant_users_with_profiles = []
    attendant_display_names = {}
    for user in attendant_users:
        try:
            profile = user.attendant_profile
            attendant_users_with_profiles.append((user, profile))
        except AttendantProfile.DoesNotExist:
            attendant_users_with_profiles.append((user, None))
        except Exception as e:
            # Handle any database errors gracefully
            from django.db import OperationalError
            if isinstance(e, OperationalError):
                # If there's a database error, try to continue without profile
                attendant_users_with_profiles.append((user, None))
            else:
                attendant_users_with_profiles.append((user, None))
        # Store display name for template
        attendant_display_names[user.id] = get_attendant_display_name(user)
    
    # Create a list of hours for the schedule
    hours = ['10', '11', '12', '13', '14', '15', '16', '17', '18']
    
    # Check if today is a closed day
    today = timezone.now().date()
    is_today_closed = ClosedDay.objects.filter(date=today).exists()
    
    context = {
        'closed_days': closed_days,
        'hours': hours,
        'attendant_users': attendant_users,
        'active_attendant_users': active_attendant_users,
        'attendant_users_with_profiles': attendant_users_with_profiles,
        'attendant_display_names': attendant_display_names,
        'is_today_closed': is_today_closed,
        'today': today,
    }
    
    return render(request, 'appointments/admin_settings.html', context)

@login_required
@user_passes_test(is_admin)
def admin_add_attendant(request):
    """Add new attendant"""
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
    
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_delete_attendant(request, attendant_id):
    """Delete attendant"""
    attendant = get_object_or_404(Attendant, id=attendant_id)
    attendant_name = f"{attendant.first_name} {attendant.last_name}"
    attendant.delete()
    
    messages.success(request, f'Attendant {attendant_name} deleted successfully.')
    return redirect('appointments:admin_settings')


@login_required
@user_passes_test(is_admin)
def admin_create_attendant_user(request):
    """Create a new attendant user account"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        if not all([username, password, first_name, last_name, email, phone]):
            messages.error(request, 'Username, password, first name, last name, email, and phone number are required.')
            return redirect('appointments:admin_settings')
        
        # Validate email format
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('appointments:admin_settings')
        
        # Validate phone number format
        import re
        phone_digits = re.sub(r'\D', '', phone)
        if len(phone_digits) != 11 or not phone_digits.startswith('09'):
            messages.error(request, 'Please enter a valid 11-digit Philippine phone number starting with 09 (e.g., 09123456789).')
            return redirect('appointments:admin_settings')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken. Please choose another one.')
            return redirect('appointments:admin_settings')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'That email is already registered. Please use a different email address.')
            return redirect('appointments:admin_settings')
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone_digits,
            user_type='attendant',
            is_active=True
        )
        user.set_password(password)
        user.save()
        
        # Create corresponding Attendant object so it appears in booking pages
        from django.utils import timezone
        from datetime import date, time
        Attendant.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={
                'shift_date': date.today(),
                'shift_time': time(10, 0)  # Default to 10:00 AM
            }
        )
        
        messages.success(request, f'Profile created for {first_name} {last_name}.')
    
    return redirect('appointments:admin_settings')


@login_required
@user_passes_test(is_admin)
def admin_toggle_attendant_user(request, user_id):
    """Activate or deactivate an attendant user account"""
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    user.is_active = not user.is_active
    user.archived = not user.is_active
    user.save()
    
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'Attendant account {user.username} has been {status}.')
    return redirect('appointments:admin_settings')


@login_required
@user_passes_test(is_admin)
def admin_edit_attendant_user(request, user_id):
    """Edit attendant user account"""
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        
        if not all([first_name, last_name, username]):
            messages.error(request, 'First name, last name, and username are required.')
            return redirect('appointments:admin_edit_attendant_user', user_id=user_id)
        
        # Check if username is taken by another user
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, 'That username is already taken. Please choose another one.')
            return redirect('appointments:admin_edit_attendant_user', user_id=user_id)
        
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = email if email else user.email
        user.middle_name = middle_name if middle_name else user.middle_name
        user.save()
        
        messages.success(request, f'Attendant account {username} has been updated successfully.')
        return redirect('appointments:admin_settings')
    
    return render(request, 'appointments/admin_edit_attendant_user.html', {'attendant_user': user})


@login_required
@user_passes_test(is_admin)
def admin_manage_attendant_profile(request, user_id):
    """Manage attendant profile (work days, hours, phone, and profile picture)"""
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    
    if request.method == 'POST':
        work_days = request.POST.getlist('work_days')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        phone = request.POST.get('phone', '').strip()
        
        if not work_days:
            messages.error(request, 'Please select at least one work day.')
            return redirect('appointments:admin_settings')
        
        if not start_time or not end_time:
            messages.error(request, 'Please provide both start and end times.')
            return redirect('appointments:admin_settings')
        
        # Validate store hours restriction (10 AM - 6 PM)
        from datetime import datetime
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        min_time = datetime.strptime('10:00', '%H:%M').time()
        max_time = datetime.strptime('18:00', '%H:%M').time()
        
        if start_time_obj < min_time or end_time_obj > max_time:
            messages.error(request, 'Shift hours must be between 10:00 AM and 6:00 PM.')
            return redirect('appointments:admin_settings')
        
        if start_time_obj >= end_time_obj:
            messages.error(request, 'Start time must be before end time.')
            return redirect('appointments:admin_settings')
        
        # Validate phone number if provided
        if phone:
            import re
            if not re.match(r'^09\d{9}$', phone):
                messages.error(request, 'Phone number must be 11 digits starting with 09 (e.g., 09123456789).')
                return redirect('appointments:admin_settings')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            # Validate file type
            if profile_picture.content_type not in ['image/jpeg', 'image/jpg', 'image/png']:
                messages.error(request, 'Profile picture must be in JPG or PNG format.')
                return redirect('appointments:admin_settings')
            user.profile_picture = profile_picture
            user.save()
        
        # Get or create profile
        profile, created = AttendantProfile.objects.get_or_create(user=user)
        profile.work_days = work_days
        profile.start_time = start_time
        profile.end_time = end_time
        if phone:
            profile.phone = phone
        elif phone == '':
            profile.phone = None
        profile.save()
        
        if created:
            messages.success(request, f'Profile created for {user.get_full_name()}.')
        else:
            messages.success(request, f'Profile updated for {user.get_full_name()}.')
        
        return redirect('appointments:admin_settings')
    
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_reset_attendant_password(request, user_id):
    """Reset attendant account password and provide a temporary one"""
    from django.contrib.auth.models import User as DjangoUser
    import secrets
    import string
    
    user = get_object_or_404(User, id=user_id, user_type='attendant')
    
    # Generate a random 10-character password
    chars = string.ascii_letters + string.digits
    temp_password = ''.join(secrets.choice(chars) for _ in range(10))
    
    user.set_password(temp_password)
    user.save()
    
    messages.success(
        request,
        f'Password for {user.username} has been reset. Temporary password: {temp_password}'
    )
    return redirect('appointments:admin_settings')


@login_required
@user_passes_test(is_admin)
def admin_delete_notification(request, notification_id):
    """Delete notification"""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.delete()
    
    messages.success(request, 'Notification deleted successfully.')
    return redirect('appointments:admin_notifications')

@login_required
@user_passes_test(is_admin)
def admin_view_patient(request, patient_id):
    """View patient details"""
    from accounts.models import User
    
    patient = get_object_or_404(User, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    
    return render(request, 'appointments/admin_patient_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_edit_patient(request, patient_id):
    """View patient (Data Privacy - view only, no editing allowed)"""
    from accounts.models import User
    
    patient = get_object_or_404(User, id=patient_id, user_type='patient')
    
    # Data Privacy Act compliance - Staff can only VIEW patient profiles, not edit
    messages.info(request, 'Staff can only view patient profiles. Editing is restricted to comply with Data Privacy Act.')
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    
    return render(request, 'appointments/admin_patient_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_delete_patient(request, patient_id):
    """Delete patient"""
    from accounts.models import User
    
    patient = get_object_or_404(User, id=patient_id)
    patient_name = patient.full_name
    patient.delete()
    
    messages.success(request, f'Patient {patient_name} deleted successfully.')
    return redirect('appointments:admin_patients')

@login_required
@user_passes_test(is_admin)
def admin_add_closed_day(request):
    """Add closed day"""
    if request.method == 'POST':
        from .models import ClosedDay
        
        date = request.POST.get('start_date')
        reason = request.POST.get('reason')
        
        if date and reason:
            try:
                ClosedDay.objects.create(date=date, reason=reason)
                messages.success(request, f'Closed day {date} added successfully.')
            except Exception as e:
                messages.error(request, f'Error adding closed day: {str(e)}')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_delete_closed_day(request, closed_day_id):
    """Delete closed day"""
    from .models import ClosedDay
    
    closed_day = get_object_or_404(ClosedDay, id=closed_day_id)
    closed_day.delete()
    
    messages.success(request, 'Closed day deleted successfully.')
    return redirect('appointments:admin_settings')

@login_required
@user_passes_test(is_admin)
def admin_cancellation_requests(request):
    """Admin view for cancellation and reschedule requests"""
    from .models import CancellationRequest, RescheduleRequest, Appointment
    
    cancellation_requests = CancellationRequest.objects.all().order_by('-created_at')
    reschedule_requests = RescheduleRequest.objects.all().order_by('-created_at')
    
    # Get appointments for reschedule requests
    reschedule_requests_with_appointments = []
    for reschedule_request in reschedule_requests:
        try:
            appointment = Appointment.objects.get(id=reschedule_request.appointment_id)
            reschedule_requests_with_appointments.append((reschedule_request, appointment))
        except Appointment.DoesNotExist:
            reschedule_requests_with_appointments.append((reschedule_request, None))
    
    # Get appointments for cancellation requests
    cancellation_requests_with_appointments = []
    for cancellation_request in cancellation_requests:
        try:
            appointment = Appointment.objects.get(id=cancellation_request.appointment_id)
            cancellation_requests_with_appointments.append((cancellation_request, appointment))
        except Appointment.DoesNotExist:
            cancellation_requests_with_appointments.append((cancellation_request, None))
    
    context = {
        'cancellation_requests': cancellation_requests,
        'reschedule_requests': reschedule_requests,
        'reschedule_requests_with_appointments': reschedule_requests_with_appointments,
        'cancellation_requests_with_appointments': cancellation_requests_with_appointments,
    }
    
    return render(request, 'appointments/admin_reschedules_cancellations.html', context)

@login_required
@user_passes_test(is_admin)
def admin_approve_cancellation(request, request_id):
    """Admin approve cancellation request"""
    from .models import CancellationRequest
    
    cancellation_request = get_object_or_404(CancellationRequest, id=request_id)
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
        from .models import HistoryLog
        HistoryLog.objects.create(
            action_type='approve',
            item_type='cancellation_request',
            item_id=cancellation_request.id,
            item_name=f"Cancellation Request #{cancellation_request.id} - {appointment.patient.get_full_name()}",
            performed_by=request.user,
            details={
                'appointment_id': appointment.id,
                'patient': appointment.patient.get_full_name(),
                'reason': cancellation_request.reason or '',
            }
        )
    else:
        messages.error(request, 'This cancellation request has already been processed.')
    
    return redirect('appointments:admin_cancellation_requests')

@login_required
@user_passes_test(is_admin)
def admin_reject_cancellation(request, request_id):
    """Admin reject cancellation request"""
    from .models import CancellationRequest
    
    cancellation_request = get_object_or_404(CancellationRequest, id=request_id)
    appointment = get_object_or_404(Appointment, id=cancellation_request.appointment_id)
    
    if cancellation_request.status == 'pending':
        # Update cancellation request status
        cancellation_request.status = 'rejected'
        cancellation_request.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='cancellation',
            appointment_id=appointment.id,
            title='Cancellation Request Rejected',
            message=f'Your cancellation request for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been rejected. Please contact us for more information.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Cancellation request rejected for {appointment.patient.full_name}.')
        
        # Log cancellation rejection
        from .models import HistoryLog
        HistoryLog.objects.create(
            action_type='reject',
            item_type='cancellation_request',
            item_id=cancellation_request.id,
            item_name=f"Cancellation Request #{cancellation_request.id} - {appointment.patient.get_full_name()}",
            performed_by=request.user,
            details={
                'appointment_id': appointment.id,
                'patient': appointment.patient.get_full_name(),
                'reason': cancellation_request.reason or '',
            }
        )
    else:
        messages.error(request, 'This cancellation request has already been processed.')
    
    return redirect('appointments:admin_cancellation_requests')


@login_required
@user_passes_test(is_admin)
def admin_approve_reschedule(request, request_id):
    """Admin approve reschedule request"""
    from .models import RescheduleRequest
    
    reschedule_request = get_object_or_404(RescheduleRequest, id=request_id)
    appointment = get_object_or_404(Appointment, id=reschedule_request.appointment_id)
    
    if reschedule_request.status == 'pending':
        # Check if the new date is a closed clinic day
        if ClosedDay.objects.filter(date=reschedule_request.new_appointment_date).exists():
            closed_day = ClosedDay.objects.get(date=reschedule_request.new_appointment_date)
            reason_text = f" ({closed_day.reason})" if closed_day.reason else ""
            messages.error(request, f'Cannot approve reschedule: The clinic is closed on {reschedule_request.new_appointment_date.strftime("%B %d, %Y")}{reason_text}.')
            return redirect('appointments:admin_cancellation_requests')
        
        # Update reschedule request status
        reschedule_request.status = 'approved'
        reschedule_request.save()
        
        # Update the appointment with new date and time
        old_date = appointment.appointment_date
        old_time = appointment.appointment_time
        appointment.appointment_date = reschedule_request.new_appointment_date
        appointment.appointment_time = reschedule_request.new_appointment_time
        appointment.status = 'pending'  # Set to pending after reschedule
        appointment.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Reschedule Request Approved',
            message=f'Your reschedule request for {appointment.get_service_name()} has been approved. New date and time: {reschedule_request.new_appointment_date} at {reschedule_request.new_appointment_time}.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Reschedule request approved for {appointment.patient.full_name}.')
        
        # Log reschedule approval
        log_appointment_history('reschedule', appointment, request.user, {
            'old_date': str(old_date),
            'old_time': str(old_time),
            'new_date': str(reschedule_request.new_appointment_date),
            'new_time': str(reschedule_request.new_appointment_time),
            'reschedule_request_id': reschedule_request.id,
        })
    else:
        messages.error(request, 'This reschedule request has already been processed.')
    
    return redirect('appointments:admin_cancellation_requests')


@login_required
@user_passes_test(is_admin)
def admin_reject_reschedule(request, request_id):
    """Admin reject reschedule request"""
    from .models import RescheduleRequest
    
    reschedule_request = get_object_or_404(RescheduleRequest, id=request_id)
    appointment = get_object_or_404(Appointment, id=reschedule_request.appointment_id)
    
    if reschedule_request.status == 'pending':
        # Update reschedule request status
        reschedule_request.status = 'rejected'
        reschedule_request.save()
        
        # Create notification for patient
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Reschedule Request Rejected',
            message=f'Your reschedule request for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been rejected. Please contact us for more information.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Reschedule request rejected for {appointment.patient.full_name}.')
        
        # Log reschedule rejection
        from .models import HistoryLog
        HistoryLog.objects.create(
            action_type='reject',
            item_type='reschedule_request',
            item_id=reschedule_request.id,
            item_name=f"Reschedule Request #{reschedule_request.id} - {appointment.patient.get_full_name()}",
            performed_by=request.user,
            details={
                'appointment_id': appointment.id,
                'patient': appointment.patient.get_full_name(),
                'requested_date': str(reschedule_request.new_appointment_date),
                'requested_time': str(reschedule_request.new_appointment_time),
            }
        )
    else:
        messages.error(request, 'This reschedule request has already been processed.')
    
    return redirect('appointments:admin_cancellation_requests')


@login_required
@user_passes_test(is_admin)
def admin_manage_service_images(request):
    """Admin view to manage service images"""
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
    return render(request, 'appointments/admin_manage_service_images.html', context)


@login_required
@user_passes_test(is_admin)
def admin_manage_product_images(request):
    """Admin view to manage product images"""
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
    return render(request, 'appointments/admin_manage_product_images.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_service_image(request, image_id):
    """Delete a service image"""
    image = get_object_or_404(ServiceImage, id=image_id)
    service_name = image.service.service_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {service_name}')
    return redirect('appointments:admin_manage_service_images')


@login_required
@user_passes_test(is_admin)
def admin_delete_product_image(request, image_id):
    """Delete a product image"""
    image = get_object_or_404(ProductImage, id=image_id)
    product_name = image.product.product_name
    image.delete()
    messages.success(request, f'Image deleted successfully for {product_name}')
    return redirect('appointments:admin_manage_product_images')


@login_required
@user_passes_test(is_admin)
def admin_set_primary_service_image(request, image_id):
    """Set a service image as primary"""
    image = get_object_or_404(ServiceImage, id=image_id)
    # Unset other primary images for this service
    ServiceImage.objects.filter(service=image.service, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.service.service_name}')
    return redirect('appointments:admin_manage_service_images')


@login_required
@user_passes_test(is_admin)
def admin_set_primary_product_image(request, image_id):
    """Set a product image as primary"""
    image = get_object_or_404(ProductImage, id=image_id)
    # Unset other primary images for this product
    ProductImage.objects.filter(product=image.product, is_primary=True).update(is_primary=False)
    # Set this image as primary
    image.is_primary = True
    image.save()
    messages.success(request, f'Primary image updated for {image.product.product_name}')
    return redirect('appointments:admin_manage_product_images')


@login_required
@user_passes_test(is_admin)
def admin_view_feedback(request):
    """Staff view patient feedback - Only shows service/package/product ratings, not attendant ratings (private)"""
    from .models import Feedback
    
    # Get all feedback, but exclude attendant_rating in display (Data Privacy - attendant feedback is private)
    feedbacks = Feedback.objects.all().order_by('-created_at')
    
    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(feedbacks, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'feedbacks': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'appointments/admin_feedback.html', context)


@login_required
@user_passes_test(is_admin)
def admin_inventory(request):
    """Staff inventory management for products"""
    products = Product.objects.all().order_by('product_name')
    
    # Get low stock products (stock < 10)
    low_stock_products = products.filter(stock__lt=10)
    
    # Get out of stock products
    out_of_stock_products = products.filter(stock=0)
    
    # Statistics
    total_products = products.count()
    total_stock_value = sum(p.price * p.stock for p in products)
    low_stock_count = low_stock_products.count()
    out_of_stock_count = out_of_stock_products.count()
    
    context = {
        'products': products,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_products': total_products,
        'total_stock_value': total_stock_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
    }
    
    return render(request, 'appointments/admin_inventory.html', context)


def log_appointment_history(action_type, appointment, performed_by, details=None):
    """Helper function to log appointment history"""
    from .models import HistoryLog
    
    # Get appointment name
    if appointment.service:
        item_name = f"{appointment.service.service_name} - {appointment.patient.get_full_name()}"
    elif appointment.product:
        item_name = f"{appointment.product.product_name} - {appointment.patient.get_full_name()}"
    elif appointment.package:
        item_name = f"{appointment.package.package_name} - {appointment.patient.get_full_name()}"
    else:
        item_name = f"Appointment #{appointment.id} - {appointment.patient.get_full_name()}"
    
    # Prepare details
    log_details = {
        'appointment_id': appointment.id,
        'patient': appointment.patient.get_full_name(),
        'date': str(appointment.appointment_date),
        'time': str(appointment.appointment_time),
        'status': appointment.status,
    }
    if details:
        log_details.update(details)
    
    HistoryLog.objects.create(
        action_type=action_type,
        item_type='appointment',
        item_id=appointment.id,
        item_name=item_name,
        performed_by=performed_by,
        details=log_details
    )


@login_required
@user_passes_test(is_admin)
def admin_history_log(request):
    """Admin view for history log with filtering"""
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
    return render(request, 'appointments/admin_history_log.html', context)


@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    """Admin analytics dashboard - same as owner but for staff"""
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
    
    return render(request, 'appointments/admin_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def admin_update_stock(request, product_id):
    """Update product stock"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')  # 'add' or 'set'
        quantity_raw = request.POST.get('quantity', '').strip()
        
        # Validate quantity input
        try:
            quantity = int(quantity_raw)
        except (TypeError, ValueError):
            messages.error(request, 'Please enter a valid whole number for the quantity.')
            return redirect('appointments:admin_inventory')
        
        if quantity < 0:
            messages.error(request, 'Quantity cannot be negative.')
            return redirect('appointments:admin_inventory')
        
        if action == 'add':
            product.stock += quantity
            messages.success(request, f'Added {quantity} unit{"s" if quantity != 1 else ""} to {product.product_name}. New stock: {product.stock}')
        elif action == 'set':
            product.stock = quantity
            messages.success(request, f'Stock for {product.product_name} set to {quantity}')
        else:
            messages.error(request, 'Unknown stock action. Please try again.')
            return redirect('appointments:admin_inventory')
        
        if product.stock < 0:
            product.stock = 0
            messages.warning(request, f'Stock for {product.product_name} cannot go below zero. Reset to 0.')
        
        product.save()
        
        # Check if product is now available for pre-ordering
        if product.stock > 0 and product.stock < 10:
            messages.warning(request, f'{product.product_name} is running low on stock ({product.stock} units remaining).')
        elif product.stock == 0:
            messages.info(request, f'{product.product_name} is now out of stock. Patients will be unable to pre-order until replenished.')
        
        return redirect('appointments:admin_inventory')
    
    return redirect('appointments:admin_inventory')


def log_admin_history(item_type, item_name, action, performed_by, details='', related_id=None):
    """Helper function to log history"""
    from services.models import HistoryLog
    
    HistoryLog.objects.create(
        type=item_type,
        name=item_name,
        action=action,
        performed_by=performed_by,
        details=details,
        related_id=related_id
    )


@login_required
@user_passes_test(is_admin)
def admin_manage_services(request):
    """Staff manage services - same interface as owner"""
    from services.models import Service, ServiceCategory
    from django.core.paginator import Paginator
    
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
                    log_admin_history('Service', service_name, 'Added', request.user.get_full_name() or request.user.username, 
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
            log_admin_history('Service', service.service_name, 'Edited', request.user.get_full_name() or request.user.username,
                       f'Updated: {old_name} -> {service.service_name}', service.id)
            messages.success(request, 'Service updated successfully!')
        
        elif action == 'delete' or action == 'archive':
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            service_name = service.service_name
            service.archived = True
            service.save()
            log_admin_history('Service', service_name, 'Deleted', request.user.get_full_name() or request.user.username,
                       f'Service archived', service.id)
            messages.success(request, 'Service archived successfully!')
        
        return redirect('appointments:admin_manage_services')
    
    # Add pagination
    paginator = Paginator(services, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ServiceCategory.objects.all()
    context = {
        'services': page_obj,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'appointments/admin_manage_services.html', context)


@login_required
@user_passes_test(is_admin)
def admin_manage_packages(request):
    """Staff manage packages - same interface as owner"""
    from packages.models import Package
    from django.core.paginator import Paginator
    
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
                    log_admin_history('Package', package_name, 'Added', request.user.get_full_name() or request.user.username,
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
            log_admin_history('Package', package.package_name, 'Edited', request.user.get_full_name() or request.user.username,
                       f'Updated: {old_name} -> {package.package_name}', package.id)
            messages.success(request, 'Package updated successfully!')
        
        elif action == 'delete' or action == 'archive':
            package_id = request.POST.get('package_id')
            package = get_object_or_404(Package, id=package_id)
            package_name = package.package_name
            package.archived = True
            package.save()
            log_admin_history('Package', package_name, 'Deleted', request.user.get_full_name() or request.user.username,
                       f'Package archived', package.id)
            messages.success(request, 'Package archived successfully!')
        
        return redirect('appointments:admin_manage_packages')
    
    # Add pagination
    paginator = Paginator(packages, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'packages': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'appointments/admin_manage_packages.html', context)


@login_required
@user_passes_test(is_admin)
def admin_manage_products(request):
    """Staff manage products - same interface as owner"""
    from django.core.paginator import Paginator
    
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
                    log_admin_history('Product', product_name, 'Added', request.user.get_full_name() or request.user.username,
                               f'Price: {price}, Stock: {stock or 0}', None)
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
            log_admin_history('Product', product.product_name, 'Edited', request.user.get_full_name() or request.user.username,
                       f'Updated: {old_name} -> {product.product_name}', product.id)
            messages.success(request, 'Product updated successfully!')
        
        elif action == 'delete' or action == 'archive':
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product_name = product.product_name
            product.archived = True
            product.save()
            log_admin_history('Product', product_name, 'Deleted', request.user.get_full_name() or request.user.username,
                       f'Product archived', product.id)
            messages.success(request, 'Product archived successfully!')
        
        return redirect('appointments:admin_manage_products')
    
    # Add pagination
    paginator = Paginator(products, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'appointments/admin_manage_products.html', context)
