from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login-user/', views.login_user, name='login_user'),
    path('logout-user/', views.logout_user, name='logout_user'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password-validate/<uidb64>/<token>/',
         views.reset_password_validate, name='reset_password_validate'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-details/<orderNumber>',
         views.order_details, name='order_details'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]
