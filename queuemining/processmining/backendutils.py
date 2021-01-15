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

pd.set_option("display.max_rows", None, "display.max_columns", None)

def eventDataFrameSorted(log):
    dataframe_list = []
    event_stream = pm4py.convert_to_event_stream(log)
    dataframe = pm4py.convert_to_dataframe(log)
    colums = ["trace_name","activity_name","Average Service Time","Average Waiting Time","Number of resources","Capacity of teh activity"]
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
        pass

    for i in activities:
        try:
            capacity =conc_act_get.apply(log, parameters={conc_act_get.Parameters.TIMESTAMP_KEY: "time:timestamp", conc_act_get.Parameters.START_TIMESTAMP_KEY: "start_timestamp"})
            for item in capacity:
                if i == "("+"'"+i+"', '"+i+"'"+")":
                    capacity = capacity[i]
                else:
                    capacity = 1
            resource_count = len(dataframe[dataframe["concept:name"] == i]["org:resource"].unique().tolist())
            count = len(dataframe[dataframe["concept:name"] == i].index)
            average_service_time = int(dataframe[dataframe["concept:name"] == i].sum(axis=0,skipna=True)["@@duration"]/count)
            #print(dataframe[dataframe["concept:name"] == i].sum(axis=0,skipna=True))
            try:
                average_waiting_time = np.mean(traces[i]['all_values'])
            except:
                average_waiting_time = 0
            sns.distplot(traces[i]['all_values'])
            plt.show()

        except KeyError:
            pass

        new_row = pd.Series(data={'activity_name': i,'Average Service Time': average_service_time, 'Average Waiting Time' : average_waiting_time,
                                  'Number of resources': resource_count,"Capacity of teh activity":capacity})
        df = df.append(new_row, ignore_index=True)

    if not df.empty:
        dataframe_list.append(df)

    return dataframe_list



def timerangehours(start_date, end_date,timestep):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


def timerangebigger(start_date,end_date,timestep):
    fraction = int(timestep/24)+1
    for n in range(int(math.ceil(int((end_date - start_date).days)/fraction)+1)):
        yield start_date + timedelta(n*fraction)


def timesplittingbigger(log,rangestart,rangeend,timestep,businesshooursstart,businesshoursend, weekend_list):
    for single_step in timerangebigger(rangestart, rangeend, timestep):
        single_step = single_step - timedelta(minutes=1)
        filtered_log_events = timestamp_filter.apply_events(log, single_step.strftime("%Y-%m-%d %H:%M:%S"), (single_step + timedelta(hours=timestep)).strftime("%Y-%m-%d %H:%M:%S"))
        data = eventDataFrameSorted(filtered_log_events)


        fractions = timestep/24
        rest = timestep%24
        st = (single_step + timedelta(hours=timestep)).strftime("%Y-%m-%d %H:%M:%S")
        end = (single_step + timedelta(hours=timestep + rest)).strftime("%Y-%m-%d %H:%M:%S")
        filtered_log_events = timestamp_filter.apply_events(log, st, end)
        data = data.extend(eventDataFrameSorted(filtered_log_events))

    return data


def timesplittinghours(log,rangestart,rangeend,timestep,businesshooursstart,businesshoursend, weekend_list):
    for single_step in timerangehours(rangestart, rangeend,timestep):
        print(single_step)
        single_step = single_step.replace(hour= businesshooursstart,minute= 0,second=0,microsecond=0) - timedelta(minutes=1)
        print(single_step)
        if businesshoursend-businesshooursstart <= timestep:
            filtered_log_events = timestamp_filter.apply_events(log, single_step.strftime("%Y-%m-%d %H:%M:%S"), (single_step+timedelta(hours=businesshoursend-businesshooursstart)).strftime("%Y-%m-%d %H:%M:%S"))
            data = eventDataFrameSorted(filtered_log_events)

        else:
            fractions = int((businesshoursend-businesshooursstart)/timestep)
            rest = (businesshoursend-businesshooursstart)%timestep


            for item in range(0,fractions):
                filtered_log_events = timestamp_filter.apply_events(log, (single_step+timedelta(hours=item*timestep)).strftime("%Y-%m-%d %H:%M:%S"),
                                                                (single_step+timedelta(hours=item*timestep + timestep)).strftime(
                                                                    "%Y-%m-%d %H:%M:%S"))
                data = eventDataFrameSorted(filtered_log_events)


            st = (single_step + timedelta(hours=fractions * timestep)).strftime("%Y-%m-%d %H:%M:%S")
            end = (single_step + timedelta(hours=fractions * timestep + rest)).strftime("%Y-%m-%d %H:%M:%S")
            filtered_log_events = timestamp_filter.apply_events(log, st,end)
            data = data.extend(eventDataFrameSorted(filtered_log_events))

    return data









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







