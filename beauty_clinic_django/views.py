from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse


def home(request):
    """Home page view"""
    # Redirect admin users to admin dashboard
    if request.user.is_authenticated and request.user.user_type == 'admin':
        return redirect('appointments:admin_dashboard')
    
    response = render(request, 'home.html')
    # Prevent caching of home page for logged-out users
    if not request.user.is_authenticated:
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
    return response


@never_cache
@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout view with proper cache control to prevent back button access"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    response = redirect('home')
    # Clear all session data
    request.session.flush()
    # Prevent caching of logout page and redirect
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
