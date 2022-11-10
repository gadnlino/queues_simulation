from enum import Enum

class QueueEventType(Enum):
    ARRIVAL = "ARRIVAL"
    DEPARTURE = "DEPARTURE"

event_type_values = {
    QueueEventType.ARRIVAL: 1,
    QueueEventType.DEPARTURE: 0,
}