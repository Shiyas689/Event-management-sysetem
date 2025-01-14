from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import ContractorLoginView


urlpatterns = [
    # Home view
    path('', views.home, name='home'),
    path('contractor/home/', views.contractor_home, name='contractor_home'),
    path('contractor/login/', ContractorLoginView.as_view(), name='contractor_login'),

    # Event related views
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/', views.event_list, name='event_list'),
    
    # Contractor related views
    path('contractors/', views.contractor_list, name='contractor_list'),
    path('contractor/profile/<int:pk>/', views.contractor_profile, name='contractor_profile'),
    path('contractor/<int:contractor_id>/', views.contractor_profile_view, name='contractor_profile'),
    path('event/create/', views.create_event, name='create_event'),
    path('contractor/login/', views.contractor_login, name='contractor_login'),
    path('contractor/signup/', views.contractor_signup, name='contractor_signup'),

    # User related views
    path('customer/login/', views.customer_login, name='customer_login'),
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('logout/', views.user_logout, name='user_logout'),
    path('reset',views.Resethome,name='reset'),
    path('passwordreset',views.resetPassword,name='resetPassword'),
    # About and contact views
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Booking view
    path('book-event/<int:event_id>/', views.book_event, name='book_event'),
    path('ticket/<int:ticket_id>/', views.ticket_view, name='ticket_view'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
