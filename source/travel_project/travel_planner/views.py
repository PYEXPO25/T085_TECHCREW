from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
from .models import Religious  # Import the Religious model
import requests  # For sending data to Gemini AI

# Configure Google Gemini AI
GOOGLE_API_KEY = "AIzaSyB9hq8iaipp08G6vCtdYz_WQ4C_cgiLyXA"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

def index(request):
    return render(request, 'index.html')

def login(request):
    # Fetch all the religious sites from the database
    sites = Religious.objects.all()
    
    # Pass the data to the 'login.html' template using context dictionary
    return render(request, 'login.html', {'sites': sites})


def categories(request):
    return render(request, 'categories.html') 

def religious(request):
    return render(request, 'religious.html')

def itinerary_1(request):
    return render(request, 'itinerary_1.html')

def home(request):
    return render(request, 'home.html')

def search_cities(request):
    query = request.GET.get('q', '')

    if query:
        # Filter based on the 'city' field (instead of 'name')
        # Include both 'city' and 'site' fields in the response
        cities = Religious.objects.filter(city__icontains=query).values('city', 'site')

        # Return the matching cities and their associated sites as JSON
        return JsonResponse({'cities': list(cities)})
    else:
        return JsonResponse({'cities': []})



# Itinerary view
def itinerary_1(request):
    # Extract query parameters (passed from the form)
    destination = request.GET.get('destination', '')
    num_people = request.GET.get('numPeople', '')
    start_date = request.GET.get('startDate', '')
    end_date = request.GET.get('endDate', '')

    # If the destination contains parentheses (i.e., city and site)
    if '(' in destination and ')' in destination:
        # Split the city and site parts
        city, site_name = destination.split('(')
        site_name = site_name.rstrip(')')  # Remove the closing parenthesis
        city = city.strip()  # Remove any extra spaces
    else:
        city = destination
        site_name = None  # No site name in the query parameter

    # Do the database lookup for the city
    site = Religious.objects.filter(city__iexact=city, site__iexact=site_name).first()

    # Prepare context data
    context = {
        'destination': destination,
        'num_people': num_people,
        'start_date': start_date,
        'end_date': end_date,
        'city': city,
        'site_name': site_name,
    }

    # If the site was found, pass its details to the template
    if site:
        context.update({
            'site': site.site,
            'sites': site,  # Pass the whole site object to the template
            'description': site.description,  # Fetch description from DB
            'history': site.history,  # Fetch history from DB
        })
    else:
        context.update({
            'site': 'Unknown',
            'sites': None,
            'description': 'Description not available.',
            'history': 'History not available.',
        })

    # Render the 'itinerary_1.html' template and pass the context
    return render(request, 'itinerary_1.html', context)

# AI interaction endpoint
@csrf_exempt  # Disable CSRF for testing; secure in production
def chat_with_ai(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_input = data.get("message", "")

            if not user_input:
                return JsonResponse({"error": "No message provided"}, status=400)

            # Get AI response based on the user input
            response = model.generate_content(user_input)

            return JsonResponse({"response": response.text})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
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