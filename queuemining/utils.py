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


def submit_data(form, request):
    """A shortcut function, that submits the data from the DocumentForm to the system"""
    data_save = form.save()
    data_id = data_save.pk
    request.session['data_id'] = data_id
    submit_time(form, request)


def submit_time(form, request):
    """A shortcut function that saves an additional TimeStep"""
    time_frame = form.cleaned_data['timeframe']
    unit = form.cleaned_data['unit']
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    time_step = TimeStep.objects.create(timeframe=time_frame, unit=unit)
    data_object.timestep.add(time_step)


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


def delete_time(request, time_id):
    if request.method == 'POST':
        if is_time_available(request):
            delete_time_step = TimeStep.objects.get(id=time_id).delete()
            return render(request, 'table.html', {"data": delete_time_step})
    else:
        no_change = TimeStep.objects.get(id=time_id)
        return render(request, 'table.html', {"data": no_change})


def delete_time_all(request):
    if is_time_available(request):
        data_id = request.session['data_id']
        data_object = Data.objects.get(id=data_id)
        for time in data_object.timestep.all():
            time_id = time.id
            TimeStep.objects.get(id=time_id).delete()


def is_time_available(request):
    output = True
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    if len(data_object.timestep.all()) == 0:
        return False
    return output

