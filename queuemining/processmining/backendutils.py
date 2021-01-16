import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
import pandas as pd
from pm4py.statistics.traces.log import case_arrival
from pm4py.algo.filtering.log.timestamp import timestamp_filter
import math
from datetime import timedelta
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.objects.petri import performance_map
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pm4py.statistics.concurrent_activities.log import get as conc_act_get
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.statistics.performance_spectrum import algorithm as performance_spectrum

pd.set_option("display.max_rows", None, "display.max_columns", None)

def eventDataFrameSorted(log):
    event_stream = pm4py.convert_to_event_stream(log)
    dataframe = pm4py.convert_to_dataframe(log)
    colums = ["Cases in the queue","activity_name","Average Service Time","Average Waiting Time","Number of resources","Capacity of teh activity"]
    df = pd.DataFrame(columns=colums)
    try:
        activities = dataframe['concept:name'].unique().tolist()
    except KeyError:
        activities = []
    try:
        tree = inductive_miner.apply_tree(log)
        net, initial_marking, final_marking = pt_converter.apply(tree, variant=pt_converter.Variants.TO_PETRI_NET)
        traces = performance_map.get_transition_performance_with_token_replay(log, net, initial_marking,final_marking)
    except:
        traces = []

    for i in activities:
        try:
            count = len(dataframe[dataframe["concept:name"] == i].index)
            average_service_time = int(dataframe[dataframe["concept:name"] == i].sum(axis=0,skipna=True)["@@duration"]/count)
            capacity_list = conc_act_get.apply(log, parameters={conc_act_get.Parameters.TIMESTAMP_KEY: "time:timestamp",
                                                           conc_act_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})
            capacity = 0
            for item in capacity_list:
                if item == "("+"'"+i+"', '"+i+"'"+")":
                    capacity +=1
                else:
                    capacity = 1

            try:
                average_waiting_time = np.average(traces[i]['all_values'])
            except:
                average_waiting_time = 0

        except:
            average_service_time = 0
            waiting_list = []
            dff = dataframe
            dff = dff.sort_values(by=['time:timestamp'])
            dff =dff.reset_index(drop=True)

            for index,row in dff.iterrows():
                if index == 0 and dff._get_value(index,'concept:name') == i:
                    waiting_list.append(0)

                if index >0 and dff._get_value(index,'concept:name') == i:
                    old = dff._get_value(index-1,'time:timestamp')
                    waiting_list.append((dff._get_value(index,'time:timestamp')-old).total_seconds())

            if len(waiting_list) == 0:
                average_waiting_time = 0

            else:
                average_waiting_time = np.average(waiting_list)

            dff = dff[dff["concept:name"] == i]
            dff = dff.sort_values(by=['time:timestamp'])
            dff = dff.reset_index(drop=True)
            capacity = 0
            for index,row in dff.iterrows():

                if index >0 and dff._get_value(index, 'time:timestamp') == dff._get_value(index-1, 'time:timestamp'):
                    capacity += 1

        resource_count = len(dataframe[dataframe["concept:name"] == i]["org:resource"].unique().tolist())
        case_count = len(dataframe[dataframe["concept:name"] == i]["case:concept:name"].unique().tolist())
        new_row = pd.Series(data={'Cases in the queue' : case_count,'activity_name': i,'Average Service Time': average_service_time, 'Average Waiting Time' : average_waiting_time,
                                  'Number of resources': resource_count,"Capacity of teh activity":capacity})
        df = df.append(new_row, ignore_index=True)

    if df.empty:
        return None
    return df





def timerangehours(start_date, end_date,timestep):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


def timerangebigger(start_date,end_date,timestep):
    fraction = int(timestep/24)+1
    for n in range(int(math.ceil(int((end_date - start_date).days)/fraction)+1)):
        yield start_date + timedelta(n*fraction)


def timesplittingbigger(log,rangestart,rangeend,timestep,businesshooursstart,businesshoursend, weekend_list):
    dataframe_list = []
    for single_step in timerangebigger(rangestart, rangeend, timestep):
        single_step = single_step - timedelta(minutes=1)
        filtered_log_events = timestamp_filter.apply_events(log, single_step.strftime("%Y-%m-%d %H:%M:%S"), (single_step + timedelta(hours=timestep)).strftime("%Y-%m-%d %H:%M:%S"))
        data = eventDataFrameSorted(filtered_log_events)
        dataframe_list.append(data)


        fractions = timestep/24
        rest = timestep%24
        st = (single_step + timedelta(hours=timestep)).strftime("%Y-%m-%d %H:%M:%S")
        end = (single_step + timedelta(hours=timestep + rest)).strftime("%Y-%m-%d %H:%M:%S")
        filtered_log_events = timestamp_filter.apply_events(log, st, end)
        data2 = eventDataFrameSorted(filtered_log_events)
        dataframe_list.append(data2)




    return dataframe_list


def timesplittinghours(log,rangestart,rangeend,timestep,businesshooursstart,businesshoursend, weekend_list):
    dataframe_list = []
    for single_step in timerangehours(rangestart, rangeend,timestep):
        single_step = single_step.replace(hour= businesshooursstart,minute= 0,second=0,microsecond=0) - timedelta(minutes=1)
        if businesshoursend-businesshooursstart <= timestep:
            filtered_log_events = timestamp_filter.apply_events(log, single_step.strftime("%Y-%m-%d %H:%M:%S"), (single_step+timedelta(hours=businesshoursend-businesshooursstart)).strftime("%Y-%m-%d %H:%M:%S"))
            data = eventDataFrameSorted(filtered_log_events)
            dataframe_list.append(data)
        else:
            fractions = int((businesshoursend-businesshooursstart)/timestep)
            rest = (businesshoursend-businesshooursstart)%timestep


            for item in range(0,fractions):
                filtered_log_events = timestamp_filter.apply_events(log, (single_step+timedelta(hours=item*timestep)).strftime("%Y-%m-%d %H:%M:%S"),
                                                                (single_step+timedelta(hours=item*timestep + timestep)).strftime(
                                                                    "%Y-%m-%d %H:%M:%S"))
                data = eventDataFrameSorted(filtered_log_events)
                dataframe_list.append(data)

            st = (single_step + timedelta(hours=fractions * timestep)).strftime("%Y-%m-%d %H:%M:%S")
            end = (single_step + timedelta(hours=fractions * timestep + rest)).strftime("%Y-%m-%d %H:%M:%S")
            filtered_log_events = timestamp_filter.apply_events(log, st,end)
            data2 = eventDataFrameSorted(filtered_log_events)
            dataframe_list.append(data2)



    return dataframe_list










def filtertimerange(log):
    old = log[0][0]["time:timestamp"]
    new = None
    old2 = old
    new2 = None
    for trace  in log:
        for event in trace:
            new = event["time:timestamp"]
            new2 = new
            if new < old:
                old = new
            elif new2 > old2:

                old2 = new2

    return old, old2





def calculateAverageoftimestep(dataframe_list,log):
    cases_in_queue = []
    average_service_time = []
    average_waiting_time = []
    number_of_resources = []
    capacity_of_activity = []

    activities = attributes_filter.get_attribute_values(log, "concept:name")
    colums = ["Cases in the queue","activity_name","Average Service Time","Average Waiting Time","Number of resources","Capacity of teh activity"]
    df = pd.DataFrame(columns=colums)
    for activity in activities:
        for frame in dataframe_list:
            try:

                dataframe_filtered = frame[frame["activity_name"] == activity]
                dataframe_filtered = dataframe_filtered.reset_index(drop=True)
                cases_in_queue.append(dataframe_filtered.iloc[0][0])
                average_service_time.append(dataframe_filtered.iloc[0][2])
                average_waiting_time.append(dataframe_filtered.iloc[0][3])
                number_of_resources.append(dataframe_filtered.iloc[0][4])
                capacity_of_activity.append(dataframe_filtered.iloc[0][5])


            except:
                pass
        new_row = pd.Series(
            data={'Cases in the queue': np.average(cases_in_queue), 'activity_name': activity, 'Average Service Time': np.average(average_service_time),
                    'Average Waiting Time': np.average(average_waiting_time),
              'Number of resources': np.average(number_of_resources), "Capacity of teh activity": np.average(capacity_of_activity)})

        df = df.append(new_row, ignore_index=True)




    return df









