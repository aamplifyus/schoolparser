from enum import Enum

""" FRAGILITY MODEL """
# MODEL params in milliseconds
WINSIZE_LTV = 250
STEPSIZE_LTV = 125
RADIUS = 1.5  # perturbation radius
PERTURBTYPE = "c"
COLUMN_PERTURBATION = "c"
ROW_PERTURBATION = "r"


class FRAGILITY_PARAMETERS(Enum):
    WINSIZE = 250
    STEPSIZE = 125
    RADIUS = 1.5
    PERTURBTYPE = "C"
    COLUMN_PERTURBATION = "C"
    ROW_PERTURBATION = "R"


# possible reference schemes for scalp recording data - note that there is no bipolar
class SCALP_REFERENCES(Enum):
    monopolar = "monopolar"
    common_avg = "common_avg"
    bipolar = "bipolar"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


class IEEG_REFERENCES(Enum):
    bipolar = "bipolar"
    monopolar = "monopolar"
    common_avg = "common_avg"

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)
