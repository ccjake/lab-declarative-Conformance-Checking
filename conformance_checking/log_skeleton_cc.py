from pm4py.algo.discovery.log_skeleton import algorithm as log_disc
from pm4py.algo.conformance.log_skeleton import algorithm as log_conf
import pm4py


# log = pm4py.read_xes("/Users/baichaoye/PycharmProjects/lab-declarative-Conformance-Checking/example_log/example_log.xes")
log = pm4py.read_xes("../example_log/example_log.xes")
par = {log_disc.Variants.CLASSIC.value.Parameters.NOISE_THRESHOLD:0.2}
model = log_disc.apply(log,parameters=par)
# print(model)