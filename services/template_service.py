from django.conf import settings
from appointments.models import SMSTemplate
from datetime import datetime, date, time
import logging

logger = logging.getLogger(__name__)

class SMSTemplateService:
    """
    Service for managing SMS templates and rendering them with dynamic content
    """
    
    def __init__(self):
        self.clinic_info = {
            'clinic_name': getattr(settings, 'CLINIC_NAME', 'Beauty Clinic'),
            'clinic_phone': getattr(settings, 'CLINIC_PHONE', '09123456789'),
            'clinic_address': getattr(settings, 'CLINIC_ADDRESS', 'Your Clinic Address'),
        }
    
    def get_template(self, template_type, template_name=None):
        """
        Get an active SMS template by type and optionally by name
        
        Args:
            template_type (str): Type of template (confirmation, reminder, etc.)
            template_name (str): Optional specific template name
        
        Returns:
            SMSTemplate: The template object or None if not found
        """
        try:
            if template_name:
                template = SMSTemplate.objects.get(
                    template_type=template_type,
                    name=template_name,
                    is_active=True
                )
            else:
                # Get the first active template of this type
                template = SMSTemplate.objects.filter(
                    template_type=template_type,
                    is_active=True
                ).first()
            
            return template
        except SMSTemplate.DoesNotExist:
            logger.warning(f"No active template found for type: {template_type}, name: {template_name}")
            return None
    
    def render_template(self, template, context=None):
        """
        Render a template with the provided context variables
        
        Args:
            template (SMSTemplate): The template to render
            context (dict): Variables to substitute in the template
        
        Returns:
            str: Rendered message
        """
        if not template:
            return ""
        
        # Start with the template message
        message = template.message
        
        # Add clinic info to context
        full_context = {**self.clinic_info}
        if context:
            full_context.update(context)
        
        # Replace variables in the message
        try:
            message = message.format(**full_context)
        except KeyError as e:
            logger.error(f"Missing variable {e} in template {template.name}")
            # Replace missing variables with placeholder
            message = message.replace(f"{{{e}}}", f"[{e}]")
        except Exception as e:
            logger.error(f"Error rendering template {template.name}: {str(e)}")
            return template.message  # Return original if rendering fails
        
        return message.strip()
    
    def send_appointment_confirmation(self, appointment, template_name=None):
        """
        Send appointment confirmation using template
        
        Args:
            appointment: Appointment object
            template_name (str): Optional specific template name
        
        Returns:
            dict: SMS sending result
        """
        template = self.get_template('confirmation', template_name)
        if not template:
            logger.error("No confirmation template found")
            return {'success': False, 'error': 'No confirmation template found'}
        
        # Prepare context variables
        context = self._prepare_appointment_context(appointment)
        
        # Render the template
        message = self.render_template(template, context)
        
        # Send SMS
        from .sms_service import sms_service
        return sms_service.send_sms(appointment.patient.phone, message)
    
    def send_appointment_reminder(self, appointment, template_name=None):
        """
        Send appointment reminder using template
        
        Args:
            appointment: Appointment object
            template_name (str): Optional specific template name
        
        Returns:
            dict: SMS sending result
        """
        template = self.get_template('reminder', template_name)
        if not template:
            logger.error("No reminder template found")
            return {'success': False, 'error': 'No reminder template found'}
        
        # Prepare context variables
        context = self._prepare_appointment_context(appointment)
        
        # Render the template
        message = self.render_template(template, context)
        
        # Send SMS
        from .sms_service import sms_service
        return sms_service.send_sms(appointment.patient.phone, message)
    
    def send_cancellation_notification(self, appointment, reason="", template_name=None):
        """
        Send cancellation notification using template
        
        Args:
            appointment: Appointment object
            reason (str): Cancellation reason
            template_name (str): Optional specific template name
        
        Returns:
            dict: SMS sending result
        """
        template = self.get_template('cancellation', template_name)
        if not template:
            logger.error("No cancellation template found")
            return {'success': False, 'error': 'No cancellation template found'}
        
        # Prepare context variables
        context = self._prepare_appointment_context(appointment)
        context['cancellation_reason'] = reason
        
        # Render the template
        message = self.render_template(template, context)
        
        # Send SMS
        from .sms_service import sms_service
        return sms_service.send_sms(appointment.patient.phone, message)
    
    def send_attendant_reassignment(self, appointment, previous_attendant=None, template_name=None):
        """
        Send attendant reassignment notification using template
        
        Args:
            appointment: Appointment object
            previous_attendant: Previous attendant object (optional)
            template_name (str): Optional specific template name
        
        Returns:
            dict: SMS sending result
        """
        template = self.get_template('attendant_reassignment', template_name)
        if not template:
            logger.error("No attendant reassignment template found")
            return {'success': False, 'error': 'No attendant reassignment template found'}
        
        context = self._prepare_appointment_context(appointment)
        if previous_attendant:
            context['previous_attendant_name'] = f"{previous_attendant.first_name} {previous_attendant.last_name}".strip()
        else:
            context['previous_attendant_name'] = 'our previous staff'
        
        message = self.render_template(template, context)
        
        from .sms_service import sms_service
        return sms_service.send_sms(appointment.patient.phone, message)
    
    def send_package_confirmation(self, package_booking, template_name=None):
        """
        Send package confirmation using template
        
        Args:
            package_booking: Package booking object
            template_name (str): Optional specific template name
        
        Returns:
            dict: SMS sending result
        """
        template = self.get_template('package_confirmation', template_name)
        if not template:
            logger.error("No package confirmation template found")
            return {'success': False, 'error': 'No package confirmation template found'}
        
        # Prepare context variables
        context = self._prepare_package_context(package_booking)
        
        # Render the template
        message = self.render_template(template, context)
        
        # Send SMS
        from .sms_service import sms_service
        return sms_service.send_sms(package_booking.patient.phone, message)
    
    def send_custom_message(self, phone, template_name, context=None):
        """
        Send custom message using a custom template
        
        Args:
            phone (str): Recipient phone number
            template_name (str): Name of the custom template
            context (dict): Variables for the template
        
        Returns:
            dict: SMS sending result
        """
        template = self.get_template('custom', template_name)
        if not template:
            logger.error(f"No custom template found with name: {template_name}")
            return {'success': False, 'error': f'No custom template found: {template_name}'}
        
        # Render the template
        message = self.render_template(template, context or {})
        
        # Send SMS
        from .sms_service import sms_service
        return sms_service.send_sms(phone, message)
    
    def _prepare_appointment_context(self, appointment):
        """
        Prepare context variables for appointment-related templates
        
        Args:
            appointment: Appointment object
        
        Returns:
            dict: Context variables
        """
        # Format date and time safely
        if isinstance(appointment.appointment_date, date):
            date_str = appointment.appointment_date.strftime('%B %d, %Y')
        else:
            date_str = str(appointment.appointment_date)
            
        if isinstance(appointment.appointment_time, time):
            time_str = appointment.appointment_time.strftime('%I:%M %p')
        else:
            time_str = str(appointment.appointment_time)
        
        # Determine service name
        service_name = "Product Purchase"
        if appointment.service:
            service_name = appointment.service.service_name
        elif appointment.package:
            service_name = appointment.package.package_name
        
        if hasattr(appointment, 'attendant') and appointment.attendant:
            attendant_name = f"{appointment.attendant.first_name} {appointment.attendant.last_name}".strip()
        else:
            attendant_name = "our staff"
        
        return {
            'patient_name': appointment.patient.get_full_name(),
            'appointment_date': date_str,
            'appointment_time': time_str,
            'service_name': service_name,
            'attendant_name': attendant_name,
        }
    
    def _prepare_package_context(self, package_booking):
        """
        Prepare context variables for package-related templates
        
        Args:
            package_booking: Package booking object
        
        Returns:
            dict: Context variables
        """
        return {
            'patient_name': package_booking.patient.get_full_name(),
            'package_name': package_booking.package.package_name,
            'package_price': f"P{package_booking.package.price:,.2f}",
            'package_sessions': package_booking.package.sessions,
            'package_duration': f"{package_booking.package.duration_days} days",
        }
    
    def create_default_templates(self, user):
        """
        Create default SMS templates if none exist
        
        Args:
            user: User who will be marked as creator
        """
        default_templates = [
            {
                'name': 'Default Confirmation',
                'template_type': 'confirmation',
                'message': """Hi {patient_name}!

Your appointment has been confirmed:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}
Location: {clinic_name}

Please arrive 15 minutes early.
Thank you for choosing us!

- Skinovation Clinic"""
            },
            {
                'name': 'Default Reminder',
                'template_type': 'reminder',
                'message': """Hi {patient_name}!

Reminder: You have an appointment tomorrow:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}

Please arrive 15 minutes early.
See you soon!

- Skinovation Clinic"""
            },
            {
                'name': 'Default Cancellation',
                'template_type': 'cancellation',
                'message': """Hi {patient_name}!

Your appointment has been cancelled:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}

{cancellation_reason}

Please contact us to reschedule.
Thank you for your understanding.

- Skinovation Clinic"""
            },
            {
                'name': 'Default Package Confirmation',
                'template_type': 'package_confirmation',
                'message': """Hi {patient_name}!

Your package has been booked successfully:
Package: {package_name}
Price: {package_price}
Sessions: {package_sessions}
Duration: {package_duration}

Your package is now active. Book your sessions anytime!
Thank you for choosing us!

- Skinovation Clinic"""
            },
            {
                'name': 'Default Attendant Reassignment',
                'template_type': 'attendant_reassignment',
                'message': """Hi {patient_name}!

We have assigned a new staff member to assist you for your upcoming appointment:
Date: {appointment_date}
Time: {appointment_time}
Service: {service_name}
New Staff: {attendant_name}

If you have any questions, feel free to contact us at {clinic_phone}.
We look forward to seeing you!

- Skinovation Clinic"""
            }
        ]
        
        for template_data in default_templates:
            if not SMSTemplate.objects.filter(
                template_type=template_data['template_type'],
                name=template_data['name']
            ).exists():
                SMSTemplate.objects.create(
                    name=template_data['name'],
                    template_type=template_data['template_type'],
                    message=template_data['message'],
                    created_by=user
                )
                logger.info(f"Created default template: {template_data['name']}")

# Global template service instance
template_service = SMSTemplateService()
