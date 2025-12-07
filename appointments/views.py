from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, time as time_obj, date, time
from .models import Appointment, Notification, ClosedDay
from accounts.models import User, Attendant, AttendantProfile
from services.models import Service
from products.models import Product
from packages.models import Package
from services.utils import send_appointment_sms, send_attendant_assignment_sms
import json


def get_available_attendants(selected_date=None, selected_time=None):
    """
    Get all available attendants, ensuring all active attendant users have corresponding Attendant objects.
    This function syncs User objects with Attendant objects on the fly.
    Only returns attendants whose User account is active.
    """
    # Get all active attendant users and ensure they have corresponding Attendant objects
    attendant_users = User.objects.filter(user_type='attendant', is_active=True).order_by('first_name', 'last_name')
    attendant_ids = set()
    
    for user in attendant_users:
        # Get or create Attendant object for this user
        attendant, created = Attendant.objects.get_or_create(
            first_name=user.first_name,
            last_name=user.last_name,
            defaults={
                'shift_date': date.today(),
                'shift_time': time(10, 0)  # Default to 10:00 AM
            }
        )
        attendant_ids.add(attendant.id)
    
    # Only include existing Attendant objects that have corresponding active User objects
    # This ensures deactivated attendants are excluded
    all_existing_attendants = Attendant.objects.all()
    for attendant in all_existing_attendants:
        # Check if this attendant has an active user account
        try:
            user = User.objects.get(
                user_type='attendant',
                first_name=attendant.first_name,
                last_name=attendant.last_name,
                is_active=True
            )
            attendant_ids.add(attendant.id)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            # If no active user found, exclude this attendant
            pass
    
    # Get all attendants (only those with active user accounts)
    all_attendants = Attendant.objects.filter(id__in=attendant_ids).order_by('first_name', 'last_name')
    
    # If date and time are provided, filter by availability
    if selected_date and selected_time:
        try:
            appointment_datetime = datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M")
            day_name = appointment_datetime.strftime('%A')
            appointment_time_obj = datetime.strptime(selected_time, "%H:%M").time()
            
            # Filter attendants by availability
            available_attendant_ids = []
            for attendant in all_attendants:
                try:
                    user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name, is_active=True)
                    profile = getattr(user, 'attendant_profile', None)
                    if profile:
                        # Only include if work_days is not empty and the selected day is in work_days
                        if profile.work_days and day_name in profile.work_days and profile.start_time <= appointment_time_obj < profile.end_time:
                            available_attendant_ids.append(attendant.id)
                    # If no profile, exclude from available list (attendant must have profile with work days set)
                except (User.DoesNotExist, User.MultipleObjectsReturned):
                    # If no active user found, exclude this attendant
                    pass
            
            return Attendant.objects.filter(id__in=available_attendant_ids).order_by('first_name', 'last_name')
        except (ValueError, TypeError):
            # If date/time parsing fails, return only active attendants
            return all_attendants
    
    return all_attendants


@login_required
def my_appointments(request):
    """User's appointments"""
    appointments = Appointment.objects.filter(patient=request.user).order_by('-created_at', '-appointment_date', '-appointment_time')
    
    context = {
        'appointments': appointments,
    }
    
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def patient_history(request):
    """Patient view own treatment and product purchase history"""
    # Only allow patients to access this
    if request.user.user_type != 'patient':
        messages.error(request, 'This page is only available for patients.')
        return redirect('home')
    
    # Get completed appointments (treatment history)
    completed_appointments = Appointment.objects.filter(
        patient=request.user,
        status='completed'
    ).order_by('-appointment_date', '-appointment_time')
    
    # Get product purchases (appointments with products)
    product_purchases = Appointment.objects.filter(
        patient=request.user,
        product__isnull=False
    ).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'completed_appointments': completed_appointments,
        'product_purchases': product_purchases,
    }
    
    return render(request, 'appointments/patient_history.html', context)


@login_required
def book_service(request, service_id):
    """Book a service appointment"""
    service = get_object_or_404(Service, id=service_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        attendant_id = request.POST.get('attendant', '')
        
        if appointment_date and appointment_time:
            # Validate that date and time are not in the past
            from django.utils import timezone
            appointment_datetime_str = f"{appointment_date} {appointment_time}"
            try:
                appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")
                appointment_datetime_aware = timezone.make_aware(appointment_datetime)
                
                if appointment_datetime_aware <= timezone.now():
                    messages.error(request, 'Cannot book appointments in the past. Please select a future date and time.')
                    context = {
                        'service': service,
                        'attendants': get_available_attendants(),
                    }
                    return render(request, 'appointments/book_service.html', context)
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
                context = {
                    'service': service,
                    'attendants': get_available_attendants(),
                }
                return render(request, 'appointments/book_service.html', context)
            
            # Check if the selected date is a closed clinic day
            appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            if ClosedDay.objects.filter(date=appointment_date_obj).exists():
                closed_day = ClosedDay.objects.get(date=appointment_date_obj)
                reason_text = f" ({closed_day.reason})" if closed_day.reason else ""
                messages.error(request, f'The clinic is closed on {appointment_date_obj.strftime("%B %d, %Y")}{reason_text}. Please select another date.')
                context = {
                    'service': service,
                    'attendants': get_available_attendants(),
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_service.html', context)
            
            # Get the attendant - handle empty or invalid IDs
            available_attendants = get_available_attendants(selected_date=appointment_date, selected_time=appointment_time)
            if attendant_id:
                try:
                    attendant = Attendant.objects.get(id=int(attendant_id))
                    # Verify that the attendant is active
                    try:
                        attendant_user = User.objects.get(
                            user_type='attendant',
                            first_name=attendant.first_name,
                            last_name=attendant.last_name
                        )
                        if not attendant_user.is_active:
                            messages.error(request, 'This attendant account is currently inactive. Please select another attendant.')
                            context = {
                                'service': service,
                                'attendants': available_attendants,
                                'selected_date': appointment_date,
                                'selected_time': appointment_time,
                            }
                            return render(request, 'appointments/book_service.html', context)
                    except (User.DoesNotExist, User.MultipleObjectsReturned):
                        # If no user found, check if attendant is in available list
                        if attendant not in available_attendants:
                            messages.error(request, 'This attendant is not available. Please select another attendant.')
                            context = {
                                'service': service,
                                'attendants': available_attendants,
                                'selected_date': appointment_date,
                                'selected_time': appointment_time,
                            }
                            return render(request, 'appointments/book_service.html', context)
                except (Attendant.DoesNotExist, ValueError, TypeError):
                    # If attendant doesn't exist, get the first available attendant
                    if available_attendants.exists():
                        attendant = available_attendants.first()
                    else:
                        messages.error(request, 'No attendants available. Please contact the clinic.')
                        context = {
                            'service': service,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_service.html', context)
            else:
                # If no attendant selected, get the first available
                if available_attendants.exists():
                    attendant = available_attendants.first()
                else:
                    messages.error(request, 'No attendants available. Please contact the clinic.')
                    context = {
                        'service': service,
                        'attendants': available_attendants,
                        'selected_date': appointment_date,
                        'selected_time': appointment_time,
                    }
                    return render(request, 'appointments/book_service.html', context)
            
            # Check attendant availability based on work schedule
            appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            day_name = appointment_datetime.strftime('%A')
            appointment_time_obj = datetime.strptime(appointment_time, "%H:%M").time()
            
            # Policy: Patients cannot book at 6:00 PM (closed time) - last bookable time is 1 hour before closed time (5:00 PM)
            closed_time = datetime.strptime('18:00', '%H:%M').time()
            if appointment_time_obj >= closed_time:
                messages.error(request, 'Booking is not allowed at 6:00 PM. The last available booking time is 5:00 PM (1 hour before closing).')
                context = {
                    'service': service,
                    'attendants': available_attendants,
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_service.html', context)
            
            # Check if attendant has a profile and is active
            attendant_available = True
            try:
                user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name, is_active=True)
                profile = getattr(user, 'attendant_profile', None)
                
                if profile:
                    # Check if work days are set
                    if not profile.work_days or len(profile.work_days) == 0:
                        messages.error(request, f'{attendant.first_name} {attendant.last_name} has no work days configured. Please contact the clinic or select another attendant.')
                        context = {
                            'service': service,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_service.html', context)
                    
                    # Check if it's a work day
                    if day_name not in profile.work_days:
                        messages.error(request, f'{attendant.first_name} {attendant.last_name} is not available on {day_name}. Please choose another day or attendant.')
                        context = {
                            'service': service,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_service.html', context)
                    
                    # Check if time is within work hours
                    if appointment_time_obj < profile.start_time or appointment_time_obj >= profile.end_time:
                        messages.error(request, f'Appointment time must be between {profile.start_time.strftime("%I:%M %p")} and {profile.end_time.strftime("%I:%M %p")} for {attendant.first_name} {attendant.last_name}.')
                        context = {
                            'service': service,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_service.html', context)
                    attendant_available = True
                else:
                    # If no profile exists, reject the booking
                    messages.error(request, f'{attendant.first_name} {attendant.last_name} has no work schedule configured. Please contact the clinic or select another attendant.')
                    context = {
                        'service': service,
                        'attendants': available_attendants,
                        'selected_date': appointment_date,
                        'selected_time': appointment_time,
                    }
                    return render(request, 'appointments/book_service.html', context)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                # If no user found, reject the booking
                messages.error(request, 'Attendant account not found. Please select another attendant.')
                context = {
                    'service': service,
                    'attendants': available_attendants,
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_service.html', context)
            
            # Check for existing appointments at the same time slot
            existing_appointments = Appointment.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                attendant_id=attendant.id,
                status__in=['pending', 'confirmed']
            ).count()
            
            # Maximum 3 patients per time slot
            if existing_appointments >= 3:
                messages.error(request, 'This time slot is fully booked. Please choose another time.')
                context = {
                    'service': service,
                    'attendants': available_attendants,
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_service.html', context)
            
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # All appointments start as pending and require staff approval
            initial_status = 'pending'
            
            appointment = Appointment.objects.create(
                patient=request.user,
                service=service,
                attendant=attendant,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=initial_status,
                transaction_id=transaction_id
            )
            
            # Log appointment booking
            from .models import HistoryLog
            HistoryLog.objects.create(
                action_type='book',
                item_type='appointment',
                item_id=appointment.id,
                item_name=f"{service.service_name} - {request.user.get_full_name()}",
                performed_by=request.user,
                details={
                    'appointment_id': appointment.id,
                    'patient': request.user.get_full_name(),
                    'service': service.service_name,
                    'attendant': f"{attendant.first_name} {attendant.last_name}",
                    'date': str(appointment_date),
                    'time': str(appointment_time),
                    'status': initial_status,
                    'transaction_id': transaction_id,
                }
            )
            
            # Create notification
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Appointment Booked',
                message=f'Your {service.service_name} appointment has been booked for {appointment_date} at {appointment_time}. Waiting for staff approval. Transaction ID: {transaction_id}',
                patient=request.user
            )
            
            # Notify owner of new appointment booking (single notification for all owners)
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='New Appointment Booked',
                message=f'New appointment booked: {appointment.patient.get_full_name()} - {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time}. Status: {appointment.status}.',
                patient=None  # Owner notification
            )
            
            # Send SMS confirmation to patient
            sms_result = send_appointment_sms(appointment, 'confirmation')
            if sms_result['success']:
                messages.success(request, f'Appointment booked! Waiting for staff approval. SMS confirmation sent. Transaction ID: {transaction_id}')
            else:
                messages.success(request, f'Appointment booked! Waiting for staff approval. (SMS notification failed) Transaction ID: {transaction_id}')
            
            # Send SMS and create in-app notification for attendant
            try:
                attendant_user = User.objects.filter(
                    user_type='attendant',
                    first_name=attendant.first_name,
                    last_name=attendant.last_name,
                    is_active=True
                ).first()
                
                if attendant_user:
                    # Send SMS to attendant
                    send_attendant_assignment_sms(appointment)
                    
                    # Create in-app notification for attendant
                    Notification.objects.create(
                        type='appointment',
                        appointment_id=appointment.id,
                        title='New Appointment Assigned',
                        message=f'You have been assigned a new appointment: {appointment.patient.get_full_name()} - {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time}.',
                        patient=attendant_user  # Store attendant user in patient field for notification
                    )
            except Exception as e:
                # Log error but don't fail the booking
                pass
            
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get available attendants based on selected date/time (if provided)
    selected_date = request.GET.get('date', '')
    selected_time = request.GET.get('time', '')
    available_attendants = get_available_attendants(selected_date, selected_time)
    
    # Get closed days for calendar display
    closed_days = ClosedDay.objects.all().values_list('date', flat=True)
    closed_days_list = [str(date) for date in closed_days]
    closed_days_json = json.dumps(closed_days_list)
    
    context = {
        'service': service,
        'attendants': available_attendants,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'closed_days': closed_days_json,
    }
    
    return render(request, 'appointments/book_service.html', context)


@login_required
def book_product(request, product_id):
    """Book a product pre-order"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        
        if appointment_date and appointment_time:
            # Validate that date and time are not in the past
            from django.utils import timezone
            appointment_datetime_str = f"{appointment_date} {appointment_time}"
            try:
                appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")
                appointment_datetime_aware = timezone.make_aware(appointment_datetime)
                
                if appointment_datetime_aware <= timezone.now():
                    messages.error(request, 'Cannot book appointments in the past. Please select a future date and time.')
                    context = {
                        'product': product,
                    }
                    return render(request, 'appointments/book_product.html', context)
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
                context = {
                    'product': product,
                }
                return render(request, 'appointments/book_product.html', context)
            
            # Check if the selected date is a closed clinic day
            appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            if ClosedDay.objects.filter(date=appointment_date_obj).exists():
                closed_day = ClosedDay.objects.get(date=appointment_date_obj)
                reason_text = f" ({closed_day.reason})" if closed_day.reason else ""
                messages.error(request, f'The clinic is closed on {appointment_date_obj.strftime("%B %d, %Y")}{reason_text}. Please select another date.')
                context = {
                    'product': product,
                }
                return render(request, 'appointments/book_product.html', context)
            
            # Check stock availability
            if product.stock <= 0:
                messages.error(request, f'Sorry, {product.product_name} is currently out of stock. Please check back later or contact the clinic.')
                context = {
                    'product': product,
                }
                return render(request, 'appointments/book_product.html', context)
            
            # Policy: Patients cannot book at 6:00 PM (closed time) - last bookable time is 1 hour before closed time (5:00 PM)
            appointment_time_obj = datetime.strptime(appointment_time, "%H:%M").time()
            closed_time = datetime.strptime('18:00', '%H:%M').time()
            if appointment_time_obj >= closed_time:
                messages.error(request, 'Booking is not allowed at 6:00 PM. The last available booking time is 5:00 PM (1 hour before closing).')
                context = {
                    'product': product,
                }
                return render(request, 'appointments/book_product.html', context)
            
            # Get the default attendant for product pre-orders
            attendant = get_object_or_404(Attendant, id=1)
            
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # All appointments start as pending and require staff approval
            initial_status = 'pending'
            
            appointment = Appointment.objects.create(
                patient=request.user,
                product=product,
                attendant=attendant,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=initial_status,
                transaction_id=transaction_id
            )
            
            # Log product pre-order booking
            from .models import HistoryLog
            HistoryLog.objects.create(
                action_type='book',
                item_type='appointment',
                item_id=appointment.id,
                item_name=f"{product.product_name} - {request.user.get_full_name()}",
                performed_by=request.user,
                details={
                    'appointment_id': appointment.id,
                    'patient': request.user.get_full_name(),
                    'product': product.product_name,
                    'attendant': f"{attendant.first_name} {attendant.last_name}",
                    'date': str(appointment_date),
                    'time': str(appointment_time),
                    'status': initial_status,
                    'transaction_id': transaction_id,
                }
            )
            
            # Deduct stock only when staff confirms the pre-order
            # Stock will be deducted when appointment status changes to 'confirmed'
            
            # Create notification
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Product Pre-Ordered',
                message=f'Your {product.product_name} has been pre-ordered for pickup on {appointment_date} at {appointment_time}. Waiting for staff approval. Transaction ID: {transaction_id}',
                patient=request.user
            )
            
            # Notify owner of product pre-order (single notification for all owners)
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Product Pre-Order',
                message=f'Product pre-order: {request.user.get_full_name()} - {product.product_name} on {appointment_date} at {appointment_time}. Status: {initial_status}.',
                patient=None  # Owner notification
            )
            
            # Send SMS confirmation
            sms_result = send_appointment_sms(appointment, 'confirmation')
            if sms_result['success']:
                messages.success(request, f'Product pre-ordered successfully! Waiting for staff approval. SMS confirmation sent. Transaction ID: {transaction_id}')
            else:
                messages.success(request, f'Product pre-ordered successfully! Waiting for staff approval. (SMS notification failed) Transaction ID: {transaction_id}')
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get closed days for calendar display
    closed_days = ClosedDay.objects.all().values_list('date', flat=True)
    closed_days_list = [str(date) for date in closed_days]
    closed_days_json = json.dumps(closed_days_list)
    
    context = {
        'product': product,
        'closed_days': closed_days_json,
    }
    
    return render(request, 'appointments/book_product.html', context)


@login_required
def book_package(request, package_id):
    """Book a package"""
    package = get_object_or_404(Package, id=package_id)
    
    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        appointment_time = request.POST.get('appointment_time')
        attendant_id = request.POST.get('attendant', '')
        
        if appointment_date and appointment_time:
            # Validate that date and time are not in the past
            from django.utils import timezone
            appointment_datetime_str = f"{appointment_date} {appointment_time}"
            try:
                appointment_datetime = datetime.strptime(appointment_datetime_str, "%Y-%m-%d %H:%M")
                appointment_datetime_aware = timezone.make_aware(appointment_datetime)
                
                if appointment_datetime_aware <= timezone.now():
                    messages.error(request, 'Cannot book appointments in the past. Please select a future date and time.')
                    context = {
                        'package': package,
                        'attendants': get_available_attendants(),
                    }
                    return render(request, 'appointments/book_package.html', context)
            except ValueError:
                messages.error(request, 'Invalid date or time format.')
                context = {
                    'package': package,
                    'attendants': get_available_attendants(),
                }
                return render(request, 'appointments/book_package.html', context)
            
            # Check if the selected date is a closed clinic day
            appointment_date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
            if ClosedDay.objects.filter(date=appointment_date_obj).exists():
                closed_day = ClosedDay.objects.get(date=appointment_date_obj)
                reason_text = f" ({closed_day.reason})" if closed_day.reason else ""
                messages.error(request, f'The clinic is closed on {appointment_date_obj.strftime("%B %d, %Y")}{reason_text}. Please select another date.')
                context = {
                    'package': package,
                    'attendants': get_available_attendants(),
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_package.html', context)
            
            # Get the attendant - handle empty or invalid IDs
            available_attendants = get_available_attendants(selected_date=appointment_date, selected_time=appointment_time)
            if attendant_id:
                try:
                    attendant = Attendant.objects.get(id=int(attendant_id))
                    # Verify that the attendant is active
                    try:
                        attendant_user = User.objects.get(
                            user_type='attendant',
                            first_name=attendant.first_name,
                            last_name=attendant.last_name
                        )
                        if not attendant_user.is_active:
                            messages.error(request, 'This attendant account is currently inactive. Please select another attendant.')
                            context = {
                                'package': package,
                                'attendants': available_attendants,
                                'selected_date': appointment_date,
                                'selected_time': appointment_time,
                            }
                            return render(request, 'appointments/book_package.html', context)
                    except (User.DoesNotExist, User.MultipleObjectsReturned):
                        # If no user found, check if attendant is in available list
                        if attendant not in available_attendants:
                            messages.error(request, 'This attendant is not available. Please select another attendant.')
                            context = {
                                'package': package,
                                'attendants': available_attendants,
                                'selected_date': appointment_date,
                                'selected_time': appointment_time,
                            }
                            return render(request, 'appointments/book_package.html', context)
                except (Attendant.DoesNotExist, ValueError, TypeError):
                    # If attendant doesn't exist, get the first available attendant
                    if available_attendants.exists():
                        attendant = available_attendants.first()
                    else:
                        messages.error(request, 'No attendants available. Please contact the clinic.')
                        context = {
                            'package': package,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_package.html', context)
            else:
                # If no attendant selected, get the first available
                if available_attendants.exists():
                    attendant = available_attendants.first()
                else:
                    messages.error(request, 'No attendants available. Please contact the clinic.')
                    context = {
                        'package': package,
                        'attendants': available_attendants,
                        'selected_date': appointment_date,
                        'selected_time': appointment_time,
                    }
                    return render(request, 'appointments/book_package.html', context)
            
            # Check attendant availability based on work schedule
            appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            day_name = appointment_datetime.strftime('%A')
            appointment_time_obj = datetime.strptime(appointment_time, "%H:%M").time()
            
            # Policy: Patients cannot book at 6:00 PM (closed time) - last bookable time is 1 hour before closed time (5:00 PM)
            closed_time = datetime.strptime('18:00', '%H:%M').time()
            if appointment_time_obj >= closed_time:
                messages.error(request, 'Booking is not allowed at 6:00 PM. The last available booking time is 5:00 PM (1 hour before closing).')
                context = {
                    'package': package,
                    'attendants': available_attendants,
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_package.html', context)
            
            # Check if attendant has a profile and is active
            try:
                user = User.objects.get(user_type='attendant', first_name=attendant.first_name, last_name=attendant.last_name, is_active=True)
                profile = getattr(user, 'attendant_profile', None)
                
                if profile:
                    # Check if work days are set
                    if not profile.work_days or len(profile.work_days) == 0:
                        messages.error(request, f'{attendant.first_name} {attendant.last_name} has no work days configured. Please contact the clinic or select another attendant.')
                        context = {
                            'package': package,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_package.html', context)
                    
                    # Check if it's a work day
                    if day_name not in profile.work_days:
                        messages.error(request, f'{attendant.first_name} {attendant.last_name} is not available on {day_name}. Please choose another day or attendant.')
                        context = {
                            'package': package,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_package.html', context)
                    
                    # Check if time is within work hours
                    if appointment_time_obj < profile.start_time or appointment_time_obj >= profile.end_time:
                        messages.error(request, f'Appointment time must be between {profile.start_time.strftime("%I:%M %p")} and {profile.end_time.strftime("%I:%M %p")} for {attendant.first_name} {attendant.last_name}.')
                        context = {
                            'package': package,
                            'attendants': available_attendants,
                            'selected_date': appointment_date,
                            'selected_time': appointment_time,
                        }
                        return render(request, 'appointments/book_package.html', context)
                else:
                    # If no profile exists, reject the booking
                    messages.error(request, f'{attendant.first_name} {attendant.last_name} has no work schedule configured. Please contact the clinic or select another attendant.')
                    context = {
                        'package': package,
                        'attendants': available_attendants,
                        'selected_date': appointment_date,
                        'selected_time': appointment_time,
                    }
                    return render(request, 'appointments/book_package.html', context)
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                # If no user found, reject the booking
                messages.error(request, 'Attendant account not found. Please select another attendant.')
                context = {
                    'package': package,
                    'attendants': available_attendants,
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_package.html', context)
            
            # Check for existing appointments at the same time slot
            existing_appointments = Appointment.objects.filter(
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                attendant_id=attendant.id,
                status__in=['pending', 'confirmed']
            ).count()
            
            # Maximum 3 patients per time slot
            if existing_appointments >= 3:
                messages.error(request, 'This time slot is fully booked. Please choose another time.')
                context = {
                    'package': package,
                    'attendants': available_attendants,
                    'selected_date': appointment_date,
                    'selected_time': appointment_time,
                }
                return render(request, 'appointments/book_package.html', context)
            
            # Generate transaction ID
            import uuid
            transaction_id = str(uuid.uuid4())[:8].upper()
            
            # All appointments start as pending and require staff approval
            initial_status = 'pending'
            
            appointment = Appointment.objects.create(
                patient=request.user,
                package=package,
                attendant=attendant,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status=initial_status,
                transaction_id=transaction_id
            )
            
            # Log package booking
            from .models import HistoryLog
            HistoryLog.objects.create(
                action_type='book',
                item_type='appointment',
                item_id=appointment.id,
                item_name=f"{package.package_name} - {request.user.get_full_name()}",
                performed_by=request.user,
                details={
                    'appointment_id': appointment.id,
                    'patient': request.user.get_full_name(),
                    'package': package.package_name,
                    'attendant': f"{attendant.first_name} {attendant.last_name}",
                    'date': str(appointment_date),
                    'time': str(appointment_time),
                    'status': initial_status,
                    'transaction_id': transaction_id,
                }
            )
            
            # Create notification
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Package Booked',
                message=f'Your {package.package_name} package has been booked for {appointment_date} at {appointment_time}. Waiting for staff approval. Transaction ID: {transaction_id}',
                patient=request.user
            )
            
            # Notify owner of package booking (single notification for all owners)
            Notification.objects.create(
                type='appointment',
                appointment_id=appointment.id,
                title='Package Booked',
                message=f'Package booking: {request.user.get_full_name()} - {package.package_name} on {appointment_date} at {appointment_time}. Status: {initial_status}.',
                patient=None  # Owner notification
            )
            
            messages.success(request, f'Package booked! Waiting for staff approval. Transaction ID: {transaction_id}')
            return redirect('appointments:my_appointments')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    # Get available attendants based on selected date/time (if provided)
    selected_date = request.GET.get('date', '')
    selected_time = request.GET.get('time', '')
    available_attendants = get_available_attendants(selected_date, selected_time)
    
    # Get closed days for calendar display
    closed_days = ClosedDay.objects.all().values_list('date', flat=True)
    closed_days_list = [str(date) for date in closed_days]
    closed_days_json = json.dumps(closed_days_list)
    
    context = {
        'package': package,
        'attendants': available_attendants,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'closed_days': closed_days_json,
    }
    
    return render(request, 'appointments/book_package.html', context)


@login_required
def notifications(request):
    """User's notifications"""
    notifications = Notification.objects.filter(patient=request.user).order_by('-created_at')
    
    # Mark notifications as read
    notifications.update(is_read=True)
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'appointments/notifications.html', context)


@login_required
def request_cancellation(request, appointment_id):
    """Request cancellation for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    # Check if appointment can be cancelled (must be at least 2 days before)
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.appointment_date, appointment.appointment_time)
    )
    days_until_appointment = (appointment_datetime - timezone.now()).days
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Require cancellation reason
        if not reason:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'Cancellation reason is required. Please provide a reason for cancelling.'}, status=400)
            messages.error(request, 'Cancellation reason is required. Please provide a reason for cancelling.')
            return redirect('appointments:my_appointments')
        
        # Check if appointment can be cancelled
        if appointment.status not in ['pending', 'confirmed']:
            if is_ajax:
                return JsonResponse({'success': False, 'message': 'This appointment cannot be cancelled.'}, status=400)
            messages.error(request, 'This appointment cannot be cancelled.')
            return redirect('appointments:my_appointments')
        
        # Create cancellation request (for both within 2 days and more than 2 days)
        from .models import CancellationRequest
        
        # Determine appointment type
        appointment_type = 'regular'
        if appointment.package:
            appointment_type = 'package'
        
        # Check if cancellation request already exists
        cancellation_request = CancellationRequest.objects.filter(
            appointment_id=appointment.id,
            status='pending'
        ).first()
        
        if not cancellation_request:
            cancellation_request = CancellationRequest.objects.create(
                appointment_id=appointment.id,
                appointment_type=appointment_type,
                patient=request.user,
                reason=reason,
                status='pending'
            )
        
        # Notify owner of cancellation request (single notification for all owners)
        if days_until_appointment < 2:
            Notification.objects.create(
                type='cancellation',
                appointment_id=appointment.id,
                title='Cancellation Request (Within 2 Days)',
                message=f'Patient {request.user.full_name} has requested to cancel their appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time} within 2 days. Reason: {reason}. Please review.',
                patient=None  # Owner notification
            )
        else:
            Notification.objects.create(
                type='cancellation',
                appointment_id=appointment.id,
                title='Cancellation Request',
                message=f'Patient {request.user.full_name} has requested to cancel their appointment for {appointment.get_service_name()} on {appointment.appointment_date} at {appointment.appointment_time}. Reason: {reason}',
                patient=None  # Owner notification
            )
        
        if is_ajax:
            return JsonResponse({
                'success': True, 
                'message': 'Your cancellation request has been submitted. The owner will review it shortly.'
            })
        messages.success(request, 'Your cancellation request has been submitted. The owner will review it shortly.')
        return redirect('appointments:my_appointments')
    
    # GET request - check if within 2 days
    if days_until_appointment < 2:
        messages.error(request, 'Cancellation is not allowed within 2 days of the appointment. The owner will be notified if you submit a request.')
        return redirect('appointments:my_appointments')
    
    # GET request - show cancellation form
    context = {
        'appointment': appointment,
        'days_until_appointment': days_until_appointment,
    }
    
    return render(request, 'appointments/request_cancellation.html', context)


@login_required
def handle_unavailable_attendant(request, appointment_id):
    """Patient handles unavailable attendant - choose from 3 options"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    # Check if there's a pending unavailability request
    from .models import AttendantUnavailabilityRequest
    try:
        unavailability_request = AttendantUnavailabilityRequest.objects.get(
            appointment=appointment,
            status='pending'
        )
    except AttendantUnavailabilityRequest.DoesNotExist:
        messages.error(request, 'No unavailability request found for this appointment.')
        return redirect('appointments:my_appointments')
    
    if request.method == 'POST':
        choice = request.POST.get('choice')
        
        # Record patient's choice
        unavailability_request.patient_choice = choice
        unavailability_request.status = 'resolved'
        unavailability_request.resolved_at = timezone.now()
        unavailability_request.save()
        
        # Create notification for owner
        Notification.objects.create(
            type='system',
            title='Patient Responded to Unavailability',
            message=f'Patient {appointment.patient.get_full_name()} chose: {dict(unavailability_request._meta.get_field("patient_choice").choices).get(choice, choice)} for appointment on {appointment.appointment_date}.'
        )
        
        if choice == 'choose_another':
            # Redirect to appointment booking with service/package/product to choose another attendant
            messages.info(request, 'Please select another available attendant for the same date and time.')
            if appointment.service:
                return redirect('appointments:book_service', service_id=appointment.service.id)
            elif appointment.package:
                return redirect('appointments:book_package', package_id=appointment.package.id)
            elif appointment.product:
                return redirect('appointments:book_product', product_id=appointment.product.id)
            else:
                messages.error(request, 'Unable to determine appointment type.')
                return redirect('appointments:my_appointments')
        
        elif choice == 'reschedule_same':
            # Redirect to reschedule request
            messages.info(request, 'Please select a new date and time with the same attendant.')
            return redirect('appointments:request_reschedule', appointment_id=appointment_id)
        
        elif choice == 'cancel':
            # Redirect to cancellation request
            messages.info(request, 'Please confirm cancellation of your appointment.')
            return redirect('appointments:request_cancellation', appointment_id=appointment_id)
        
        else:
            messages.error(request, 'Invalid choice. Please select one of the options.')
    
    context = {
        'appointment': appointment,
        'unavailability_request': unavailability_request,
    }
    
    return render(request, 'appointments/unavailable_attendant.html', context)


@login_required
def request_reschedule(request, appointment_id):
    """Request reschedule for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if request.method == 'POST':
        new_date = request.POST.get('new_appointment_date')
        new_time = request.POST.get('new_appointment_time')
        reason = request.POST.get('reason', '')
        
        if not new_date or not new_time:
            messages.error(request, 'Please provide both new date and time.')
            return redirect('appointments:request_reschedule', appointment_id=appointment_id)
        
        # Check if appointment can be rescheduled
        if appointment.status not in ['pending', 'confirmed']:
            messages.error(request, 'This appointment cannot be rescheduled.')
            return redirect('appointments:my_appointments')
        
        # Policy: Patients cannot reschedule when the appointment is within the same day
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        appointment_datetime = timezone.make_aware(
            datetime.combine(appointment.appointment_date, appointment.appointment_time)
        )
        current_datetime = timezone.now()
        days_until_appointment = (appointment_datetime.date() - current_datetime.date()).days
        
        if days_until_appointment < 1:
            messages.error(request, 'Rescheduling is not allowed when the appointment is within the same day. Please contact the clinic directly.')
            return redirect('appointments:my_appointments')
        
        # Validate that the new date/time is not in the past
        try:
            new_datetime = timezone.make_aware(
                datetime.combine(
                    datetime.strptime(new_date, '%Y-%m-%d').date(),
                    datetime.strptime(new_time, '%H:%M').time()
                )
            )
            
            if new_datetime <= current_datetime:
                messages.error(request, 'You cannot reschedule to a date and time in the past. Please select a future date and time.')
                return redirect('appointments:request_reschedule', appointment_id=appointment_id)
        except (ValueError, TypeError) as e:
            messages.error(request, 'Invalid date or time format. Please try again.')
            return redirect('appointments:request_reschedule', appointment_id=appointment_id)
        
        # Check if the new date is a closed clinic day
        new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
        if ClosedDay.objects.filter(date=new_date_obj).exists():
            closed_day = ClosedDay.objects.get(date=new_date_obj)
            reason_text = f" ({closed_day.reason})" if closed_day.reason else ""
            messages.error(request, f'The clinic is closed on {new_date_obj.strftime("%B %d, %Y")}{reason_text}. Please select another date.')
            return redirect('appointments:request_reschedule', appointment_id=appointment_id)
        
        # Create reschedule request
        from .models import RescheduleRequest
        
        reschedule_request = RescheduleRequest.objects.create(
            appointment_id=appointment.id,
            new_appointment_date=new_date,
            new_appointment_time=new_time,
            patient=request.user,
            reason=reason,
            status='pending'
        )
        
        # Create notification for staff
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Reschedule Request',
            message=f'Patient {request.user.full_name} has requested to reschedule their appointment for {appointment.get_service_name()} from {appointment.appointment_date} at {appointment.appointment_time} to {new_date} at {new_time}. Reason: {reason}',
            patient=None  # Staff notification
        )
        
        # Notify owner of reschedule request (single notification for all owners)
        Notification.objects.create(
            type='reschedule',
            appointment_id=appointment.id,
            title='Reschedule Request',
            message=f'Patient {request.user.full_name} has requested to reschedule their appointment for {appointment.get_service_name()} from {appointment.appointment_date} at {appointment.appointment_time} to {new_date} at {new_time}.',
            patient=None  # Owner notification
        )
        
        messages.success(request, 'Your reschedule request has been submitted. The staff will review it shortly.')
        return redirect('appointments:my_appointments')
    
    # GET request - check if rescheduling is allowed
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    appointment_datetime = timezone.make_aware(
        datetime.combine(appointment.appointment_date, appointment.appointment_time)
    )
    current_datetime = timezone.now()
    days_until_appointment = (appointment_datetime.date() - current_datetime.date()).days
    
    # Policy: Patients cannot reschedule when the appointment is within the same day
    if days_until_appointment < 1:
        messages.error(request, 'Rescheduling is not allowed when the appointment is within the same day. Please contact the clinic directly.')
        return redirect('appointments:my_appointments')
    
    # GET request - show reschedule form
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/request_reschedule.html', context)


@login_required
def submit_feedback(request, appointment_id):
    """Submit feedback for a completed appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    
    if appointment.status != 'completed':
        messages.error(request, 'Feedback can only be submitted for completed appointments.')
        return redirect('appointments:my_appointments')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        attendant_rating = request.POST.get('attendant_rating')
        comment = request.POST.get('comment', '')
        
        if not rating:
            messages.error(request, 'Please provide a rating for the appointment.')
            return redirect('appointments:my_appointments')
        
        rating = int(rating)
        if rating < 1 or rating > 5:
            messages.error(request, 'Appointment rating must be between 1 and 5.')
            return redirect('appointments:my_appointments')
        
        # Validate attendant rating if provided
        attendant_rating_int = None
        if attendant_rating:
            attendant_rating_int = int(attendant_rating)
            if attendant_rating_int < 1 or attendant_rating_int > 5:
                messages.error(request, 'Attendant rating must be between 1 and 5.')
                return redirect('appointments:my_appointments')
        
        # Check if feedback already exists
        from .models import Feedback
        if Feedback.objects.filter(appointment=appointment, patient=request.user).exists():
            messages.error(request, 'You have already submitted feedback for this appointment.')
            return redirect('appointments:my_appointments')
        
        # Create feedback
        Feedback.objects.create(
            appointment=appointment,
            patient=request.user,
            rating=rating,
            attendant_rating=attendant_rating_int,
            comment=comment
        )
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('appointments:my_appointments')
    
    return redirect('appointments:my_appointments')


@csrf_exempt
@require_http_methods(["GET"])
def get_notifications_api(request):
    """API endpoint to get notifications (replaces get_notifications.php)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        from django.db.models import Q
        
        if request.user.user_type == 'admin':
            # For admin/staff, show all system notifications (where patient is null)
            notifications = Notification.objects.filter(patient__isnull=True, is_read=False).order_by('-created_at')[:10]
        elif request.user.user_type == 'owner':
            # For owner, show all system notifications (where patient is null)
            notifications = Notification.objects.filter(patient__isnull=True, is_read=False).order_by('-created_at')[:10]
        elif request.user.user_type == 'attendant':
            # For attendant, show notifications assigned to them or system notifications
            notifications = Notification.objects.filter(
                (Q(patient=request.user) | Q(patient__isnull=True)),
                is_read=False
            ).order_by('-created_at')[:10]
        else:
            # For patients, show their notifications
            notifications = Notification.objects.filter(patient=request.user, is_read=False).order_by('-created_at')[:10]
        
        # Count unread notifications
        unread_count = notifications.count()
        
        # Format notifications
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'notification_id': notification.id,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at_formatted': notification.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def update_notifications_api(request):
    """API endpoint to update notifications (replaces update_notifications.php)"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            action = data.get('action')
            notification_id = data.get('notification_id')
        else:
            action = request.POST.get('action')
            notification_id = request.POST.get('notification_id')
        
        if action == 'mark_read':
            if notification_id:
                notification = get_object_or_404(Notification, id=notification_id)
                # Allow admin, owner, or the notification's patient to mark as read
                if request.user.user_type in ('admin', 'owner'):
                    # For admin/owner, only allow marking system notifications (patient is None)
                    if notification.patient is None:
                        notification.is_read = True
                        notification.save()
                        return JsonResponse({'success': True})
                elif notification.patient == request.user:
                    notification.is_read = True
                    notification.save()
                    return JsonResponse({'success': True})
        
        elif action == 'mark_all_read':
            if request.user.user_type in ('admin', 'owner'):
                Notification.objects.filter(patient__isnull=True).update(is_read=True)
            else:
                Notification.objects.filter(patient=request.user).update(is_read=True)
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Invalid action'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})