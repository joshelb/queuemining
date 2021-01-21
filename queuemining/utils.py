from django.http import HttpResponse
from .forms import DataForm
from .models import Data, TimeStep, DataFrame
from django.shortcuts import render
from operator import itemgetter
from queuemining.processmining.main import run as create_df
import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import os.path
import os


"""Shortcut functions"""


def data_valid(form):
    """A shortcut function, that returns true, if the SelectionForm and DocForm are valid and the selection
    given by the user is usable (ergo the timeframe is greater than 0 and a unit was selected) """
    output = False
    if form.is_valid() and not form.cleaned_data['unit'] == "N" and form.cleaned_data['timeframe'] > 0:
        output = True
    return output


def hours_valid(form):
    """Shows if the submitted business hours are valid"""
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


def get_timestep(time_id):
    return TimeStep.objects.get(id=time_id)


def set_current_time(request, timestep):
    time_frame = timestep.timeframe
    unit = timestep.unit
    current_time = time_convert(time_frame, unit)
    request.session['cur_timestep'] = timestep.id
    request.session['current_time'] = current_time


def get_current_time(request):
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


def is_time_available(request):
    """A shortcut function used to check, if there are any timesteps left"""
    output = True
    data_id = request.session['data_id']
    data_object = Data.objects.get(id=data_id)
    if len(data_object.timestep.all()) == 0:
        return False
    return output


"""Data Submittion"""


def submit_data(form, request):
    """A shortcut function, that submits the data from the DocumentForm to the system"""
    data_save = form.save()
    data_id = data_save.pk
    request.session['data_id'] = data_id
    submit_time(form, request)


def submit_time(form, request):
    """A shortcut function that saves a TimeStep and all associated data"""
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
    submit_dataframe(request, time_step)


def submit_current(form, request):
    time_step = form.cleaned_data['timestep']
    set_current_time(request, time_step)


"""Deletion"""


def delete_time(request):
    """Deletes the current timestep"""
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
    """Deletes all timesteps"""
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


def wipe_data(request):
    try:
        if not request.session['data_id'] is None:
            data_object = get_data(request)
            delete_time_all(request)
            if os.path.exists("queuemining/static/queuemining/images/"+str(request.session['data_id'])+'.png'):
                os.remove("queuemining/static/queuemining/images/"+str(request.session['data_id'])+'.png')
            if os.path.exists("media/" + str(data_object.document)):
                os.remove("media/" + str(data_object.document))
            data_object.delete()
            request.session['data_id'] = None
    except KeyError:
        pass


"""Dataframe"""


def create_dataframe(request):
    """Creates a dataframe based on the users data"""
    data = get_data(request)
    df = create_df("media/" + str(data.document), request.session['current_time'], data.day_start, data.day_end,
                   data.offdays)
    return df


def submit_dataframe(request, timestep):
    """Saves a dataframe to the backend"""
    df = create_dataframe(request)
    i = 0
    for index, row in df.iterrows():
        act_id = i
        cases = float(row["Cases in the queue"])
        cases = round(cases, 5)
        act = row["activity_name"]
        ser_time = float(row["Average Service Time"])
        ser_time = round(ser_time, 5)
        wait_time = float(row["Average Waiting Time"])
        wait_time = round(wait_time, 5)
        res_nr = float(row["Number of resources"])
        res_nr = round(res_nr, 5)
        capacity = float(row["Capacity of teh activity"])
        capacity = round(capacity, 5)
        i +=1
        frame = DataFrame.objects.create(
            act_id=act_id,
            case_amount=cases,
            act_name=act,
            service_time=ser_time,
            waiting_time=wait_time,
            res_nr=res_nr,
            capacity=capacity
        )
        timestep.frame.add(frame)


def show_dataframe(time_id):
    """Transforms the data of the DataFrame Model objects associated with a certain
    timestep into a dataframe and displays it"""
    timestep = get_timestep(time_id)
    output = pd.DataFrame(columns=["Cases in the queue", "Activity name",
                                   "Average service time", "Average waiting time",
                                   "Number of resources", "Capacity of the activity"] )
    for row in timestep.frame.all().order_by('act_id'):
        cases = row.case_amount
        act = row.act_name
        ser_time = row.service_time
        wait_time = row.waiting_time
        res_nr = row.res_nr
        capacity = row.capacity
        new_row = pd.Series(data={'Cases in the queue': cases,
                                  'Activity name': act,
                                  'Average service time': ser_time,
                                  'Average waiting time': wait_time,
                                  'Number of resources': res_nr,
                                  'Capacity of the activity': capacity})
        output = output.append(new_row, ignore_index=True)
    return output


"""Analysis"""


def analyse_get_data(df, timeframe,timeframestring):
    """Creates a dataframe containing relevant information to the analysis"""
    output = pd.DataFrame(columns=["Activity name", "Utilization rate", "Queue length", "Timeframe"])
    for index, row in df.iterrows():
        act = row["Activity name"]
        if not row["Average service time"] == 0:
            util = float(row["Cases in the queue"]) / (timedelta(hours=timeframe).total_seconds()/(float(row["Average service time"]*row["Capacity of the activity"])))
        else:
            util = 0
        lil = int(row["Cases in the queue"]*row["Average waiting time"])
        new_row = pd.Series(data={'Activity name': act, 'Utilization rate': util, 'Queue length': lil,'Timeframe': timeframestring})
        output = output.append(new_row, ignore_index=True)
    return output


def timestep_data(df, timeframe):
    """Adds up all the utilization rates and queue lengths from the before created dataframe,
     so that it is possible to compare based on the whole timestep, not just the single activities"""
    data = analyse_get_data(df, timeframe,timeframe)
    util = 0
    lil = 0
    for index, row in data.iterrows():
        util += row["Utilization rate"]
        lil += row["Queue length"]
    if util == 0:
        util = None
    return util, lil


def compare(request):
    """Compares the summed up utilization rates and queue lengths of all timesteps, to determine,
    which timestep is the best."""
    util_list = []
    lil_list = []
    data = get_data(request)
    for time in data.timestep.all():
        time_frame = time.timeframe
        unit = time.unit
        time_id = time.id
        dur = time_convert(time_frame, unit)
        df = show_dataframe(time_id)
        util, lil = timestep_data(df, dur)
        if not util is None:
            util_list.append((time_id, util))
        lil_list.append((time_id, lil))
    if len(util_list) == 0:
        util_list.sort(key=itemgetter(1), reverse=True)
    lil_list.sort(key=itemgetter(1), reverse=False)
    result_list = []
    util_pos = 0
    lil_pos = 0
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


"""Plotting"""


def get_plot_data(request):
    """Returns a list of dataframes containing data used for plots displayed on the analysis page"""
    data_object = get_data(request)
    output = []
    for time in data_object.timestep.all():
        df = show_dataframe(time.id)
        time_frame = time.timeframe
        unit = time.unit
        dur = time_convert(time_frame, unit)
        data = analyse_get_data(df, dur, str(time_frame) + " " + str(unit))
        output.append(data)
    plotting(output, request)
    return output


def plotting(dataframe_list, request):
    fig, (ax1, ax2) = plt.subplots(1, 2)
    for frame in dataframe_list:
        ax1.plot(frame["Activity name"].tolist(), frame['Utilization rate'].tolist(), label=frame["Timeframe"][0])
        ax2.plot(frame["Activity name"].tolist(), frame['Queue length'].tolist(), label=frame["Timeframe"][0])
    ax1.tick_params(labelrotation=90)
    ax2.tick_params(labelrotation=90)
    plt.legend()
    plt.tight_layout()
    plt.savefig("queuemining/static/queuemining/images/"+str(request.session['data_id'])+'.png')
