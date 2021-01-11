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

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CurrentForm, self).__init__(*args, **kwargs)
        if not self.request is None:
            data_id = self.request['data_id']
            query = Data.objects.get(id=data_id).timestep.all()
            self.fields['timestep'].evaluated_queryset = query
