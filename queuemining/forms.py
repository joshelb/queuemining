from django import forms
from .models import Table


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ('document', )


class SelectionForm(forms.Form):
    class Meta:
        model = Table
    UNIT_CHOICES = (
        ("N", "---"),
        ("H", "Hour"),
        ("D", "Day"),
        ("W", "Week"),
        ("M", "Month")
    )
    timeframe = forms.IntegerField(label='timeframe', initial = 1)
    unit = forms.ChoiceField(label='unit', choices = UNIT_CHOICES)
