from django.contrib import admin
from .models import Religious  # Correctly import the Religious model

# Register your models here.
admin.site.register(Religious)  # Register the Religious model with Django admin