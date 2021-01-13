from django.shortcuts import render
import random
from django.http import HttpResponse
from . import forms
from . import models
from django.template import loader
from . import utils
import csv
import os
from django.conf import settings


def get_data(request):
    """Get data is the view used to manage the upload of the event log,
     as well as of the user setting the time window. In our current version,
     we require the user to provide both inputs at the same time,
     otherwise the data is not submitted."""
    random.seed(10)
    context = {}
    if request.method == 'POST':
        data_form = forms.DataForm(request.POST, request.FILES)
        if utils.data_valid(data_form) and utils.hours_valid(data_form):
            utils.submit_data(data_form, request)
            text = "Thank you for your upload!"
        else:
            data_form = forms.DataForm()
            text = "Your uploaded file and/or the selected timeframe \n " \
                   "were not submitted in a way usable by the system. Please redo!"
        context['text'] = text
    else:
        data_form = forms.DataForm()
    context['data_form'] = data_form
    template = loader.get_template('main.html')
    return HttpResponse(template.render(context, request))


def view_table(request):
    """ This view gets a .csv formatted file (currently in base dir of the project)
        and creates the table specified in the assignment pdf.
        The input will come from the processmining module where the information will be extracted from the event logs.
        When that functionality is added it will take .csv formatted tables directly from there."""
    csv_fp = open(os.path.join(settings.BASE_DIR, 'test_csv.csv'))
    reader = csv.DictReader(csv_fp, delimiter=",")
    table_data = [i for i in reader]
    context = {'table_data': table_data}
    if request.method == 'POST':
        time_form = forms.TimeForm(request.POST)
        current_form = forms.CurrentForm(request, request.POST)
        if 'time_submit' in time_form.data:
            if utils.data_valid(time_form):
                if not utils.time_used(time_form, request):
                    utils.submit_time(time_form, request)
                    time_text = "Thank you for your upload!"
                else:
                    time_text = "This timeframe was already used!"
            else:
                time_form = forms.TimeForm()
                time_text = "Your timeframe wasn't submittable"
            context['time_text'] = time_text
        elif 'time_delete_all' in time_form.data:
            time_form = forms.TimeForm()
            if utils.delete_time_all(request):
                delete_text = "All timesteps have been deleted!"
            else:
                delete_text = "There are no timesteps to delete!"
            context['delete_text'] = delete_text
        elif 'time_delete' in time_form.data:
            time_form = forms.TimeForm()
            if utils.delete_time(request):
                delete_text = "The current timestep has been deleted!"
            else:
                delete_text = "There are no timesteps to delete!"
            context['delete_text'] = delete_text
        if current_form.is_valid() and not current_form.cleaned_data['timestep'] is None:
            utils.submit_current(current_form, request)
    else:
        time_form = forms.TimeForm()
        current_form = forms.CurrentForm(request)
    context['time_form'] = time_form
    context['current_form'] = current_form
    return render(request, 'table.html', context)

