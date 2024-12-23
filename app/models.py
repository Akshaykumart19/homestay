from django.db import models
from django.contrib.auth.models import AbstractUser , BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

    objects = CustomUserManager()  # Use the custom manager for user creation

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)  # Price for the category
    number_of_rooms = models.PositiveIntegerField(default=0)  # Number of rooms in this category
    is_available = models.BooleanField(default=True)  # Availability of the category
    image = models.ImageField(upload_to='category/', blank=True, null=True)
    free_wifi = models.BooleanField(default=False)  # Free Wi-Fi availability
    hot_water = models.BooleanField(default=False)  # Hot water availability
    swimming_pool = models.BooleanField(default=False)  # Swimming pool availability
    kitchen = models.BooleanField(default=False)  # Kitchen availability
    parking_area = models.BooleanField(default=False)  # Parking area availability
    is_ac = models.BooleanField(default=False)  # Air-conditioned room
    is_non_ac = models.BooleanField(default=False)  # Non-air-conditioned room
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# Seasonal Pricing Model (applied per Category)
class SeasonalPricing(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='seasonal_prices')
    start_date = models.DateField()
    end_date = models.DateField()
    price_per_night = models.DecimalField(max_digits=8, decimal_places=2)  # Override price for the category during this season

    class Meta:
        unique_together = ('category', 'start_date', 'end_date')
        
    def __str__(self):
        return f"{self.category.name} - {self.price_per_night} (from {self.start_date} to {self.end_date})"


# Tourist Location Model
class TouristLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    distance_from_home_stay = models.DecimalField(max_digits=5, decimal_places=2, help_text="Distance in kilometers")
    image = models.ImageField(upload_to='tourist_locations/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    link=models.CharField(null=True,max_length=100)

    def __str__(self):
        return self.name

# Booking Model
class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'customer'})
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    _total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Backing field

    def __str__(self):
        return f"{self.customer.username} - {self.Category.name} ({self.start_date} to {self.end_date})"

    @property
    def total_price(self):
        if self._total_price is not None:
            return self._total_price

        # Check for seasonal pricing
        seasonal_pricing = SeasonalPricing.objects.filter(
            category=self.Category,
            start_date__lte=self.start_date,
            end_date__gte=self.end_date
        ).first()

        price_per_night = seasonal_pricing.price_per_night if seasonal_pricing else self.Category.price_per_night
        total_days = (self.end_date - self.start_date).days

        return total_days * price_per_night

    @total_price.setter
    def total_price(self, value):
        self._total_price = value

    
    def delete(self, *args, **kwargs):
        # Restore room availability when booking is deleted
        self.Category.number_of_rooms += 1
        self.Category.save()
        super().delete(*args, **kwargs)

# Payment Model
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('pending', 'Pending'), ('failed', 'Failed')])
    transaction_id = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.booking} - {self.amount} ({self.status})"


class Photo(models.Model):
    image = models.ImageField(upload_to='photos/')  # Store images in the 'media/photos/' directory
    caption = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.caption if self.caption else f"Photo {self.id}"
    
