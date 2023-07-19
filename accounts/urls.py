from django.urls import path
from . import views

urlpatterns = [
    path('registerUser/', views.register_user, name='registerUser'),
    path('registerVendor/', views.register_vendor, name='registerVendor'),

    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('myAccount/', views.my_account, name='myAccount'),
    path('custDashboard/', views.cust_dashboard, name='custDashboard'),
    path('vendorDashboard/', views.vendor_dashboard, name='vendorDashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate-email'),
]
