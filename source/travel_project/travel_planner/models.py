from django.db import models

class Religious(models.Model):
    city = models.CharField(max_length=100)
    sites = models.CharField(max_length=200)
    description = models.TextField()
    history = models.TextField()

    def __str__(self):
        return self.city
    
from django.db import models

class Leisure(models.Model):
    city = models.CharField(max_length=100)
    sites = models.CharField(max_length=200)
    description = models.TextField()
    popularity = models.TextField()

    def __str__(self):
        return self.city