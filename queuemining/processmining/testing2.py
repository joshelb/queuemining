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
utc=pytz.UTC
log = xes_importer.apply('running-example.xes')

event_stream = pm4py.convert_to_event_stream(log)

get_activities = attributes_filter.get_attribute_values(log, "concept:name")




for i in event_stream:
    print(i)
    print(type(i))
pd.set_option("display.max_rows", None, "display.max_columns", None)
def creatTables(log,dataframe, start,end, timestep):
    for index in dataframe.index():
        if start < dataframe["start_time"][index] and dataframe["end_time"][index] < end:





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
    end_date = end_date.replace(hour = 0, minute= 0, second = 0,microsecond= 0)
    start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    for n in range(int(math.ceil(int(int((end_date - start_date).total_seconds())/60)/timestep))):

        yield start_date + timedelta(minutes=timestep*n)

def timesplitting(log,rangestart,rangeend,timestep,dataframe):
    for single_step in timerange(rangestart, rangeend,timestep):
        creatTables(log,dataframe, single_step,single_step+timedelta(minutes=timestep),timestep)





        filtered_log = timestamp_filter.filter_traces_intersecting(log, single_step.strftime("%Y-%m-%d %H:%M:%S"),  (single_step+timedelta(minutes=timestep)).strftime("%Y-%m-%d %H:%M:%S"))
        print(filtered_log)
        print(single_step.strftime("%Y-%m-%d %H:%M:%S"))
        print((single_step+timedelta(minutes=timestep)).strftime("%Y-%m-%d %H:%M:%S"))




start_date , end_date = filtertimerange(log)
timesplitting(log,start_date,end_date,20000)

ps = performance_spectrum.apply(log, ["register request","decide"],
                                parameters={performance_spectrum.Parameters.ACTIVITY_KEY: "concept:name",
                                            performance_spectrum.Parameters.TIMESTAMP_KEY: "time:timestamp"})

print(ps)

