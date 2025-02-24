from django.db import models
from django.contrib.auth.models import User

class Destination(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    typical_cost = models.DecimalField(max_digits=10, decimal_places=2)
    recommended_days = models.IntegerField()
    best_season = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in hours")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} at {self.destination.name}"

class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    destinations = models.ManyToManyField(Destination)
    activities = models.ManyToManyField(Activity, through='ItineraryActivity')
    created_at = models.DateTimeField(auto_now_add=True)

class ItineraryActivity(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    day = models.IntegerField()
    time_slot = models.TimeField()
