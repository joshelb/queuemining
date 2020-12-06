from django import forms
from .models import Data


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('document', 'timeframe', 'unit', )
    UNIT_CHOICES = (
            ("N", "---"),
            ("H", "Hour"),
            ("D", "Day"),
            ("W", "Week"),
            ("M", "Month")
    )
    unit = forms.ChoiceField(label='unit', choices=UNIT_CHOICES)
