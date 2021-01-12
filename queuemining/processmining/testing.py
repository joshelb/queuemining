import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.timestamp import timestamp_filter
import numpy as np
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

import pandas as pd
from datetime import timedelta, date, datetime
import math
import pytz
from pm4py.statistics.performance_spectrum import algorithm as performance_spectrum

utc = pytz.UTC
log = xes_importer.apply('running-example.xes')

event_stream = pm4py.convert_to_event_stream(log)

get_activities = attributes_filter.get_attribute_values(log, "concept:name")




for i in event_stream:
    print(i)
    print(type(i))
pd.set_option("display.max_rows", None, "display.max_columns", None)


def creatTables(log):
    get_activities = attributes_filter.get_attribute_values(log, "concept:name")

    df = pd.DataFrame(columns=['Numebr of cases in the queue','Average Service Time','Average waiting time','Number of resources','Capacity of the activity'],
                      )
    for activity in get_activities:
        print(activity)
        tracefilter_log_pos = attributes_filter.apply(log, [activity],
                                                      parameters={
                                                          attributes_filter.Parameters.ATTRIBUTE_KEY: "concept:name",
                                                          attributes_filter.Parameters.POSITIVE: True})
        new_row  = pd.Series(data={'Numebr of cases in the queue':len(tracefilter_log_pos)}, name=activity)
        df = df.append(new_row,ignore_index=False)

        print(df)
        print("        ###################              ")
        for i in tracefilter_log_pos:

            print(i, "\n")

        print("        ###################              ")

    return


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
    print(old,old2)
    return old, old2


def timerange(start_date, end_date,timestep):
    for n in range(int(math.ceil(int(int((end_date - start_date).total_seconds())/60)/timestep))):

        yield start_date + timedelta(minutes=timestep*n)


def timesplitting(log,rangestart,rangeend,timestep):
    for single_step in timerange(rangestart, rangeend,timestep):
        filtered_log = timestamp_filter.filter_traces_intersecting(log, single_step.strftime("%Y-%m-%d %H:%M:%S"),  (single_step+timedelta(minutes=timestep)).strftime("%Y-%m-%d %H:%M:%S"))
        print(filtered_log)
        print(single_step.strftime("%Y-%m-%d %H:%M:%S"))
        print((single_step+timedelta(minutes=timestep)).strftime("%Y-%m-%d %H:%M:%S"))


def get_resource_count(log, activities):
    result_list = []
    # This part differentiates between csv and xes files
    # Event logs have a 'origin' key in their attributes dictionary that stores what type of file they came from
    if log.attributes['origin'] == 'csv':
        activity_str = 'concept:name'
        resource_str = 'resource'
    elif log.attributes['origin'] == 'xes':
        activity_str = 'concept:name'
        resource_str = 'org:resource'
    for i in activities:
        counter = 0
        check_list = []
        event_stream = pm4py.convert_to_event_stream(log)
        event_stream_temp = functools.filter_(lambda t: t[activity_str] == i, event_stream)
        for e in event_stream_temp:
            if e[resource_str] not in check_list:
                check_list.append(e[resource_str])
                counter += 1
        result_list.append(counter)
    return result_list


def get_activities(log):
    activities = attributes_filter.get_attribute_values(log, "concept:name")
    return list(activities.keys())


start_date , end_date = filtertimerange(log)
timesplitting(log,start_date,end_date,20000)

ps = performance_spectrum.apply(log, ["register request","decide"],
                                parameters={performance_spectrum.Parameters.ACTIVITY_KEY: "concept:name",
                                            performance_spectrum.Parameters.TIMESTAMP_KEY: "time:timestamp"})

print(ps)


def group_by_resources(log):
    """Returns a dict having a resource as key and a list of lists with an activity name and a timestamp as content"""
    resources = attributes_filter.get_attribute_values(log, "org:resources")
    list_by_res = {"resource": [[]]}
    for res in resources:
        traces_containing_res = attributes_filter.apply(log, [res],parameters={
            attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource", attributes_filter.Parameters.POSITIVE: True})
        for trace in traces_containing_res:
            contains_res = attributes_filter.apply_events(trace, [res], parameters={
                attributes_filter.Parameters.ATTRIBUTE_KEY: "org:resource", attributes_filter.Parameters.POSITIVE: True})
            for act in contains_res:
                act_data = [trace.attributes["concept:name"], act.attributes["concept:name"], act.attributes["time:timestamp"]]
                list_by_res[res].append(act_data)
            #list_by_res[res].sort() Wie sortiere ich nach timestamp?
    del list_by_res["resource"]
    return list_by_res


def get_end_times(log):
    """Returns a dict having a resource as key and a list of lists with an activity name
    and a start and end timestamp as content """
    list_by_res = group_by_resources(log)
    for res in list_by_res.keys():
        for act in list_by_res[res]:
            if list_by_res[res].index(act)+1 < len(list_by_res):
                next_act = list_by_res[res][list_by_res[res].index(act) + 1]
                act.append(next_act[2])
            else:
                act.append("unknown") #Was wenn Endtime unbekannt?
    return list_by_res


def create_df(log):
    """Returns a dataframe holding all relevant information"""
    list_by_res = get_end_times(log)
    traces = []
    activities = []
    resources = []
    start = []
    end = []
    wait = []
    for res in list_by_res.keys():
        for act in list_by_res[res]:
            traces.append(act[0])
            activities.append(act[1])
            resources.append(res)
            start.append(act[2])
            end.append(act[3])
            wait.append("0")
    d = {"trace_name": traces, "activity_name": activities, "resource": resources,
         "start_time": start, "end_time": end, "waiting_time": wait}
    df = pd.DataFrame(d)
    return df
