import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import interval_lifecycle
import pandas as pd
from queuemining.processmining.backendutils import filtertimerange,timesplittinghours,timesplittingbigger,calculateAverageoftimestep



pd.set_option("display.max_rows", None, "display.max_columns", None)


""""Handles the import of the Log Files and returns the log object"""
def importLogs(filepath,timestampcolumn):
    if filepath[-4:] == '.xes':
        log = xes_importer.apply(filepath)
    elif filepath[-4:] == '.csv':
        log = pd.read_csv('<path_to_csv_file.csv>', sep=',')
        log = dataframe_utils.convert_timestamp_columns_in_df(log)
        log = log.sort_values(timestampcolumn)
        log = log_converter.apply(log)
    return log

""""Enriches the log object in case of lifcycle transitions if possible"""
def enrichlog(log):
    try:
        enriched_log = interval_lifecycle.assign_lead_cycle_time(log)
    except KeyError:
        enriched_log = log
    return enriched_log







if __name__ == "__main__":
    logobject = enrichlog(importLogs("running-example.xes","time:timestamp"))
    st,et = filtertimerange(logobject)
    print(st,et)

    timestep = 2000
    if timestep >= 24:
        datalist = timesplittingbigger(logobject,st,et,timestep,0,19,[])
        frame = calculateAverageoftimestep(datalist,logobject)
    else:
        datalist = timesplittinghours(logobject,st,et,timestep,0,19,[])
        frame = calculateAverageoftimestep(datalist,logobject)


    print(frame)



