from django.http import HttpResponse
from .forms import DataForm
from .models import Data, TimeStep
from django.shortcuts import render


def data_valid(form):
    """A shortcut function, that returns true, if the SelectionForm and DocForm are valid and the selection
    given by the user is usable (ergo the timeframe is greater than 0 and a unit was selected) """
    output = False
    if form.is_valid() and not form.cleaned_data['unit'] == "N" and form.cleaned_data['timeframe'] > 0:
        output = True
    return output


def hours_valid(form):
    output = False
    if form.is_valid() and form.cleaned_data['day_start'] < form.cleaned_data['day_end']\
            and 0 <= form.cleaned_data['day_start'] <= 24\
            and 0 <= form.cleaned_data['day_end'] <= 24\
            and len(form.cleaned_data['weekends']) < 7:
        output = True
    return output


def submit_data(form, request):
    """A shortcut function, that submits the data from the DocumentForm to the system"""
    data_save = form.save()
    data_id = data_save.pk
    request.session['data_id'] = data_id
    submit_time(form, request)


def submit_time(form, request):
    """A shortcut function that saves an additional TimeStep and saves it converted into
    hours in the 'current' attribute of the data object"""
    time_frame = form.cleaned_data['timeframe']
    unit = form.cleaned_data['unit']
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    time_step = TimeStep.objects.create(timeframe=time_frame, unit=unit)
    data_object.timestep.add(time_step)
    data_object.save()
    current_time = time_convert(time_frame, unit)
    request.session['current_time'] = current_time
    request.session['cur_timestep'] = time_step.id


def submit_current(form, request):
    time_step = form.cleaned_data['timestep']
    set_current_time(request, time_step)


def set_current_time(request, timestep):
    """A shortcut function that returns the current attribute from the data object"""
    time_frame = timestep.timeframe
    unit = timestep.unit
    current_time = time_convert(time_frame, unit)
    request.session['cur_timestep'] = timestep.id
    request.session['current_time'] = current_time


def get_current_time(request):
    """A shortcut function that returns the current attribute from the data object"""
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    return data_object.current


def time_convert(timeframe, unit):
    """A shortcut function that converts a timestep to hours"""
    if unit == "H":
        output = timeframe
    elif unit == "D":
        output = timeframe * 24
    elif unit == "W":
        output = timeframe * 168
    elif unit == "M":
        output = timeframe * 720
    return output


def time_used(form, request):
    """A shortcut function, used to check if a timestep was already submitted"""
    output = False
    time_frame = form.cleaned_data['timeframe']
    unit = form.cleaned_data['unit']
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    for time in data_object.timestep.all():
        if time.timeframe == time_frame and time.unit == unit:
            output = True
    return output


def delete_time(request):
    if is_time_available(request):
        time_id = request.session['cur_timestep']
        timestep = TimeStep.objects.get(id=time_id)
        timestep.delete()
        if is_time_available(request):
            time_last = TimeStep.objects.latest('id')
            set_current_time(request, time_last)
        else:
            request.session['cur_timestep'] = None
            request.session['current_time'] = None
        output = True
    else:
        output = False
    return output


def delete_time_all(request):
    if is_time_available(request):
        data_id = request.session['data_id']
        data_object = Data.objects.get(id=data_id)
        for time in data_object.timestep.all():
            time_id = time.id
            TimeStep.objects.get(id=time_id).delete()
        request.session['cur_timestep'] = None
        request.session['current_time'] = None
        output = True
    else:
        output = False
    return output


def is_time_available(request):
    output = True
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    if len(data_object.timestep.all()) == 0:
        return False
    return output
