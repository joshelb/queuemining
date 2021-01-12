from django import forms
from .models import Data, TimeStep


class DataForm(forms.ModelForm):
    class Meta:
        model = Data
        fields = ('document', 'timeframe', 'unit', 'weekends', 'day_start', 'day_end')
    UNIT_CHOICES = (
            ("N", "---"),
            ("H", "Hour"),
            ("D", "Day"),
            ("W", "Week"),
            ("M", "Month")
    )
    DAY_CHOICES = (
            ("1", "Monday"),
            ("2", "Tuesday"),
            ("3", "Wednesday"),
            ("4", "Thursday"),
            ("5", "Friday"),
            ("6", "Saturday"),
            ("7", "Sunday"),
    )
    timeframe = forms.IntegerField(initial=1)
    unit = forms.ChoiceField(label='unit', choices=UNIT_CHOICES)
    weekends = forms.MultipleChoiceField(choices=DAY_CHOICES, widget=forms.CheckboxSelectMultiple)
    day_start = forms.IntegerField(initial=9)
    day_end = forms.IntegerField(initial=17)


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


class CurrentForm(forms.Form):
    timestep = forms.ModelChoiceField(
        queryset=None,
        required=False, empty_label="---", label='Current')

    def __init__(self, request, *args, **kwargs):
        super(CurrentForm, self).__init__(*args, **kwargs)
        if not request is None:
            data_id = request.session['data_id']
            query = Data.objects.get(id=data_id).timestep.all()
            self.fields['timestep'].queryset = query
            self.fields['timestep'].widget.choices = self.fields['timestep'].choices
