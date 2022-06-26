from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer
import os
# log = xes_importer(os.path.join("test","input_data",""))

def declare_model_discover(path):
    log = xes_importer.apply(path)

    skolen = lsk_discovery.apply(log= log,parameters={lsk_discovery.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: 0})
    return skolen

skeleton_model = declare_model_discover("example_log/synthetic event log.xes")
# skeleton_model = declare_model_discover("example_log/example_log.xes")


# import pandas as pd
# import pm4py
# df = pd.read_csv("example_log/example_log_mg.csv")
# df = pm4py.format_dataframe(df,case_id='case',activity_key='event',timestamp_key='startTime')
# eg = pm4py.convert_to_event_log(df)
# model = lsk_discovery.apply(log=eg)

for k in skeleton_model.keys():
    skeleton_model[k] = list(skeleton_model[k])
    skeleton_model[k].sort()
print(skeleton_model)


# print(model)
