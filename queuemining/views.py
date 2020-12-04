from django.shortcuts import render
import random
from django.http import HttpResponse
from . import forms
from . import models
from django.template import loader
from . import utils


def get_data(request):
    """Get data is the view used to manage the upload of the event log,
     as well as of the user setting the time window. In our current version,
     we require the user to provide both inputs at the same time,
     otherwise the data is not submitted."""
    random.seed(10)
    context = {}
    if request.method == 'POST':
        doc_form = forms.DocumentForm(request.POST, request.FILES)
        time_form = forms.SelectionForm(request.POST)
        if doc_form.is_valid() and utils.selection_valid(time_form):
            utils.submit_document(doc_form)
            utils.submit_timeframe(time_form)
            text = "Thank you for your upload!"
        elif utils.selection_valid(time_form) and not doc_form.is_valid():
            doc_form = forms.DocumentForm()
            text = "Please upload an event log with your timeframe! \n " \
                   "Note that the use of a CSV or XES file is mandatory."
        elif doc_form.is_valid() and not utils.selection_valid(time_form):
            time_form = forms.SelectionForm()
            text = "Please submit your desired timeframe with your event log!"
        else:
            doc_form = forms.DocumentForm()
            time_form = forms.SelectionForm()
            text = "Your uploaded file as well as the selected timeframe \n " \
                   "were not submitted in a way usable by the system. Please redo!"
        context['text'] = text
    else:
        doc_form = forms.DocumentForm()
        time_form = forms.SelectionForm()
    context['doc_form'] = doc_form
    context['time_form'] = time_form
    template = loader.get_template('main.html')
    return HttpResponse(template.render(context, request))


# def create_table():
