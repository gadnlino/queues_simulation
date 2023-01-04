from dataclasses import dataclass
from itertools import count

from models.event_type import EventType


@dataclass
class Event:
    client_id: str
    type: EventType
    timestamp: float
    queue_number: int
    remaining_service_time: float
    client_color: str

    __id_counter = count(start=1)

    def __init__(self, type: EventType, timestamp: float, queue_number: int, \
        client_id: int = None, remaining_service_time: float = None, client_color: str = None):
        self.type = type
        self.timestamp = timestamp
        self.queue_number = queue_number

        if (not (client_id)):
            self.client_id = next(self.__id_counter)
        else:
            self.client_id = client_id

        if (remaining_service_time):
            self.remaining_service_time = remaining_service_time
        else:
            self.remaining_service_time = None

        if (client_color):
            self.client_color = client_color
        else:
            self.client_color = None

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __le__(self, other):
        return self.timestamp <= other.timestamp

    def as_dict(self):
        return {
            'client_id': self.client_id,
            'type': str(self.type),
            'timestamp': self.timestamp,
            'queue_number': self.queue_number
        }
