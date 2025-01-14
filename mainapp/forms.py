from django import forms
from .models import Event, Contractor
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Booking


# EventForm to handle event creation/updation
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'time', 'location', 'description', 'poster_image']  # Added poster_image to Event form

# ContractorProfileForm to handle contractor profile updates (including profile image)
class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = Contractor
        fields = ['company_name', 'email', 'phone', 'profile_image']  # Includes profile image for contractor
class ContractorSignupForm(forms.ModelForm):
    company_name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=True)
    profile_image = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput(),
        }

# Customer Signup Form
class CustomerSignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'password': forms.PasswordInput(),
        }
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['num_tickets']  # Only allowing users to specify the number of tickets
        widgets = {
            'num_tickets': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of tickets',
                'min': 1
            }),
        }
        labels = {
            'num_tickets': 'Number of Tickets',
        }
