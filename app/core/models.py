import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
import os


ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    )

ORDER_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
)



def product_image_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'product', filename)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role='customer', **extra_field):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email),
                          role=role, 
                          **extra_field
                          )
        user.set_password(password)

        if role == 'seller':
            user.is_staff = False
        elif role == 'admin':
            user.is_staff = True

        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password):
        user = self.create_user(email, password, role='admin')
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    
    objects = UserManager()

    USERNAME_FIELD = 'email'



class Tag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name
    


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name


class Product(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=product_image_file_path, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    warranty = models.IntegerField(default=12) 

    tags = models.ManyToManyField('Tag')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
   
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        return sum(item.product.price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product') 

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"
    

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"

    def calculate_total(self):
        total = sum(item.get_total() for item in self.items.all())
        self.total_price = total
        self.save()
        return total


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.PROTECT  
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) 

    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity} - {self.order.id}"
    

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return f"Review by {self.user.name} - {self.rating}⭐"


