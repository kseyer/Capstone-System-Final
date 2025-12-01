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
        """Validate email - STRICT verification to ensure REAL Gmail accounts only"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        # Check if email already exists in the system
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address is already registered. Please use a different email or try logging in.')
        
        # MUST be a Gmail account - required for Google Sign-In
        if not email.lower().endswith('@gmail.com'):
            raise ValidationError(
                'Only Gmail addresses (@gmail.com) are accepted. '
                'This is required for Google Sign-In verification. '
                'Please use your real, active Gmail account.'
            )
        
        # Get the email username part (before @gmail.com)
        email_parts = email.lower().split('@')[0]
        
        # STRICT: Minimum length - real emails are rarely shorter than 5 characters
        if len(email_parts) < 5:
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account '
                '(the one you actually use and can sign in with Google). '
                'Test emails and fake accounts are NOT allowed.'
            )
        
        # Remove common separators for analysis
        email_name = email_parts.replace('.', '').replace('_', '').replace('-', '')
        
        # Check for suspicious patterns that indicate fake emails
        import string
        import re
        
        # STRICT CHECK: Block common test/fake email patterns
        blocked_patterns = [
            'test', 'fake', 'dummy', 'sample', 'example', 'temp', 'throwaway',
            'asdf', 'qwer', 'zxcv', 'abcd', 'user', 'email', 'mail'
        ]
        
        email_lower = email_parts.lower()
        for pattern in blocked_patterns:
            if pattern in email_lower:
                raise ValidationError(
                    f'Test and fake email addresses are NOT allowed. '
                    f'Please use your REAL, active Gmail account that you use regularly. '
                    f'You must be able to sign in with Google using this email.'
                )
        
        # 1. Email cannot start with a number
        if email_name and email_name[0].isdigit():
            raise ValidationError(
                'Invalid email format. Gmail addresses cannot start with a number. '
                'Please use your real Gmail account.'
            )
        
        # 2. Check if email has too many consecutive numbers (more than 3)
        if re.search(r'\d{4,}', email_name):
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account with a proper name '
                '(e.g., john.doe@gmail.com, maryjane2024@gmail.com).'
            )
        
        # 3. Check if email is mostly numbers (more than 25% numbers is suspicious)
        digit_count = sum(c.isdigit() for c in email_name)
        if len(email_name) > 0 and digit_count / len(email_name) > 0.25:
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account with a proper name, '
                'not random characters or excessive numbers.'
            )
        
        # 4. Check for proper character distribution (vowels vs consonants)
        # Filter out numbers and special chars for this check
        letters_only = ''.join(c for c in email_name if c.isalpha())
        
        if len(letters_only) >= 5:  # Only check if we have enough letters
            vowels = set('aeiou')
            vowel_count = sum(1 for c in letters_only if c in vowels)
            
            # Real names typically have 30-50% vowels
            vowel_ratio = vowel_count / len(letters_only) if len(letters_only) > 0 else 0
            
            # STRICT: Vowel ratio should be between 25-55% for real names
            if vowel_ratio < 0.25:
                raise ValidationError(
                    'Email address appears to be random characters. '
                    'Please use your REAL Gmail account (e.g., john.doe@gmail.com, mary.smith@gmail.com). '
                    'You must be able to sign in with Google using this email.'
                )
            
            # Reject if TOO MANY vowels (suspiciously high ratio)
            if vowel_ratio > 0.55:
                raise ValidationError(
                    'Email address appears invalid. Please use your REAL Gmail account with a proper name.'
                )
        
        # 5. Check for extremely long random strings (more than 18 characters is suspicious)
        if len(email_name) > 18:
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account. '
                'Extremely long email addresses are not accepted.'
            )
        
        # 6. Check if the email looks like keyboard mashing (too many consecutive consonants)
        # More than 4 consonants in a row is very unusual in real names
        consonants = set(string.ascii_lowercase) - set('aeiou')
        consecutive_consonants = 0
        max_consecutive = 0
        
        for char in letters_only:
            if char in consonants:
                consecutive_consonants += 1
                max_consecutive = max(max_consecutive, consecutive_consonants)
            else:
                consecutive_consonants = 0
        
        if max_consecutive > 4:
            raise ValidationError(
                'Email address appears to be random characters (keyboard mashing). '
                'Please use your REAL Gmail account with your actual name.'
            )
        
        # 7. Check for repeating patterns that indicate random typing
        pattern_count = 0
        for i in range(len(email_name) - 2):
            if email_name[i].isalpha() and email_name[i+1].isdigit() and email_name[i+2].isalpha():
                pattern_count += 1
            elif email_name[i].isdigit() and email_name[i+1].isalpha() and email_name[i+2].isdigit():
                pattern_count += 1
        
        # More than 2 alternating patterns suggests random characters
        if pattern_count > 2:
            raise ValidationError(
                'Email address appears to contain random character patterns. '
                'Please use your REAL Gmail account.'
            )
        
        # 8. STRICT: Check for common dictionary words or recognizable patterns
        # If email is long and has NO recognizable patterns, it's likely fake
        common_name_patterns = [
            'john', 'jane', 'mary', 'james', 'robert', 'michael', 'william', 'david', 'joseph', 'thomas',
            'chris', 'daniel', 'matt', 'lisa', 'sarah', 'emily', 'anna', 'alex', 'ryan', 'kevin',
            'admin', 'support', 'contact', 'info', 'service', 'help'
        ]
        
        # If the email is long (>12 chars) and doesn't contain any recognizable patterns
        if len(letters_only) > 12:
            has_recognizable_pattern = any(pattern in letters_only.lower() for pattern in common_name_patterns)
            
            # Check for repeating characters (like "aaa", "bbb")
            has_repeating_chars = bool(re.search(r'(.)\1{2,}', letters_only))
            
            if not has_recognizable_pattern and not has_repeating_chars:
                # Additional entropy check: calculate character variety
                unique_chars = len(set(letters_only))
                char_variety_ratio = unique_chars / len(letters_only)
                
                # Real names usually have 0.4-0.75 character variety
                # Random strings have very high variety (0.75+)
                if char_variety_ratio > 0.72:
                    raise ValidationError(
                        'Email address appears to be randomly generated characters. '
                        'Please use your REAL Gmail account - the one you actually use and can verify. '
                        'Test emails and fake accounts will be rejected.'
                    )
        
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
        """Validate email - check for duplicates (excluding current user) and verify Gmail"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError('Email address is required.')
        
        # Ensure it's a Gmail account (required for Google Sign-In compatibility)
        if not email.lower().endswith('@gmail.com'):
            raise ValidationError(
                'Only Gmail addresses (@gmail.com) are accepted. '
                'This is required for Google Sign-In verification. '
                'Please use your real, active Gmail account.'
            )
        
        # Get the email username part (before @gmail.com)
        email_parts = email.lower().split('@')[0]
        
        # STRICT: Minimum length - real emails are rarely shorter than 5 characters
        if len(email_parts) < 5:
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account '
                '(the one you actually use and can sign in with Google). '
                'Test emails and fake accounts are NOT allowed.'
            )
        
        # Remove common separators for analysis
        email_name = email_parts.replace('.', '').replace('_', '').replace('-', '')
        
        # Check for suspicious patterns that indicate fake emails
        import string
        import re
        
        # STRICT CHECK: Block common test/fake email patterns
        blocked_patterns = [
            'test', 'fake', 'dummy', 'sample', 'example', 'temp', 'throwaway',
            'asdf', 'qwer', 'zxcv', 'abcd', 'user', 'email', 'mail'
        ]
        
        email_lower = email_parts.lower()
        for pattern in blocked_patterns:
            if pattern in email_lower:
                raise ValidationError(
                    f'Test and fake email addresses are NOT allowed. '
                    f'Please use your REAL, active Gmail account that you use regularly. '
                    f'You must be able to sign in with Google using this email.'
                )
        
        # 1. Email cannot start with a number
        if email_name and email_name[0].isdigit():
            raise ValidationError('Email address appears to be invalid. Email cannot start with a number.')
        
        # 2. Check if email has too many consecutive numbers (more than 3)
        if re.search(r'\d{4,}', email_name):
            raise ValidationError('Email address appears to be invalid. Please use a real Gmail account (e.g., john.doe@gmail.com).')
        
        # 3. Check if email is mostly numbers (more than 25% numbers is suspicious)
        digit_count = sum(c.isdigit() for c in email_name)
        if len(email_name) > 0 and digit_count / len(email_name) > 0.25:
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account with a proper name, '
                'not random characters or excessive numbers.'
            )
        
        # 4. Check for proper character distribution (vowels vs consonants)
        # Filter out numbers and special chars for this check
        letters_only = ''.join(c for c in email_name if c.isalpha())
        
        if len(letters_only) >= 5:  # Only check if we have enough letters
            vowels = set('aeiou')
            vowel_count = sum(1 for c in letters_only if c in vowels)
            
            # Real names typically have 30-50% vowels, fake random strings vary too much
            vowel_ratio = vowel_count / len(letters_only) if len(letters_only) > 0 else 0
            
            # STRICT: Vowel ratio should be between 25-55% for real names
            if vowel_ratio < 0.25:
                raise ValidationError(
                    'Email address appears to be random characters. '
                    'Please use your REAL Gmail account (e.g., john.doe@gmail.com, mary.smith@gmail.com). '
                    'You must be able to sign in with Google using this email.'
                )
            
            # Reject if TOO MANY vowels (suspiciously high ratio)
            if vowel_ratio > 0.55:
                raise ValidationError(
                    'Email address appears invalid. Please use your REAL Gmail account with a proper name.'
                )
        
        # 5. Check for extremely long random strings (more than 18 characters is suspicious)
        if len(email_name) > 18:
            raise ValidationError(
                'Email address appears invalid. Please use your REAL Gmail account. '
                'Extremely long email addresses are not accepted.'
            )
        
        # 6. Check if the email looks like keyboard mashing (too many consecutive consonants)
        # More than 4 consonants in a row is very unusual in real names
        consonants = set(string.ascii_lowercase) - set('aeiou')
        consecutive_consonants = 0
        max_consecutive = 0
        
        for char in letters_only:
            if char in consonants:
                consecutive_consonants += 1
                max_consecutive = max(max_consecutive, consecutive_consonants)
            else:
                consecutive_consonants = 0
        
        if max_consecutive > 4:
            raise ValidationError('Email address appears to be invalid. Please use a real Gmail account with a proper name.')
        
        # 7. Check for repeating patterns that indicate random typing (e.g., "fh3o1he", "2f3")
        # Count number of alternating letter-number-letter patterns
        pattern_count = 0
        for i in range(len(email_name) - 2):
            if email_name[i].isalpha() and email_name[i+1].isdigit() and email_name[i+2].isalpha():
                pattern_count += 1
            elif email_name[i].isdigit() and email_name[i+1].isalpha() and email_name[i+2].isdigit():
                pattern_count += 1
        
        # More than 2 alternating patterns suggests random characters
        if pattern_count > 2:
            raise ValidationError('Email address appears to be invalid. Please use a real Gmail account with a proper name.')
        
        # 8. STRICT: Check for common dictionary words or recognizable patterns
        # If email is long and has NO recognizable patterns, it's likely fake
        common_name_patterns = [
            'john', 'jane', 'mary', 'james', 'robert', 'michael', 'william', 'david', 'joseph', 'thomas',
            'chris', 'daniel', 'matt', 'lisa', 'sarah', 'emily', 'anna', 'alex', 'ryan', 'kevin',
            'admin', 'support', 'contact', 'info', 'service', 'help'
        ]
        
        # If the email is long (>12 chars) and doesn't contain any recognizable patterns
        if len(letters_only) > 12:
            has_recognizable_pattern = any(pattern in letters_only.lower() for pattern in common_name_patterns)
            
            # Check for repeating characters (like "aaa", "bbb")
            has_repeating_chars = bool(re.search(r'(.)\1{2,}', letters_only))
            
            if not has_recognizable_pattern and not has_repeating_chars:
                # Additional entropy check: calculate character variety
                unique_chars = len(set(letters_only))
                char_variety_ratio = unique_chars / len(letters_only)
                
                # Real names usually have 0.4-0.75 character variety
                # Random strings have very high variety (0.75+)
                if char_variety_ratio > 0.72:
                    raise ValidationError(
                        'Email address appears to be randomly generated characters. '
                        'Please use your REAL Gmail account - the one you actually use and can verify. '
                        'Test emails and fake accounts will be rejected.'
                    )
        
        # Check if email already exists for another user
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError('This email address is already being used by another account. Please use a different email.')
        
        return email.lower()
    
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
