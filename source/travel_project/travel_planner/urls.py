# travel_planner/urls.py
from django.urls import path
from .views import chat_with_ai
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('categories',views.categories, name='categories'),
    path('login', views.login, name='login'),
    path('religious', views.religious, name='religious'),
    path('itinerary_1', views.itinerary_1, name='itinerary_1'),
    path('chat/', chat_with_ai, name='chat_with_ai'),  
    path('home', views.home, name='home'),
    path('search-cities/', views.search_cities, name='search_cities'),
]

