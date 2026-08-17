from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
import httpx
import json
from django.conf import settings
from .models import ContactMessage


@ensure_csrf_cookie
def home(request):
    """Home page with welcome message and feature highlights."""
    context = {
        'page_title': 'Home',
        'features': [
            {
                'icon': 'shield',
                'title': 'Website Analysis',
                'description': 'Checks website for threats, suspicious '
                               'activity and security issues.',
            },
            {
                'icon': 'globe',
                'title': 'Government Verification',
                'description': 'Verifies official government websites and '
                               'detects impersonation.',
            },
            {
                'icon': 'report',
                'title': 'Detailed Report',
                'description': 'Get risk score and clear reasons behind '
                               'the results.',
            },
            {
                'icon': 'bolt',
                'title': 'Fast & Lightweight',
                'description': 'Quick results with minimal impact on '
                               'performance.',
            },
        ],
    }
    return render(request, 'FakeOutApp/home.html', context)


def about(request):
    """About page describing the project/mission."""
    context = {
        'page_title': 'About',
    }
    return render(request, 'FakeOutApp/about.html', context)


def contact(request):
    """Contact page with a working contact form."""
    context = {
        'page_title': 'Contact',
    }

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        form_data = {'name': name, 'email': email, 'subject': subject, 'message': message_text}

        if name and email and message_text:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message_text,
            )
            messages.success(
                request,
                "Thanks for reaching out! We've received your message "
                "and will get back to you soon."
            )
            return redirect('FakeOutApp:contact')
        else:
            if not name: form_data['name'] = ''
            if not email: form_data['email'] = ''
            if not message_text: form_data['message'] = ''
            
            messages.error(
                request,
                'Please fill in your name, email, and message before submitting.'
            )
            context['form_data'] = form_data

    return render(request, 'FakeOutApp/contact.html', context)


def help_view(request):
    """Help & FAQ page with categorized accordion questions."""
    context = {
        'page_title': 'Help & FAQ',
    }
    return render(request, 'FakeOutApp/help.html', context)


def signup_view(request):
    """
    Creates a new account and saves it to the database using Django's
    built-in User model (table: auth_user). The email is used as the
    username since FakeOut logs users in with their email address.
    """
    if request.user.is_authenticated:
        return redirect('FakeOutApp:home')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        form_data = {'name': name, 'email': email}
        error = None
        if not name or not email or not password:
            error = 'Please fill in all fields.'
            if not name: form_data['name'] = ''
            if not email: form_data['email'] = ''
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif len(password) < 8:
            error = 'Password must be at least 8 characters long.'
        elif User.objects.filter(email=email).exists():
            error = 'An account with this email already exists.'
            form_data['email'] = ''

        if error:
            messages.error(request, error)
            return render(request, 'FakeOutApp/signup.html', {'form_data': form_data})

        # Save the new user to the database.
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,   # create_user() hashes this automatically
            first_name=name,
        )

        login(request, user)
        messages.success(request, f'Welcome to FakeOut, {name}!')
        return redirect('FakeOutApp:home')

    return render(request, 'FakeOutApp/signup.html')


def login_view(request):
    """Authenticates a user against the database and logs them in."""
    if request.user.is_authenticated:
        return redirect('FakeOutApp:home')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.email}!')
            return redirect('FakeOutApp:home')
        else:
            messages.error(request, 'Invalid email or password.')
            form_data = {'email': email}
            return render(request, 'FakeOutApp/login.html', {'form_data': form_data})

    return render(request, 'FakeOutApp/login.html')


def logout_view(request):
    """Logs the current user out."""
    logout(request)
    messages.success(request, "You've been logged out.")
    return redirect('FakeOutApp:home')
def report_view(request):
    """
    Full report page. Reached from the extension's "View Full Report"
    button (?url=<the analyzed url>), or by pasting a URL into the
    site's own Analyze box on the home page.
 
    Re-runs the analysis against the FastAPI backend server-side rather
    than trusting any score/status passed in the query string, so a
    crafted link can't claim a malicious site is "safe".
    """
    target_url = request.GET.get('url', '').strip()
    context = {
        'page_title': 'Full Report',
        'target_url': target_url,
    }
 
    if not target_url:
        context['error'] = 'No URL was provided to analyze.'
        return render(request, 'FakeOutApp/report.html', context)
 
    try:
        response = httpx.post(
            f'{settings.FAKEOUT_API_BASE_URL}/api/analyze',
            json={'url': target_url},
            timeout=20.0,
        )
        response.raise_for_status()
        data = response.json()
        context['result'] = data
    except (httpx.HTTPError, ValueError):
        context['error'] = (
            "We couldn't reach the FakeOut analysis service right now. "
            "Please make sure the backend is running and try again."
        )
 
    return render(request, 'FakeOutApp/report.html', context)


@require_POST
def analyze_api(request):
    """
    AJAX endpoint: accepts a JSON body with {"url": "..."}, proxies it to
    the FastAPI backend, and returns the full analysis JSON to the browser.
    """
    try:
        body = json.loads(request.body)
        target_url = body.get('url', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request body.'}, status=400)

    if not target_url:
        return JsonResponse({'error': 'No URL provided.'}, status=400)

    try:
        response = httpx.post(
            f'{settings.FAKEOUT_API_BASE_URL}/api/analyze',
            json={'url': target_url},
            timeout=25.0,
        )
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except httpx.TimeoutException:
        return JsonResponse(
            {'error': 'Analysis timed out. Please try again.'},
            status=504,
        )
    except (httpx.HTTPError, ValueError):
        return JsonResponse(
            {'error': "Couldn't reach the analysis service. Is the backend running?"},
            status=502,
        )