import os
import pandas
from pm4py import format_dataframe
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.visualization.petrinet import visualizer as pn_visualizer


class CustomException(Exception):
    pass


filename = input("Please give the name of the .csv or .xes file you wish to import:\n")
try:
    if filename[-4:] == '.xes':
        variant = xes_importer.Variants.ITERPARSE
        parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
        log = xes_importer.apply(os.path.join(os.path.dirname(os.path.abspath(__file__)), filename), variant=variant,
                                 parameters=parameters)
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

print(log)

tree = inductive_miner.apply_tree(log)
net, initial_marking, final_marking = pt_converter.apply(tree, variant=pt_converter.Variants.TO_PETRI_NET)

gviz = pt_visualizer.apply(tree)
pt_visualizer.view(gviz)
