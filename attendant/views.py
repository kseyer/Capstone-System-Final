from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from accounts.models import User, Attendant
from appointments.models import Appointment, Notification
import json


def is_attendant(user):
    """Check if user is attendant"""
    return user.is_authenticated and user.user_type == 'attendant'


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_dashboard(request):
    """Attendant dashboard - View appointments they are in charge of"""
    today = timezone.now().date()
    
    # Get the Attendant object associated with this user
    # Try to find by exact name match first, then case-insensitive
    attendant_obj = None
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        # Try case-insensitive match
        try:
            attendant_obj = Attendant.objects.filter(
                first_name__iexact=request.user.first_name,
                last_name__iexact=request.user.last_name
            ).first()
        except:
            attendant_obj = None
    except Attendant.MultipleObjectsReturned:
        # If multiple attendants with same name, get the first one
        attendant_obj = Attendant.objects.filter(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        ).first()
    
    # Get today's appointments - show all appointments for today that have an attendant assigned
    # This ensures all appointments made by patients are visible to attendants
    today_appointments = Appointment.objects.filter(
        appointment_date=today,
        attendant__isnull=False
    ).order_by('appointment_time')
    
    # Get upcoming appointments (next 7 days) - show all with an attendant assigned
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        appointment_date__lte=today + timezone.timedelta(days=7),
        status__in=['pending', 'confirmed'],
        attendant__isnull=False
    ).order_by('appointment_date', 'appointment_time')
    
    # Get notifications regarding appointments this attendant is in charge of
    notifications = Notification.objects.filter(
        type__in=['appointment', 'confirmation', 'cancellation']
    ).order_by('-created_at')[:3]
    
    # Statistics for this attendant
    if attendant_obj:
        total_appointments = Appointment.objects.filter(attendant=attendant_obj).count()
    else:
        # Count all appointments with any attendant if no specific attendant found
        total_appointments = Appointment.objects.filter(attendant__isnull=False).count()
    today_count = today_appointments.count()
    upcoming_count = upcoming_appointments.count()
    
    # Get notification count
    notification_count = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()
    
    # Get recent patient feedback for appointments assigned to this attendant ONLY
    from appointments.models import Feedback
    recent_feedbacks = []
    feedback_count = 0
    
    if attendant_obj:
        # Only show feedback for appointments assigned to this specific attendant
        recent_feedbacks = Feedback.objects.filter(
            appointment__attendant=attendant_obj,
            attendant_rating__isnull=False
        ).select_related('patient', 'appointment').order_by('-created_at')[:5]
        
        feedback_count = Feedback.objects.filter(
            appointment__attendant=attendant_obj,
            attendant_rating__isnull=False
        ).count()
    else:
        # If no attendant object found, don't show any feedback
        # This ensures privacy - only show feedback when we can verify the attendant
        recent_feedbacks = []
        feedback_count = 0
    
    context = {
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'notifications': notifications,
        'total_appointments': total_appointments,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'today': today,
        'notification_count': notification_count,
        'recent_feedbacks': recent_feedbacks,
        'feedback_count': feedback_count,
    }
    
    return render(request, 'attendant/dashboard.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_appointments(request):
    """Attendant appointments management - Only shows appointments assigned to this attendant"""
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        attendant_obj = None
        messages.warning(request, 'No attendant profile found. Please contact staff to set up your attendant profile.')
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')
    search_query = request.GET.get('search', '')
    
    # Start with appointments assigned to this attendant only
    if attendant_obj:
        appointments = Appointment.objects.filter(attendant=attendant_obj).order_by('-created_at', '-appointment_date', '-appointment_time')
    else:
        appointments = Appointment.objects.none()
    
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
    
    return render(request, 'attendant/appointments.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_appointment_detail(request, appointment_id):
    """Attendant view appointment details - Only for assigned appointments"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify appointment is assigned to this attendant
    if appointment.attendant != attendant_obj:
        messages.error(request, 'You can only view appointments assigned to you.')
        return redirect('attendant:appointments')
    
    # Get feedback for this appointment
    from appointments.models import Feedback
    feedback = None
    attendant_feedback = None
    try:
        feedback = Feedback.objects.get(appointment=appointment)
        # Separate service/package/product feedback from attendant feedback
        attendant_feedback = {
            'rating': feedback.attendant_rating,
            'comment': feedback.comment if feedback.attendant_rating else None
        }
    except Feedback.DoesNotExist:
        pass
    
    context = {
        'appointment': appointment,
        'feedback': feedback,
        'attendant_feedback': attendant_feedback,
    }
    
    return render(request, 'attendant/appointment_detail.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_confirm_appointment(request, appointment_id):
    """Attendant confirm an appointment - Only for assigned appointments"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify appointment is assigned to this attendant
    if appointment.attendant != attendant_obj:
        messages.error(request, 'You can only confirm appointments assigned to you.')
        return redirect('attendant:appointments')
    
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
            message=f'Your appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} has been confirmed by your attendant.',
            patient=appointment.patient
        )
        
        messages.success(request, f'Appointment for {appointment.patient.full_name} has been confirmed.')
    else:
        messages.error(request, 'Only pending appointments can be confirmed.')
    
    return redirect('attendant:appointment_detail', appointment_id=appointment_id)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_complete_appointment(request, appointment_id):
    """Attendant mark appointment as completed and save treatment details - Only for assigned appointments"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify appointment is assigned to this attendant
    if appointment.attendant != attendant_obj:
        messages.error(request, 'You can only complete appointments assigned to you.')
        return redirect('attendant:appointments')
    
    if appointment.status in ['pending', 'confirmed']:
        # Mark appointment as completed
        appointment.status = 'completed'
        appointment.save()
        
        # Save treatment details (if provided via POST, otherwise create basic record)
        from appointments.models import Treatment
        
        if request.method == 'POST':
            # Get treatment details from form (if modal was used)
            treatment_notes = request.POST.get('treatment_notes', '').strip()
            products_used = request.POST.get('products_used', '').strip()
            duration_minutes = request.POST.get('duration_minutes', '').strip()
            next_appointment_recommended = request.POST.get('next_appointment_recommended', '').strip()
            
            treatment, created = Treatment.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'treatment_date': appointment.appointment_date,
                    'treatment_time': appointment.appointment_time,
                    'notes': treatment_notes if treatment_notes else None,
                    'products_used': products_used if products_used else None,
                    'duration_minutes': int(duration_minutes) if duration_minutes and duration_minutes.isdigit() else None,
                    'next_appointment_recommended': next_appointment_recommended if next_appointment_recommended else None,
                }
            )
            
            # Update if treatment already exists
            if not created:
                if treatment_notes:
                    treatment.notes = treatment_notes
                if products_used:
                    treatment.products_used = products_used
                if duration_minutes and duration_minutes.isdigit():
                    treatment.duration_minutes = int(duration_minutes)
                if next_appointment_recommended:
                    treatment.next_appointment_recommended = next_appointment_recommended
                treatment.save()
        else:
            # GET request - create basic treatment record
            Treatment.objects.get_or_create(
                appointment=appointment,
                defaults={
                    'treatment_date': appointment.appointment_date,
                    'treatment_time': appointment.appointment_time,
                }
            )
        
        # Create notification for patient prompting them to rate/leave feedback
        Notification.objects.create(
            type='appointment',
            appointment_id=appointment.id,
            title='Treatment Completed - Please Rate Your Experience',
            message=f'Your treatment for {appointment.get_service_name()} on {appointment.appointment_date} has been completed. Please rate your experience and leave feedback to help us improve our services!',
            patient=appointment.patient
        )
        
        messages.success(request, f'Treatment completed for {appointment.patient.full_name}. Patient has been notified to rate their experience.')
    else:
        messages.error(request, 'Only pending or confirmed appointments can be completed.')
    
    return redirect('attendant:appointment_detail', appointment_id=appointment_id)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_patient_profile(request, patient_id):
    """Attendant view patient profile - Only for patients with assigned appointments"""
    patient = get_object_or_404(User, id=patient_id, user_type='patient')
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Verify patient has assigned appointment with this attendant (Data Privacy compliance)
    if not Appointment.objects.filter(patient=patient, attendant=attendant_obj).exists():
        messages.error(request, 'You can only view patient profiles for appointments assigned to you.')
        return redirect('attendant:dashboard')
    
    # Get patient's appointments assigned to this attendant only
    appointments = Appointment.objects.filter(
        patient=patient,
        attendant=attendant_obj
    ).order_by('-appointment_date')
    
    # Get patient's packages (if any)
    packages = []  # Simplified for now
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'packages': packages,
    }
    
    return render(request, 'attendant/patient_profile.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_history(request):
    """Attendant view own history of completed appointments only"""
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Get only completed appointments assigned to this attendant
    completed_appointments = Appointment.objects.filter(
        attendant=attendant_obj,
        status='completed'
    ).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'completed_appointments': completed_appointments,
    }
    
    return render(request, 'attendant/history.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_feedback(request):
    """Attendant view own feedback from patients - ONLY shows feedback for their own appointments"""
    # Get the Attendant object associated with this user
    # Try to find by exact name match first
    attendant_obj = None
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        # Try to find by case-insensitive match
        try:
            attendant_obj = Attendant.objects.filter(
                first_name__iexact=request.user.first_name,
                last_name__iexact=request.user.last_name
            ).first()
        except:
            pass
    
    if not attendant_obj:
        messages.error(request, 'No attendant profile found. Please contact staff to set up your attendant profile.')
        return redirect('attendant:dashboard')
    
    # Get feedback ONLY for appointments assigned to THIS specific attendant
    # This ensures each attendant only sees their own feedback
    from appointments.models import Feedback
    from django.db.models import Q
    
    # Get filter parameters
    rating_filter = request.GET.get('rating', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search_query = request.GET.get('search', '')
    
    feedbacks = Feedback.objects.filter(
        appointment__attendant=attendant_obj,
        attendant_rating__isnull=False
    ).select_related('patient', 'appointment', 'appointment__attendant')
    
    # Apply filters
    if rating_filter:
        feedbacks = feedbacks.filter(attendant_rating=rating_filter)
    
    if date_from:
        feedbacks = feedbacks.filter(created_at__gte=date_from)
    
    if date_to:
        feedbacks = feedbacks.filter(created_at__lte=date_to)
    
    if search_query:
        feedbacks = feedbacks.filter(
            Q(patient__first_name__icontains=search_query) |
            Q(patient__last_name__icontains=search_query) |
            Q(comment__icontains=search_query) |
            Q(appointment__service__service_name__icontains=search_query) |
            Q(appointment__package__package_name__icontains=search_query)
        )
    
    feedbacks = feedbacks.order_by('-created_at')
    
    # Add pagination
    from django.core.paginator import Paginator
    paginator = Paginator(feedbacks, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'feedbacks': page_obj,
        'page_obj': page_obj,
        'attendant_obj': attendant_obj,
        'rating_filter': rating_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search_query': search_query,
    }
    
    return render(request, 'attendant/feedback.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_schedule(request):
    """Attendant view and edit their availability schedule"""
    from accounts.models import AttendantProfile
    from datetime import datetime
    
    # Get the Attendant object associated with this user
    try:
        attendant_obj = Attendant.objects.get(
            first_name=request.user.first_name,
            last_name=request.user.last_name
        )
    except Attendant.DoesNotExist:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Get or create attendant profile with work schedule
    try:
        profile = request.user.attendant_profile
    except AttendantProfile.DoesNotExist:
        profile = None
    
    if request.method == 'POST':
        work_days = request.POST.getlist('work_days')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        
        if not work_days:
            messages.error(request, 'Please select at least one work day.')
            context = {
                'attendant': attendant_obj,
                'profile': profile,
            }
            return render(request, 'attendant/schedule.html', context)
        
        if not start_time or not end_time:
            messages.error(request, 'Please provide both start and end times.')
            context = {
                'attendant': attendant_obj,
                'profile': profile,
            }
            return render(request, 'attendant/schedule.html', context)
        
        # Validate store hours restriction (10 AM - 6 PM)
        start_time_obj = datetime.strptime(start_time, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time, '%H:%M').time()
        min_time = datetime.strptime('10:00', '%H:%M').time()
        max_time = datetime.strptime('18:00', '%H:%M').time()
        
        if start_time_obj < min_time or end_time_obj > max_time:
            messages.error(request, 'Shift hours must be between 10:00 AM and 6:00 PM.')
            context = {
                'attendant': attendant_obj,
                'profile': profile,
            }
            return render(request, 'attendant/schedule.html', context)
        
        if start_time_obj >= end_time_obj:
            messages.error(request, 'Start time must be before end time.')
            context = {
                'attendant': attendant_obj,
                'profile': profile,
            }
            return render(request, 'attendant/schedule.html', context)
        
        # Get or create profile
        profile, created = AttendantProfile.objects.get_or_create(user=request.user)
        profile.work_days = work_days
        profile.start_time = start_time
        profile.end_time = end_time
        profile.save()
        
        if created:
            messages.success(request, 'Your work schedule has been created successfully.')
        else:
            messages.success(request, 'Your work schedule has been updated successfully.')
        
        return redirect('attendant:schedule')
    
    context = {
        'attendant': attendant_obj,
        'profile': profile,
    }
    
    return render(request, 'attendant/schedule.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_manage_profile(request):
    """Attendant manage their own profile (edit name, username, email)"""
    user = request.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        middle_name = request.POST.get('middle_name', '').strip()
        
        if not all([first_name, last_name, username]):
            messages.error(request, 'First name, last name, and username are required.')
            return redirect('attendant:manage_profile')
        
        # Check if username is already taken by another user
        if User.objects.filter(username=username).exclude(id=user.id).exists():
            messages.error(request, 'That username is already taken. Please choose another one.')
            return redirect('attendant:manage_profile')
        
        # Check if email is already taken by another user (if provided)
        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            messages.error(request, 'That email is already taken. Please choose another one.')
            return redirect('attendant:manage_profile')
        
        # Store old names before updating
        old_first_name = user.first_name
        old_last_name = user.last_name
        
        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        if email:
            user.email = email
        if middle_name:
            user.middle_name = middle_name
        user.save()
        
        # Update Attendant object if it exists (match by old name)
        try:
            attendant_obj = Attendant.objects.get(
                first_name=old_first_name,
                last_name=old_last_name
            )
            # Update the Attendant object with new names
            attendant_obj.first_name = first_name
            attendant_obj.last_name = last_name
            attendant_obj.save()
        except Attendant.DoesNotExist:
            # Attendant object doesn't exist - that's okay, it might be created by staff later
            pass
        except Attendant.MultipleObjectsReturned:
            # Multiple attendants with same name - update all
            Attendant.objects.filter(
                first_name=old_first_name,
                last_name=old_last_name
            ).update(first_name=first_name, last_name=last_name)
        
        messages.success(request, 'Your profile has been updated successfully.')
        return redirect('attendant:manage_profile')
    
    context = {
        'user': user,
    }
    
    return render(request, 'attendant/manage_profile.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_notifications(request):
    """Attendant notifications"""
    from django.db.models import Q
    
    # Show notifications assigned to this attendant or system notifications
    notifications = Notification.objects.filter(
        (Q(patient=request.user) | Q(patient__isnull=True)),
        type__in=['appointment', 'confirmation', 'cancellation', 'reschedule', 'system']
    ).order_by('-created_at')
    
    # Mark notifications as read
    unread_notifications = notifications.filter(is_read=False)
    for notification in unread_notifications:
        notification.is_read = True
        notification.save()
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'attendant/notifications.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def attendant_mark_notification_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.is_read = True
    notification.save()
    
    messages.success(request, 'Notification marked as read.')
    return redirect('attendant:notifications')


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def request_leave(request):
    """Attendant request sick leave/day off - one day at a time"""
    from accounts.models import AttendantLeaveRequest
    from datetime import timedelta
    
    # Get attendant profile
    try:
        profile = request.user.attendant_profile
    except:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    if request.method == 'POST':
        leave_date_str = request.POST.get('leave_date', '').strip()
        reason = request.POST.get('reason', '').strip()
        
        if not leave_date_str or not reason:
            messages.error(request, 'Please provide both a date and reason for your leave request.')
            return redirect('attendant:request_leave')
        
        try:
            from datetime import datetime
            leave_date = datetime.strptime(leave_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD.')
            return redirect('attendant:request_leave')
        
        today = timezone.now().date()
        
        # Validation: date must be in the future
        if leave_date <= today:
            messages.error(request, 'Leave request date must be in the future.')
            return redirect('attendant:request_leave')
        
        # Validation: max 30 days ahead
        max_future_date = today + timedelta(days=30)
        if leave_date > max_future_date:
            messages.error(request, 'Leave requests can only be made up to 30 days in advance.')
            return redirect('attendant:request_leave')
        
        # Check if already requested for that date
        if AttendantLeaveRequest.objects.filter(
            attendant_profile=profile,
            leave_date=leave_date
        ).exists():
            messages.error(request, f'You already have a leave request for {leave_date}.')
            return redirect('attendant:request_leave')
        
        # Create leave request
        leave_request = AttendantLeaveRequest.objects.create(
            attendant_profile=profile,
            leave_date=leave_date,
            reason=reason,
            status='pending'
        )
        
        messages.success(request, f'Leave request submitted for {leave_date}. Awaiting owner approval.')
        return redirect('attendant:view_leave_requests')
    
    # GET: Show leave request form
    today = timezone.now().date()
    max_date = today + timedelta(days=30)
    
    context = {
        'min_date': today + timedelta(days=1),  # Tomorrow
        'max_date': max_date,
    }
    
    return render(request, 'attendant/request_leave.html', context)


@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def view_leave_requests(request):
    """Attendant view their own leave requests"""
    from accounts.models import AttendantLeaveRequest
    
    # Get attendant profile
    try:
        profile = request.user.attendant_profile
    except:
        messages.error(request, 'No attendant profile found. Please contact staff.')
        return redirect('attendant:dashboard')
    
    # Get all leave requests for this attendant, ordered by date
    leave_requests = AttendantLeaveRequest.objects.filter(
        attendant_profile=profile
    ).order_by('-leave_date')
    
    # Separate by status
    pending_requests = leave_requests.filter(status='pending')
    approved_requests = leave_requests.filter(status='approved')
    rejected_requests = leave_requests.filter(status='rejected')
    
    context = {
        'pending_requests': pending_requests,
        'approved_requests': approved_requests,
        'rejected_requests': rejected_requests,
        'all_requests': leave_requests,
    }
    
    return render(request, 'attendant/view_leave_requests.html', context)


# API Endpoints for notifications
@csrf_exempt
@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def get_notifications_api(request):
    """API endpoint to get notifications for attendant"""
    try:
        # Filter notifications for the current attendant user
        notifications = Notification.objects.filter(
            patient=request.user,
            type__in=['appointment', 'confirmation', 'cancellation']
        ).order_by('-created_at')[:20]
        
        unread_count = notifications.filter(is_read=False).count()
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'notification_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'created_at_formatted': notification.created_at.strftime('%b %d, %Y %I:%M %p'),
                'is_read': notification.is_read,
                'type': notification.type
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@csrf_exempt
@login_required(login_url='/accounts/login/attendant/')
@user_passes_test(is_attendant, login_url='/accounts/login/attendant/')
def update_notifications_api(request):
    """API endpoint to update notifications"""
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'mark_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    notification = get_object_or_404(Notification, id=notification_id)
                    notification.is_read = True
                    notification.save()
                    
            elif action == 'mark_all_read':
                Notification.objects.filter(
                    type__in=['appointment', 'confirmation', 'cancellation']
                ).update(is_read=True)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid method'})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
