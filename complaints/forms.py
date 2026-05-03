"""
complaints/forms.py
───────────────────
Forms for:
  • ComplaintForm   — citizen submits a complaint
  • StatusUpdateForm — admin changes status and assigns department
"""

from django import forms
from .models import Complaint, Category, Department


class ComplaintForm(forms.ModelForm):
    location_text = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter address or click map to auto-fill',
            'id': 'location_text',
        }),
        label='Location Address'
    )
    latitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'latitude'}),
    )
    longitude = forms.DecimalField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'longitude'}),
    )

    class Meta:
        model  = Complaint
        fields = [
            'title', 'description', 'category',
            'location_text', 'latitude', 'longitude',
            'image',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Short title of the issue (e.g. Garbage overflow on MG Road)',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue in detail...',
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.all()
        self.fields['image'].required = False


class StatusUpdateForm(forms.ModelForm):
    """Admin form: update status, assign department, add notes."""

    class Meta:
        model  = Complaint
        fields = ['status', 'department', 'admin_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'admin_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional internal notes...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all()
        self.fields['department'].required = False


class ComplaintFilterForm(forms.Form):
    """Admin filter bar for complaint list."""
    category   = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    status     = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Complaint.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    search     = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search by ID, title, location…',
        }),
    )
