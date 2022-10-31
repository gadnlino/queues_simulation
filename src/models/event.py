from dataclasses import dataclass, asdict
from models.event_type import EventType

@dataclass
class Event:
    type: EventType
    timestamp: int
    queue_number: int
