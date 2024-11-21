from django.db.models import (Model,TextField,CharField,DecimalField,DateTimeField,
IntegerField,ForeignKey,OneToOneField,PositiveIntegerField,CASCADE)
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [('admin','Admin'),
    ('customer','Customer')]
    address = TextField(null=True,blank=True)
    phone_number = CharField(max_length=15,blank=True,null=True)
    user_type = CharField(max_length=10,choices=ROLE_CHOICES,default='customer')

    def __str__(self):
        return self.username
    
class Category(Model):
    name = CharField(max_length=100,unique=True)
    description = TextField(blank=True)

    def __self__(self):
        return self.name
    
class Product(Model):
    name = CharField(max_length=100)
    description = TextField(blank=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    stock = IntegerField()
    category = ForeignKey(Category,on_delete=CASCADE,related_name='products')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Cart(Model):
    user = OneToOneField(settings.AUTH_USER_MODEL,on_delete=CASCADE,related_name='cart')
    # product = ForeignKey(Product,on_delete=CASCADE,related_name='cart_items')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        f"Cart of {self.user.username}"

class CartItem(Model):
    cart = ForeignKey(Cart,on_delete=CASCADE,related_name='items')
    product = ForeignKey(Product,on_delete=CASCADE,related_name='cart_item')
    quantity = PositiveIntegerField(default=1)
    added_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.cart.user.username}"

class Order(Model):
    user = ForeignKey(settings.AUTH_USER_MODEL,on_delete=CASCADE,related_name='orders')
    total_price = DecimalField(max_digits=10,decimal_places=2)
    status = CharField(max_length=20,choices=[('Pending','Pending'),('Processing','Processing'),('Completed','Completed')],default='Pending')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"
    
class OrderItem(Model):
    order = ForeignKey(Order,on_delete=CASCADE,related_name='items')
    product = ForeignKey(Product,on_delete=CASCADE)
    quantity = PositiveIntegerField()
    price = DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"
