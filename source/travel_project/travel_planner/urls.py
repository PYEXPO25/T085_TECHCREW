# travel_planner/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('categories',views.categories, name='categories'),
    path('login', views.login, name='login'),
    path('religious', views.religious, name='religious'),
    path('itinerary_1', views.itinerary_1, name='itinerary_1'),
]

