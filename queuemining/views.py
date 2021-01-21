from django.shortcuts import render
import random
from django.http import HttpResponse
from . import forms
from django.template import loader
from . import utils
import matplotlib.pyplot as plt
import csv
import os
from django.conf import settings


def get_data(request):
    """Get data is the view used to manage the upload of the event log,
     as well as all of the data needed for our calculations."""
    random.seed(10)
    context = {}
    if request.method == 'POST':
        data_form = forms.DataForm(request.POST, request.FILES)
        if utils.data_valid(data_form) and utils.hours_valid(data_form):
            utils.submit_data(data_form, request)
            text = "Thank you for your upload!"
        else:
            data_form = forms.DataForm()
            text = "Your input was not usable by the system. Please redo!"
        context['text'] = text
    else:
        data_form = forms.DataForm()
        context['text'] = "Please enter the respective data into the sidebar!"
        utils.wipe_data(request)
    context['data_form'] = data_form
    template = loader.get_template('main.html')
    return HttpResponse(template.render(context, request))


def view_table(request):
    """View table is the view used to manage the creation and visualization of tables for each timestep."""
    context = {}
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
    if not request.session['current_time'] is None:
        df = utils.show_dataframe(request.session['cur_timestep'])
        table_data = df.to_html()
    else:
        table_data = "<p>Please submit a timestep</p>"
    context['table_data'] = table_data
    context['time_form'] = time_form
    context['current_form'] = current_form
    return render(request, 'table.html', context)


def view_analysis(request):
    """This view handles the displaying of the analysed data, being the best timestep aswell as data on
    the utilization rates and queue lengths"""
    context = {}
    best_id = utils.compare(request)
    best_time_step = utils.get_timestep(best_id)
    utils.set_current_time(request, best_time_step)
    df = utils.show_dataframe(best_id)
    result = utils.get_plot_data(request)
    image = str(request.session['data_id'])+".png"
    table_data = df.to_html()
    context["idimage"] = image
    context['table_data'] = table_data
    context['timestep'] = best_time_step.__str__()
    return render(request, 'detail.html', context)

