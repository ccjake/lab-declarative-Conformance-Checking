from enum import Enum, unique

@unique
class TEMPLATE(Enum):
    Equivalence = "equivalence"
    Always_After = "always_after"
    Always_Before = "always_before"
    Never_Together = "never_together"
    Directly_Follows = "directly_follows"
    Activity_Frequency = "activ_freq"