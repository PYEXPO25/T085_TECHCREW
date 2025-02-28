from django.db import models

class Religious(models.Model):
    # Column for city name
    city = models.CharField(max_length=255)
    
    # Column for site name
    site = models.CharField(max_length=255)
    
    # Column for a description of the site
    description = models.TextField()
    
    # Column for the historical information
    history = models.TextField()
    
    # A string representation of the model (for admin display and debugging)
    def __str__(self):
        return f"{self.city} - {self.site}"