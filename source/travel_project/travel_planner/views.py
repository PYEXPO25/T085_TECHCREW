from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from .models import Destination, Activity, Itinerary, ItineraryActivity
from .forms import ItineraryPreferencesForm

def index(request):
    return render(request, 'index.html')

from django.shortcuts import render

def login(request):
    return render(request, 'login.html') 

def categories(request):
    return render(request, 'categories.html') 

def religious(request):
    return render(request, 'religious.html')

def itinerary_1(request):
    return render(request, 'itinerary_1.html')


# @login_required
# def generate_itinerary(request):
#     if request.method == 'POST':
#         form = ItineraryPreferencesForm(request.POST)
#         if form.is_valid():
#             itinerary = form.save(commit=False)
#             itinerary.user = request.user
#             itinerary.save()
            
#             # Get user preferences
#             interests = form.cleaned_data['interests']
#             pace = form.cleaned_data['pace_preference']
#             budget = form.cleaned_data['budget']
            
#             # Calculate trip duration
#             duration = (itinerary.end_date - itinerary.start_date).days + 1
            
#             # Get suitable destinations based on preferences and budget
#             destinations = Destination.objects.filter(
#                 typical_cost__lte=budget/duration
#             )
            
#             # Add destinations to itinerary
#             itinerary.destinations.set(destinations[:3])  # Limit to 3 destinations
            
#             # Get activities based on interests
#             activities = Activity.objects.filter(
#                 destination__in=destinations,
#                 cost__lte=budget/(duration*3)  # Assuming 3 activities per day
#             )
            
#             # Create daily schedule based on pace preference
#             activities_per_day = {
#                 'relaxed': 2,
#                 'moderate': 3,
#                 'intense': 4
#             }[pace]
            
#             # Add activities to itinerary
#             current_date = itinerary.start_date
#             while current_date <= itinerary.end_date:
#                 for i, activity in enumerate(activities[:activities_per_day]):
#                     ItineraryActivity.objects.create(
#                         itinerary=itinerary,
#                         activity=activity,
#                         day=(current_date - itinerary.start_date).days + 1,
#                         time_slot=f"{9 + i*3}:00"  # Activities start at 9 AM, 3 hours apart
#                     )
#                 current_date += timedelta(days=1)
            
#             return redirect('view_itinerary', pk=itinerary.pk)
#     else:
#         form = ItineraryPreferencesForm()
    
#     return render(request, 'travel_planner/generate_itinerary.html', {'form': form})

# def view_itinerary(request, pk):
#     itinerary = Itinerary.objects.get(pk=pk)
#     activities = itinerary.itineraryactivity_set.all().order_by('day', 'time_slot')
    
#     # Group activities by day
#     daily_schedule = {}
#     for activity in activities:
#         if activity.day not in daily_schedule:
#             daily_schedule[activity.day] = []
#         daily_schedule[activity.day].append(activity)
    
#     return render(request, 'travel_planner/view_itinerary.html', {
#         'itinerary': itinerary,
#         'daily_schedule': daily_schedule
#     })