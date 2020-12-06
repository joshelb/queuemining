
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

def view_table(request):
    csv_fp = open(os.path.join(settings.BASE_DIR, 'test_csv.csv'))
    reader = csv.DictReader(csv_fp, delimiter=",")
    fieldnames = [i for i in reader.fieldnames]
    data = [i for i in reader]
    context = {'data': data, 'fields': fieldnames}
    return render(request, 'table_2.html', context)


def get_data(request):
    """Get data is the view used to manage the upload of the event log,
     as well as of the user setting the time window. In our current version,
     we require the user to provide both inputs at the same time,
     otherwise the data is not submitted."""
    random.seed(10)
    context = {}
    if request.method == 'POST':
        data_form = forms.DataForm(request.POST, request.FILES)
        if utils.data_valid(data_form):
            utils.submit_data(data_form)
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

