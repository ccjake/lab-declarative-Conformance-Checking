from pm4py.algo.discovery.log_skeleton import algorithm as lsk_discovery
from pm4py.objects.log.importer.xes import importer as xes_importer
import os
# log = xes_importer(os.path.join("test","input_data",""))

def declare_model_discover(path):
    log = xes_importer.apply(path)

    skolen = lsk_discovery.apply(log= log,parameters={lsk_discovery.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD: 0.0})
    return skolen

skeleton_model = declare_model_discover("example_log/synthetic event log.xes")
# l  = list(skeleton_model["equivalence"])
# l.sort()
print(skeleton_model)


