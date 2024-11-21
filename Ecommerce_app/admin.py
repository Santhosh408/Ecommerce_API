from django.contrib import admin
from .models import Product,Category
from django.contrib.auth import get_user_model

User = get_user_model()
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(User)
# admin.site.register(Order)
# admin.site.register(OrderItem)