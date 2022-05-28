from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer
import os
# log = xes_importer(os.path.join("test","input_data",""))

def declare_model_discover(path):
    """

    @param path: the path of the log, that would be mined
    @return: return the model
    """
    # variant = xes_importer.Variants.ITERPARSE
    # parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(path)
    # print(log[0][0])
    # print()
    # print(type(log))
    skolen = lsk_discovery.apply(log= log)
    return skolen

# skeleton_model = declare_model_discover("example_log/example_log.xes")
# print(skeleton_model)