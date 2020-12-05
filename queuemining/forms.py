from django import forms
from .models import Table


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('document', )


class SelectionForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('timeframe', 'unit',)

    UNIT_CHOICES = (
        ("N", "---"),
        ("H", "Hour"),
        ("D", "Day"),
        ("W", "Week"),
        ("M", "Month")
    )
    unit = forms.ChoiceField(label='unit', choices=UNIT_CHOICES)