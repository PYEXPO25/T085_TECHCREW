from django import forms
from .models import Itinerary

class ItineraryPreferencesForm(forms.ModelForm):
    INTEREST_CHOICES = [
        ('culture', 'Cultural Experiences'),
        ('adventure', 'Adventure Activities'),
        ('relaxation', 'Relaxation'),
        ('food', 'Food & Cuisine'),
        ('nature', 'Nature & Outdoors')
    ]
    
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )
    
    pace_preference = forms.ChoiceField(
        choices=[
            ('relaxed', 'Relaxed'),
            ('moderate', 'Moderate'),
            ('intense', 'Intense')
        ]
    )

    class Meta:
        model = Itinerary
        fields = ['start_date', 'end_date', 'budget']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'budget': forms.NumberInput(attrs={'min': '0', 'step': '100'})
        }