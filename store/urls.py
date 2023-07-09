from django.contrib import admin
from django.urls import path
from . import views
from store.middleware.auth import auth_middleware

urlpatterns = [
    path('', views.Index.as_view(), name='home'),
    path('signup/', views.SignUP.as_view(), name='signup'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path('cart/', views.Cart.as_view(), name='cart'),
    path('checkout', auth_middleware(views.Checkout.as_view()), name='checkout'),
    path('order', auth_middleware(views.OrderView.as_view()), name='order'),
]
