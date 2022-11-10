from dataclasses import dataclass

from models.service_event_type import ServiceEventType


@dataclass
class ServiceEvent:
    client_id: int
    type: ServiceEventType
    timestamp: float
    queue_number: int

    def __init__(self, type: ServiceEventType, timestamp: float, client_id: int, queue_number: int):
        self.type = type
        self.timestamp = timestamp
        self.client_id = client_id
        self.queue_number = queue_number

    def as_dict(self):
        return {
            'client_id': self.client_id,
            'type': str(self.type),
            'timestamp': self.timestamp,
            'queue_number': self.queue_number
        }

