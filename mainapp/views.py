from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Event, Contractor, Booking,Ticket
from .forms import EventForm, ContractorProfileForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
import datetime
from .forms import ContractorSignupForm, CustomerSignupForm
from .models import Contractor
from .forms import BookingForm
from django.http import HttpResponse
import io
import base64
from barcode import Code128
from barcode.writer import ImageWriter
from django.core.files.base import ContentFile
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

# Home View
def home(request):
    """
    Renders the home page for all users. If the user is a contractor, redirects them to the contractor home.
    """
    if request.user.is_authenticated:
        try:
            contractor = Contractor.objects.get(user=request.user)
            # Redirect authenticated contractors to their specific home page
            return redirect('contractor_home')
        except Contractor.DoesNotExist:
            pass  # Non-contractor users proceed to the general home page

    # Fetch general home page data
    upcoming_events = Event.objects.filter(date__gte=datetime.date.today()).order_by('date')[:20]
    top_contractors = Contractor.objects.all()[:5]

    context = {
        'events': upcoming_events,
        'contractors': top_contractors,
    }
    return render(request, 'home.html', context)
def contractor_home(request):
    """
    Contractor-specific home view displaying the contractor's events.
    """
    try:
        contractor = Contractor.objects.get(user=request.user)
    except Contractor.DoesNotExist:
        # Redirect if the user is not associated with a contractor profile
        return redirect('home')

    # Fetch all events linked to the contractor
    events = contractor.event_set.all()

    context = {
        'contractor': contractor,
        'events': events,
    }
    return render(request, 'contractor_home.html', context)
class ContractorLoginView(LoginView):
    template_name = 'contractor_login.html'
    success_url = reverse_lazy('contractor_home')

# Event Detail View
def event_detail(request, event_id):
    """
    Renders the detail page for a specific event.
    """
    event = get_object_or_404(Event, pk=event_id)
    user_booking = Booking.objects.filter(event=event, user=request.user).first()
    context = {'event': event, 'user_booking': user_booking}
    return render(request, 'event_detail.html', context)

# Contractor Profile View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Contractor, Event

@login_required
def contractor_profile(request, pk):
    contractor = get_object_or_404(Contractor, pk=pk, user=request.user)

    if request.method == 'POST':
        # Update contractor profile fields
        contractor.company_name = request.POST.get('company_name', contractor.company_name)
        contractor.phone = request.POST.get('phone', contractor.phone)
        contractor.contact_details = request.POST.get('contact_details', contractor.contact_details)

        # Handle profile image upload
        if 'profile_image' in request.FILES:
            contractor.profile_image = request.FILES['profile_image']

        contractor.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('contractor_profile', pk=pk)

    return render(request, 'contractor_profile.html', {
        'contractor': contractor,
    })
@login_required
def create_event(request):
    # Check if the user is a contractor
    try:
        contractor = Contractor.objects.get(user=request.user)
    except Contractor.DoesNotExist:
        messages.error(request, "You need to be a contractor to create an event.")
        return redirect('home')

    if request.method == 'POST':
        # Collect event details from form
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        location = request.POST.get('location')
        capacity = int(request.POST.get('capacity'))
        ticket_price = float(request.POST.get('ticket_price'))
        poster_image = request.FILES.get('poster_image')

        # Save the new event
        Event.objects.create(
            title=title,
            description=description,
            date=date,
            time=time,
            location=location,
            capacity=capacity,
            remaining_spots=capacity,
            ticket_price=ticket_price,
            poster_image=poster_image,
            contractor=contractor
        )
        messages.success(request, "Event created successfully! You can create another event below.")
        
        # Redirect to the same page to clear the form
        return redirect('create_event')

    return render(request, 'create_event.html', {})

# Event List View
def event_list(request):
    events = Event.objects.all()  # Get all events
    return render(request, 'event.html', {'events': events})

# Contractor List View
def contractor_list(request):
    """
    Displays a list of all contractors.
    """
    contractors = Contractor.objects.all()
    return render(request, 'contractor.html', {'contractors': contractors})

# About View
def about(request):
    """
    Displays the about page.
    """
    return render(request, 'about.html')

# Contact View
def contact(request):
    """
    Displays the contact page.
    """
    return render(request, 'contact.html')
def contractor_profile_view(request, contractor_id):
    # Fetch the contractor by ID
    contractor = get_object_or_404(Contractor, id=contractor_id)
    
    # Fetch the latest events associated with the contractor
    events = Event.objects.filter(contractor=contractor).order_by('-date')[:20]  # Modify limit as needed

    # Render the template with context
    context = {
        'contractor': contractor,
        'events': events
    }
    return render(request, 'contractor_profile_view.html', context)
# Contractor Signup
def contractor_signup(request):
    try:
        if request.method == "POST":
            form = ContractorSignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)  # Save form but don't commit to DB yet
                user.set_password(form.cleaned_data['password'])  # Set hashed password
                user.save()

                # Additional fields for contractor
                Contractor.objects.create(
                    user=user,
                    company_name=form.cleaned_data['company_name'],
                    phone=form.cleaned_data['phone'],
                    email=form.cleaned_data['email']
                )

                messages.success(request, "Signup successful. Please log in.")
                return redirect('contractor_login')  # Redirect to contractor login page
            else:
                messages.error(request, "Invalid submission. Please fix the errors below.")
        else:
            form = ContractorSignupForm()

    except Exception as e:
        print(f"Error during contractor signup: {e}")
        messages.error(request, "An error occurred. Please try again.")
        form = ContractorSignupForm()

    return render(request, 'signup_contractor.html', {'form': form})
# Contractor Login
def contractor_login(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)

                # Check if the user is a contractor
                if hasattr(user, 'contractor'):  # Assuming your User model has a related 'contractor' model
                    messages.success(request, "Login successful.")
                    return redirect('contractor_home')  # Ensure this matches the URL name in urls.py
                else:
                    messages.error(request, "Access restricted to contractors.")
                    return redirect('contractor_login')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Both username and password are required.")

    return render(request, 'contractor_login.html')

# Customer Signup View
def customer_signup(request):
    if request.method == "POST":
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()

            messages.success(request, "Signup successful. Please log in.")
            return redirect('customer_login')  # Adjust as per your URL name
        else:
            messages.error(request, "Invalid signup details. Please try again.")
    else:
        form = CustomerSignupForm()

    return render(request, 'signup_user.html', {'form': form})
# Customer Login
def customer_login(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('home')  # Adjust 'home' to your desired redirect URL
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Both fields are required.")

    return render(request, 'customer_login.html')

# Logout View
@login_required
def user_logout(request):
    """
    Logs out the user.
    """
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('home')
# Book Event View
@login_required
def book_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.event = event
            booking.user = request.user
            booking.save()
            
            # Generate ticket
            ticket = Ticket.objects.create(booking=booking)
            
            messages.success(request, "Booking successful! Here's your ticket.")
            return redirect('ticket_view', ticket_id=ticket.id)
    else:
        form = BookingForm()
    
    return render(request, 'booking.html', {'form': form, 'event': event})

def Resethome(request):
    return render(request,'Resetpassword.html')

def resetPassword(request):
    username=request.POST['username']
    newpwd=request.POST['password']
    try:
        user=User.objects.get(username=username)
        if user is not None:
            user.set_password(newpwd)
            user.save()
            return render (request,'Resetpassword.html',{"msg":"password reset successfully"})
    except Exception as e:
        print(e)
        return render (request,'Resetpassword.html',{"msg":"password reset failed"})
def ticket_view(request, ticket_id):
    # Fetch the booking by the provided ticket_id
    booking = get_object_or_404(Booking, id=ticket_id)

    # Generate the barcode data
    barcode_data = f"Booking ID: {booking.id} | User: {booking.user.username} | Event: {booking.event.title}"
    
    # Create barcode object
    barcode = Code128(barcode_data, writer=ImageWriter())
    
    # Create a BytesIO buffer to store the barcode image
    buffer = io.BytesIO()
    barcode.write(buffer)
    barcode_image = buffer.getvalue()

    # Convert the binary image to a base64 encoded string
    barcode_base64 = base64.b64encode(barcode_image).decode('utf-8')

    # Prepare the context with the booking and the base64 encoded image
    context = {
        "booking": booking,
        "barcode_image": barcode_base64,  # Pass the base64 string for inline display
    }
    return render(request, "ticket.html", context)