from django.http import HttpResponse
from .forms import DataForm
from .models import Data, TimeStep
from django.shortcuts import render
from operator import itemgetter
from queuemining.processmining.main import run as create_df


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
            and len(form.cleaned_data['offdays']) < 7:
        output = True
    return output


def get_data(request):
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    return data_object


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


def create_dataframe(request):
    data = get_data(request)
    df = create_df("media/" + str(data.document), request.session['current_time'], data.day_start, data.day_end,
              data.offdays, data.start_name, data.end_name)
    return df


def analyse_get_data(df, timeframe):
    output = pd.DataFrame(columms=["Activity name", "Utilization rate", "Queue length"])
    for index, row in df.iterrows:
        act = row["activity_name"]
        util = int(row["Cases in the queue"] / (timedelta(hours=timeframe).total_seconds()/(row["Average Service Time"]*row["Capacity of teh activity"])))
        lil = int(row["Cases in the queue"]*row["Average Waiting Time"])
        new_row = pd.Series(data={'Activity name': act, 'Utilization rate': util, 'Queue length': lil})
        output = output.append(new_row, ignore_index=True)
    return output


def timestep_data(df, timeframe):
    data = analyse_get_data(df, timeframe)
    util = 0
    lil = 0
    for index, row in data.iterrows:
        util += row["Utilization rate"]
        lil += row["Queue length"]
    return util, lil


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


def compare(df, data):
    util_list = [()]
    lil_list = [()]
    for time in data.timestep.all():
        time_frame = time.timeframe
        unit = time.unit
        time_id = time.id
        dur = time_convert(time_frame, unit)
        util, lil = timestep_data(df, dur)
        util_list.append((time_id, util))
        lil_list.append((time_id, lil))
    util_list.sort(key=itemgetter(1), reverse=True)
    lil_list.sort(key=itemgetter(1), reverse=False)
    result_list = []
    for time in data.timestep.all():
        time_id_2 = time.id
        i = 0
        for util_2 in util_list:
            if time_id_2 is util_2[0]:
                util_pos = i
            i += 1
        j = 0
        for lil_2 in lil_list:
            if time_id_2 is lil_2[0]:
                lil_pos = j
            j += 1
        result_list.append((time_id_2, (util_pos+lil_pos)))
    result_list.sort(key=itemgetter(1), reverse=False)
    best_time_id = result_list[0][0]
    return best_time_id

