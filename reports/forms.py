from django import forms
from .models import Report, Category


class ReportForm(forms.ModelForm):
    """Form for creating and editing reports (both lost and found items)."""
    
    class Meta:
        model = Report
        fields = [
            "title",
            "description",
            "category",
            "location",
            "event_date",
            "image",
            "contact_info"
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Item name or brief description"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Provide details about the item (color, brand, size, etc.)"
            }),
            "category": forms.Select(attrs={
                "class": "form-control"
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Where was it lost/found? (e.g., Library Building, Near Cafeteria)"
            }),
            "event_date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "image": forms.FileInput(attrs={
                "class": "form-control",
                "accept": "image/*"
            }),
            "contact_info": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone or email (optional)"
            }),
        }
