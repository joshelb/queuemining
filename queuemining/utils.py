from django.http import HttpResponse
from . import forms
from . import models


def data_valid(form):
    """A shortcut function, that returns true, if the SelectionForm is valid and the selection
    given by the user is usable (ergo the timeframe is greater than 0 and a unit was selected) """
    output = False
    if form.is_valid() and not form.cleaned_data['unit'] == "N" and form.cleaned_data['timeframe'] > 0:
        output = True
    return output


def submit_data(form, request):
    """A shortcut function, that submits the data from the DocumentForm to the system"""
    doc_name = form.cleaned_data['document']
    request.session['document'] = doc_name
    print(str(doc_name))
    time_frame = form.cleaned_data['timeframe']
    request.session['timeframe'] = time_frame
    unit = form.cleaned_data['unit']
    request.session['unit'] = unit
    print(str(time_frame) + str(unit))
    data_save = form.save()
    id = data_save.pk
    print(id)
