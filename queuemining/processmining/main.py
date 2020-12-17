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


def create_table_empty(log):
    pass


# Returns the number of resources available for each activity in the order they appear in the activities dictionary
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


# Returns the names of possible activities as a list
def get_activities(log):
    activities = attributes_filter.get_attribute_values(log, "concept:name")
    return list(activities.keys())


""" The part of the code independent from django will be written in a different module.
    We expect this to be cleaner and easier."""

""" This currently imports .xes or .csv files and turns them into event log objects in pm4py.
    The bottom part is experiments with the inductive miner."""

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
# filtered_log = filtered_log_events = timestamp_filter.apply_events(log, "2010-12-30 00:00:00", "2011-01-01 23:59:59")
# parameters = {inductive_miner.Variants.IM.value.Parameters.ACTIVITY_KEY: 'concept:name'}
# tree = inductive_miner.apply_tree(filtered_log, variant=inductive_miner.Variants.IM)
# net, im, fm = pt_converter.apply(tree, variant=pt_converter.Variants.TO_PETRI_NET)
# print(tree)
# print(type(tree))
# gviz = pt_visualizer.apply(tree, parameters={pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "png"})
# pt_visualizer.view(gviz)
# activities = get_activities(log)
# print(log.attributes)
# print(activities)
# resource_count = get_resource_count(log, activities)
# print(resource_count)
dfg = dfg_discovery.apply(log)
# gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
net, im, fm = dfg_mining.apply(dfg)
parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
gviz = pn_visualizer.apply(net, im, fm, variant=pn_visualizer.Variants.PERFORMANCE, parameters=parameters,
                           log=log)

pn_visualizer.view(gviz)
# print(gviz)
