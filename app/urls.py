from django.urls import path
from .views import*
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("",IndexView.as_view(),name="index"),
    path('register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("adminn/",AdminIndexView.as_view(),name="adminindex"),
   
    # Category URLs
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/add/', CategoryCreateView.as_view(), name='category_add'),
    path('categories/<int:pk>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # Seasonal Pricing URLs
    path('seasonalpricing/', SeasonalPricingListView.as_view(), name='seasonalpricing_list'),
    path('seasonalpricing/add/<int:category_id>/',SeasonalPricingCreateView.as_view(), name='seasonalpricing_add'),  
    path('seasonalpricing/<int:pk>/edit/', SeasonalPricingUpdateView.as_view(), name='seasonalpricing_edit'),
    path('seasonalpricing/<int:pk>/delete/', SeasonalPricingDeleteView.as_view(), name='seasonalpricing_delete'),

    # Tourist Location URLs
    path('touristlocations/', TouristLocationListView.as_view(), name='touristlocation_list'),
    path('touristlocations/add/', TouristLocationCreateView.as_view(), name='touristlocation_add'),
    path('touristlocations/<int:pk>/edit/', TouristLocationUpdateView.as_view(), name='touristlocation_edit'),
    path('touristlocations/<int:pk>/delete/', TouristLocationDeleteView.as_view(), name='touristlocation_delete'),
    
    
    path('photos/add/', PhotoAddView.as_view(), name='photo_add'),  # Add photo
    path('photos/', PhotoListView.as_view(), name='photo_list'),  # List photos
    path('photos/delete/<int:pk>/', PhotoDeleteView.as_view(), name='photo_delete'),  # Delete photo
    
    path('reservationsList/', AdminBookingListView.as_view(), name='admin_reservations'),

    
    
    path('bookings/add/<int:category_id>/', BookingCreateView.as_view(), name='booking_add'),
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)