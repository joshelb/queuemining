import os
import pandas
import pm4py
from pm4py import format_dataframe
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.visualization.petrinet import visualizer as pn_visualizer
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.objects.log.util import func as functools
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.objects.conversion.dfg import converter as dfg_mining
from pm4py.algo.filtering.log.timestamp import timestamp_filter
from pm4py.objects.petri import semantics
import graphviz


class CustomException(Exception):
    pass


def create_table_dataframe(mydict):
    return pandas.DataFrame.from_dict(mydict)


# Returns the number of resources available for each activity in the order they appear in the activities dictionary
def get_resource_count(log, mydict):
    result_list = []
    # This part differentiates between csv and xes files
    # Event logs have a 'origin' key in their attributes dictionary that stores what type of file they came from
    if log.attributes['origin'] == 'csv':
        activity_str = 'concept:name'
        resource_str = 'resource'
    elif log.attributes['origin'] == 'xes':
        activity_str = 'concept:name'
        resource_str = 'org:resource'
    for i in mydict['activity']:
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


""" Takes calculated average service times and number of cases between each activity pair
    and calculates the rest of the required information and returns them as lists """


def calculate_values(values_dict, mydict):
    queues = []
    service_time_list = []
    waiting_time_list = []
    for i in mydict['activity']:
        flag = False
        service_time = 0
        arrival_rate_list = []
        service_rate_list = []
        for j in mydict['activity']:
            if f'{i}->{j}' in values_dict:
                current = values_dict[f'{i}->{j}']
                service_rate = current[1] / current[0]
                service_rate_list.append(service_rate)
                service_time += current[0]
                arrival_rate = (service_rate * current[1]) / (current[1] + 1)
                arrival_rate_list.append(arrival_rate)
                flag = True
        if flag:
            average_arrival_rate = sum(arrival_rate_list) / len(arrival_rate_list)
            average_service_rate = sum(service_rate_list) / len(service_rate_list)
            service_time_list.append(service_time)
            queue = (average_arrival_rate * average_arrival_rate) / (
                    average_service_rate * (average_service_rate - average_arrival_rate))
            queues.append(queue)
            waiting_time = 60 / (average_service_rate - average_arrival_rate)
            waiting_time_list.append(waiting_time)
        else:
            queues.append('-')
            waiting_time_list.append('-')
            service_time_list.append('-')

    return queues, service_time_list, waiting_time_list


def calculate_queue():
    pass


# Returns the names of possible activities as a list
def get_activities(log):
    activities = attributes_filter.get_attribute_values(log, "concept:name")
    return list(activities.keys())


""" The part of the code independent from django will be written in a different module.
    We expect this to be cleaner and easier."""

""" This currently imports .xes or .csv files and turns them into event log objects in pm4py. 
    The pathing for files will be changed when migrating with django part of the project """

filename = "running-example.xes"  # input("Please give the name of the .csv or .xes file you wish to import:\n")
try:
    if filename[-4:] == '.xes':
        variant = xes_importer.Variants.ITERPARSE
        parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
        log = xes_importer.apply(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), variant=variant,
                                 parameters=parameters)
        log.attributes['origin'] = 'xes'
    elif filename[-4:] == '.csv':
        log = pandas.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), sep=';')
        log = format_dataframe(log, case_id='case_id', activity_key='activity', timestamp_key='timestamp',
                               timest_format='%Y-%m-%d %H:%M:%S%z')
        log = log_converter.apply(log)
except FileNotFoundError:
    print(f'No files with name "{filename}" found in folder.')
    exit()
except CustomException:
    print('Please only give the name of a file formatted in .xes or .csv')
    exit()

""" This section is for testing different abilities of pm4py and will be cleaned up later """
# filtered_log = filtered_log_events = timestamp_filter.apply_events(log, "2010-12-30 00:00:00", "2011-01-01 23:59:59")
# parameters = {inductive_miner.Variants.IM.value.Parameters.ACTIVITY_KEY: 'concept:name'}
# tree = inductive_miner.apply_tree(filtered_log, variant=inductive_miner.Variants.IM)
# net, im, fm = pt_converter.apply(tree, variant=pt_converter.Variants.TO_PETRI_NET)
# print(tree)
# print(type(tree))
# gviz = pt_visualizer.apply(tree, parameters={pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"})
# pt_visualizer.view(gviz)

# dfg = dfg_discovery.apply(log)
# gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
# net, im, fm = dfg_mining.apply(dfg)
# variant = pn_visualizer.Variants.FREQUENCY
# parameters = {variant.value.Parameters.FORMAT: "png"}
# gviz = pn_visualizer.apply(net, im, fm, variant=variant, parameters=parameters, log=log)
# pn_visualizer.view(gviz)
# print(gviz)


# activities = get_activities(log)
activities = ['OPD', 'Lab', 'X-Ray', 'Drug', 'Billing']
mydict = {'activity': activities}
values_dict = {'OPD->Drug': [2, 166], 'OPD->Lab': [1, 89], 'OPD->Billing': [0.21, 1]}
print(activities)
# mydict['resource_count'] = get_resource_count(log, mydict)
# print(mydict['resource_count'])
queues, service_times, waiting_times = calculate_values(values_dict, mydict)
resource_count = [13, 4, 6, 10, 5]
mydict['number'], mydict['service'], mydict['waiting'], mydict['resources'], mydict[
    'capacity'] = queues, service_times, waiting_times, resource_count, ['-', '-', '-', '-', '-']
data_frame = create_table_dataframe(mydict)
print(data_frame)