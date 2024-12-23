# views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login , logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import *
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.forms import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)
        # Add categories to the context
        context['categories'] = Category.objects.all()
        # Add photos to the context
        context['photos'] = Photo.objects.all()
        # Add tourist locations to the context
        context['tourist_locations'] = TouristLocation.objects.all()
        return context

    
    
class CustomerRegisterView(View):
    def get(self, request):
        return render(request, 'login.html')  # Return the sign-up page

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords don't match")
            return redirect('customer_register')  # Stay on the signup page

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')  # Redirect to login page after successful registration
        except:
            messages.error(request, 'Username already exists')
            return redirect('customer_register')


class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Log the user in
            # Redirect based on user role
            if user.role == 'admin':
                return redirect('adminindex')  # Redirect to custom admin dashboard
            else:
                return redirect('index')  # Redirect to customer dashboard
            messages.success(request, 'You have been logged in successfully.')
        else:
            messages.error(request, 'Invalid username or password.')
        
        return render(request, self.template_name)  # Re-render the login form with error message

class LogoutView(View):
    def get(self, request):
        logout(request)  # Log out the user
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')


class AdminIndexView(TemplateView):
    template_name="admin/base_generic.html"

# List View for Categories
class CategoryListView(ListView):
    model = Category
    template_name = 'admin/category_list.html'
    context_object_name = 'categories'

# Create View for Category
class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin/category_form.html'
    success_url = reverse_lazy('category_list')

# Update View for Category
class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin/category_form.html'
    success_url = reverse_lazy('category_list')

# Delete View for Category
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'admin/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    

# Create View for Seasonal Pricing
class SeasonalPricingCreateView(CreateView):
    model = SeasonalPricing
    form_class = SeasonalPricingForm
    template_name = 'admin/seasonalpricing_add.html'

    def get_initial(self):
        initial = super().get_initial()
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        initial['category'] = category
        return initial

    def form_valid(self, form):
        category = get_object_or_404(Category, pk=self.kwargs.get('category_id'))

        # Check if there is already a seasonal pricing for this category
        existing_pricing = SeasonalPricing.objects.filter(category=category).exists()
        if existing_pricing:
            raise ValidationError("A seasonal pricing already exists for this category. Only one seasonal pricing is allowed.")
        
        form.instance.category = category
        return super().form_valid(form)

    success_url = reverse_lazy('seasonalpricing_list')
    
    
# Seasonal Pricing List View
class SeasonalPricingListView(ListView):
    model = SeasonalPricing
    template_name = 'admin/seasonalpricing_list.html'
    context_object_name = 'seasonal_prices'

    def get_queryset(self):
        return SeasonalPricing.objects.select_related('category').all()

# Update View for Seasonal Pricing
class SeasonalPricingUpdateView(UpdateView):
    model = SeasonalPricing
    form_class = SeasonalPricingForm
    template_name = 'admin/seasonalpricing_form.html'
    success_url = reverse_lazy('category_list')

# Delete View for Seasonal Pricing
class SeasonalPricingDeleteView(DeleteView):
    model = SeasonalPricing
    template_name = 'admin/seasonalpricing_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    

# Create View for Tourist Location
class TouristLocationCreateView(CreateView):
    model = TouristLocation
    form_class = TouristLocationForm
    template_name = 'admin/touristlocation_form.html'
    success_url = reverse_lazy('category_list')

# Update View for Tourist Location
class TouristLocationUpdateView(UpdateView):
    model = TouristLocation
    form_class = TouristLocationForm
    template_name = 'admin/touristlocation_form.html'
    success_url = reverse_lazy('category_list')

# Delete View for Tourist Location
class TouristLocationDeleteView(DeleteView):
    model = TouristLocation
    template_name = 'admin/touristlocation_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    
# Tourist Location List View
class TouristLocationListView(ListView):
    model = TouristLocation
    template_name = 'admin/touristlocation_list.html'
    context_object_name = 'tourist_locations'

    def get_queryset(self):
        return TouristLocation.objects.all()
    


class PhotoAddView(View):
    template_name = 'admin/photo_add.html'  # Template for adding photos

    def get(self, request):
        form = PhotoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('photo_list')  # Redirect to the photo list page
        return render(request, self.template_name, {'form': form})  
    
    
class PhotoListView(View):
    template_name = 'admin/photo_list.html'

    def get(self, request):
        photos = Photo.objects.all()
        return render(request, self.template_name, {'photos': photos})
    

class PhotoDeleteView(View):
    def post(self, request, pk):
        photo = get_object_or_404(Photo, pk=pk)
        photo.delete()
        return redirect('photo_list')
    

class AdminBookingListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Booking
    template_name = 'admin/reservation_list.html'
    context_object_name = 'reservations'

    def test_func(self):
        # Ensure only admins can access this view
        return self.request.user.role == 'admin'

    def get_queryset(self):
        # Return all bookings
        return Booking.objects.all()
    
##################################################################################################################################################

from datetime import timedelta
from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone

class BookingCreateView(LoginRequiredMixin, View):
    template_name = 'customer/booking_add.html'

    def get(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        form = BookingForm(initial={'Category': category})
        return render(request, self.template_name, {'form': form, 'category': category})

    def post(self, request, category_id):
        category = get_object_or_404(Category, pk=category_id)
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)

            # Assign the logged-in customer and selected category to the booking
            booking.customer = request.user
            booking.Category = category

            # Get the booking dates
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            if end_date <= start_date:
                messages.error(request, "End date must be after the start date.")
                return render(request, self.template_name, {'form': form, 'category': category})

            # Calculate total nights (exclusive of the end date)
            total_nights = (end_date - start_date).days

            if total_nights <= 0:
                messages.error(request, "End date must be after the start date.")
                return render(request, self.template_name, {'form': form, 'category': category})

            # Initialize total price variable
            total_price = 0
            current_date = start_date

            # Loop through each day in the booking range and calculate the price
            while current_date < end_date:
                seasonal_pricing = SeasonalPricing.objects.filter(
                    category=category,
                    start_date__lte=current_date,
                    end_date__gte=current_date
                ).first()

                # If seasonal pricing is found, use it; otherwise, use the normal price
                price_per_night = seasonal_pricing.price_per_night if seasonal_pricing else category.price_per_night

                # Add the price of the current day to the total price
                total_price += price_per_night
                current_date += timedelta(days=1)

            # Check if there are available rooms
            if category.number_of_rooms <= 0 or not category.is_available:
                messages.error(request, "No rooms available for the selected category.")
                return render(request, self.template_name, {'form': form, 'category': category})

            # Deduct a room and save the booking
            category.number_of_rooms -= 1
            category.save()

            # Set the total price and save the booking
            booking.total_price = total_price
            booking.save()

            messages.success(request, "Booking successful!")
            return redirect('booking_list')  # Redirect to the booking list page

        return render(request, self.template_name, {'form': form, 'category': category})

    

class BookingListView(ListView):
    model = Booking
    template_name = 'customer/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        # Filter bookings for the currently logged-in customer
        return Booking.objects.filter(customer=self.request.user)
    

class BookingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Booking
    template_name = 'customer/booking_confirm_delete.html'
    success_url = reverse_lazy('booking_list')

    def test_func(self):
        # Ensure the booking belongs to the logged-in user
        booking = self.get_object()
        return booking.customer == self.request.user
    