from django.urls import path
from booking import views
app_name = 'main'
urlpatterns = [


    path('', views.home, name="home"),
    path('reservation_list/', views.reservation_list, name="reservation_list"),
    path('book_location/', views.book_location, name="book_location"),
    path('booking-details/<int:pk>/', views.booking_details, name="booking_details"),
    path('activation/<int:booking_id>/<str:token>/', views.activation_view, name="activation"),
    path('profile/', views.profile_view, name="profile_view"),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),

]

