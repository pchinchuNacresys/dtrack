from django.urls import path
from .views import *

urlpatterns = [
    # path('api_login', api_login, name='api_login'),
    
    path('APILoginView',APILoginView.as_view(), name='api_login'),
    path('APILogoutView',APILogoutView.as_view(), name='api_logout'),
]