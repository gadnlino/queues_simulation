from dataclasses import dataclass
import uuid
from models.event_type import EventType

@dataclass
class Event:
    id: str
    type: EventType
    timestamp: float
    queue_number: int
    remaining_service_time: float

    def __init__(self, type: EventType, timestamp: float, queue_number: int, \
        id: str = "", remaining_service_time: float = None):
        self.type = type
        self.timestamp = timestamp
        self.queue_number = queue_number

        if(not(id)):
            self.id = str(uuid.uuid4())
        else:
            self.id = id

        if(remaining_service_time):
            self.remaining_service_time = remaining_service_time
        else:
            self.remaining_service_time = None

    def __lt__(self, other):
        return self.timestamp < other.timestamp
    
    def __le__(self, other):
        return self.timestamp <= other.timestamp
    
    def as_dict(self):
        return {
            'id': self.id,
            'type': str(self.type),
            'timestamp': self.timestamp,
            'queue_number': self.queue_number
        }
