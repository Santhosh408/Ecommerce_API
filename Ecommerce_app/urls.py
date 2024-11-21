from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.RegisterView.as_view()),
    path('login/',views.LoginView.as_view()),
    path('logout/',views.LogoutView.as_view()),
    path('hello/',views.HelloView.as_view()),
    path('admin/categories/',views.CategoryView.as_view()),
    path('admin/products/',views.AdminProductView.as_view()),
    path('admin/products/<int:pk>/',views.AdminProductDetailView.as_view()),
    path('products/',views.UserProductView.as_view()),
    path('products/<int:pk>/',views.UserProductDetailView.as_view()),
    path('user/profile/',views.UserProfileView.as_view()),
    path('user/orders/',views.ListOrdersView.as_view()),
    path('user/orders/place/',views.PlaceOrderView.as_view()),
    path('user/orders/<int:order_id>/',views.OrderDetailView.as_view()),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add-item/', views.AddCartItemView.as_view(), name='add-cart-item'),
    path('cart/remove-item/', views.RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('cart/clear/', views.ClearCartView.as_view(), name='clear-cart')
]
