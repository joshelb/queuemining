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
