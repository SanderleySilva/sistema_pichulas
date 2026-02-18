from django.urls import path
from .views import customLogin, customLogout


urlpatterns = [
    path('login/',customLogin.as_view(),name='login'),
    path('logout/',customLogout.as_view(),name='logout'),
]