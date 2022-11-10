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

    id_counter = count(start=1)

    def __init__(self, type: EventType, timestamp: float, queue_number: int, \
        client_id: int = None, remaining_service_time: float = None):
        self.type = type
        self.timestamp = timestamp
        self.queue_number = queue_number

        if(not(client_id)):
            self.client_id = next(self.id_counter)
        else:
            self.client_id = client_id

        if(remaining_service_time):
            self.remaining_service_time = remaining_service_time
        else:
            self.remaining_service_time = None
    
    #Critérios
    #1) menor tempo primeiro
    #2) Partidas antes de chegadas
    #3) Fila 1 antes do que a fila 2
    # def __lt__(self, other):
    #     return self.timestamp < other.timestamp or\
    #          event_type_values[self.type] < event_type_values[other.type] or \
    #             self.queue_number < other.queue_number

    def __lt__(self, other):
        return self.timestamp < other.timestamp
    
    # def __le__(self, other):
    #     return self.timestamp <= other.timestamp or\
    #          event_type_values[self.type] < event_type_values[other.type] or\
    #              self.queue_number < other.queue_number

    def __le__(self, other):
        return self.timestamp <= other.timestamp
    
    def as_dict(self):
        return {
            'client_id': self.client_id,
            'type': str(self.type),
            'timestamp': self.timestamp,
            'queue_number': self.queue_number
        }
