from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.core.exceptions import ValidationError
from .models import User
import re


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form for our custom User model"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'First Name',
            'style': 'text-transform: capitalize;',
            'pattern': '[A-Za-z\\s]+',
            'title': 'Only letters and spaces allowed'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Last Name',
            'style': 'text-transform: capitalize;',
            'pattern': '[A-Za-z\\s]+',
            'title': 'Only letters and spaces allowed'
        })
    )
    middle_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Middle Name (Optional)',
            'pattern': '[A-Za-z\\s]+',
            'title': 'Only letters and spaces allowed'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '09123456789',
            'maxlength': '11',
            'pattern': '09[0-9]{9}',
            'title': 'Enter 11-digit Philippine phone number starting with 09'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'middle_name', 'email', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Username',
                'style': 'text-transform: capitalize;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_first_name(self):
        """Validate first name - letters only"""
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Check if contains only letters and spaces
            if not all(c.isalpha() or c.isspace() for c in first_name):
                raise ValidationError('First name can only contain letters and spaces.')
        return first_name
    
    def clean_last_name(self):
        """Validate last name - letters only"""
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Check if contains only letters and spaces
            if not all(c.isalpha() or c.isspace() for c in last_name):
                raise ValidationError('Last name can only contain letters and spaces.')
        return last_name
    
    def clean_middle_name(self):
        """Validate middle name - letters only if provided"""
        middle_name = self.cleaned_data.get('middle_name')
        if middle_name:
            # Check if contains only letters and spaces
            if not all(c.isalpha() or c.isspace() for c in middle_name):
                raise ValidationError('Middle name can only contain letters and spaces.')
        return middle_name
    
    def clean_phone(self):
        """Validate Philippine phone number format"""
        phone = self.cleaned_data.get('phone')
        
        if not phone:
            raise ValidationError('Phone number is required.')
        
        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', phone)
        
        # Check if it's exactly 11 digits and starts with 09
        if len(phone_digits) != 11 or not phone_digits.startswith('09'):
            raise ValidationError(
                'Please enter a valid 11-digit Philippine phone number starting with 09 (e.g., 09123456789)'
            )
        
        return phone_digits  # Return cleaned phone number
    
    def clean_email(self):
        """Validate email - check for duplicates and optionally verify it's a Google account"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        # Check if email already exists in the system
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered. Please use a different email or try logging in.')
        
        # Optional: Check if it's a Gmail account (for Google Sign-In compatibility)
        # Note: Real validation would require actually sending an email or using Google's API
        # For now, we'll just ensure it's a valid email format
        # If you want to enforce Gmail only, uncomment the lines below:
        # if not email.lower().endswith('@gmail.com'):
        #     raise ValidationError('Please use a valid Gmail address for registration.')
        
        return email.lower()  # Return lowercase email for consistency
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.middle_name = self.cleaned_data['middle_name']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.user_type = 'patient'  # Default to patient
        
        if commit:
            user.save()
        return user


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form with enhanced styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email'
        })


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form with enhanced styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password'
        })


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password',
            'id': 'id_current_password'
        }),
        help_text='Enter your current password to view it or change it'
    )
    
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password (optional)',
            'id': 'id_new_password'
        }),
        help_text='Leave blank if you don\'t want to change your password'
    )
    
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'id': 'id_confirm_password'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'middle_name', 'email', 'phone', 'address', 
                  'gender', 'civil_status', 'birthday', 'occupation', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 
                'maxlength': '11',
                'pattern': '09[0-9]{9}',
                'inputmode': 'numeric',
                'oninput': 'this.value = this.value.replace(/[^0-9]/g, "").slice(0, 11); if (this.value.length > 0 && !this.value.startsWith("09")) { this.value = "09" + this.value.replace(/^09/, ""); }'
            }),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'civil_status': forms.Select(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make password fields optional
        self.fields['current_password'].required = False
        self.fields['new_password'].required = False
        self.fields['confirm_password'].required = False
    
    def clean_phone(self):
        """Validate Philippine phone number format"""
        phone = self.cleaned_data.get('phone')
        
        if phone:
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) != 11 or not phone_digits.startswith('09'):
                raise ValidationError(
                    'Please enter a valid 11-digit Philippine phone number starting with 09 (e.g., 09123456789)'
                )
            return phone_digits
        
        return phone
    
    def clean_email(self):
        """Validate email - check for duplicates (excluding current user)"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        # Check if email already exists for another user
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError('This email address is already being used by another account. Please use a different email.')
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # If any password field is filled, validate password change
        if current_password or new_password or confirm_password:
            if not current_password:
                raise ValidationError({
                    'current_password': 'Please enter your current password to change it.'
                })
            
            # Verify current password
            if not self.instance.check_password(current_password):
                raise ValidationError({
                    'current_password': 'Current password is incorrect.'
                })
            
            # If new password is provided, validate it
            if new_password:
                if len(new_password) < 8:
                    raise ValidationError({
                        'new_password': 'Password must be at least 8 characters long.'
                    })
                
                if new_password != confirm_password:
                    raise ValidationError({
                        'confirm_password': 'New passwords do not match.'
                    })
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        
        # If a new password is provided, set it
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        return user
