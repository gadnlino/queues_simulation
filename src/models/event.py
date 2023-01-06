from dataclasses import dataclass
from itertools import count

from models.event_type import EventType


@dataclass
class Event:
    client_id: str
    """Id do cliente associado à esse evento."""
    type: EventType
    """Tipo do evento(ver class EventType)."""
    timestamp: float
    """Instante de ocorrência do evento."""
    queue_number: int
    """Número da fila onde o evento irá ocorrer."""
    remaining_service_time: float
    """Tempo restante de serviço do cliente associado ao evento. 
    Será preenchido somente quando type = EventType.START_SERVICE_2."""

    __id_counter = count(start=1)
    """Contador de ids para os novos clientes."""

    def __init__(self, type: EventType, timestamp: float, queue_number: int, \
        client_id: int = None, remaining_service_time: float = None):
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
