from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import RegexValidator
import uuid
from django.db import models
from django.contrib.auth.models import User
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from django.core.files.base import ContentFile

class Contractor(models.Model):
    """
    Model representing a contractor.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)

    # Email field (separate from contact_details)
    email = models.EmailField(unique=True)

    # Contact details field for storing additional contact information
    contact_details = models.TextField(blank=True, null=True, help_text="Additional contact information (e.g., phone, address).")

    # Phone field with validation for format
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17)

    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_image = models.ImageField(upload_to='contractor_profiles/', null=True, blank=True)  # Profile Image field

    def __str__(self):
        return self.company_name

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    contractor = models.ForeignKey('Contractor', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    capacity = models.PositiveIntegerField(default=100)
    remaining_spots = models.PositiveIntegerField(default=100)
    poster_image = models.ImageField(upload_to='event_posters/', null=True, blank=True)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Add ticket price field

    def __str__(self):
        return self.title

    def book_spot(self, num_tickets=1):
        """
        Book a specified number of spots for an event. Reduces the remaining spots.
        """
        if self.remaining_spots >= num_tickets:
            self.remaining_spots -= num_tickets
            self.save()
            return True
        return False

    def cancel_spot(self, num_tickets=1):
        """
        Cancel a specified number of bookings, increasing the remaining spots.
        """
        self.remaining_spots += num_tickets
        self.save()
class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    num_tickets = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    booking_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total price based on the ticket price
        self.total_price = self.num_tickets * self.event.ticket_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.event.title} ({self.num_tickets} tickets)"
class Ticket(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='ticket')
    ticket_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    barcode = models.ImageField(upload_to='barcodes/', blank=True, null=True)

    def generate_barcode(self):
        barcode_generator = Code128(str(self.ticket_id), writer=ImageWriter())
        buffer = BytesIO()
        barcode_generator.write(buffer)
        self.barcode.save(f"{self.ticket_id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.generate_barcode()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket for Booking {self.booking.id}"
