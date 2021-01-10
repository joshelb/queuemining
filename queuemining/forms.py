from django import forms
from .models import Data, TimeStep


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
    timeframe = forms.IntegerField(initial=1)
    unit = forms.ChoiceField(label='unit', choices=UNIT_CHOICES)


class TimeForm(forms.ModelForm):
    class Meta:
        model = TimeStep
        fields = ('timeframe', 'unit', )
    UNIT_CHOICES = (
        ("N", "---"),
        ("H", "Hour"),
        ("D", "Day"),
        ("W", "Week"),
        ("M", "Month")
    )
    timeframe = forms.IntegerField(initial=1)
    unit = forms.ChoiceField(label='unit', choices=UNIT_CHOICES)


class CurrentForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('timestep', )
    timestep = forms.ModelChoiceField(
        queryset=Data.objects.latest('uploaded_at').timestep.all(),
        required=False, empty_label="---", label='Current')