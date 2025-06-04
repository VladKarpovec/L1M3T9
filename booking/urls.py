from django.urls import path
from booking import views
app_name = 'main'

urlpatterns = [
    path('', views.home, name="home")
]