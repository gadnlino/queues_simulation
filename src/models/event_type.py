from enum import Enum


class EventType(Enum):
    ARRIVAL = "ARRIVAL"
    START_SERVICE_1 = "START_SERVICE_1"
    END_SERVICE_1 = "END_SERVICE_1"
    START_SERVICE_2 = "START_SERVICE_2"
    HALT_SERVICE_2 = "HALT_SERVICE_2"
    DEPARTURE = "DEPARTURE"
