from models.metric_type import MetricType

class Metric:
    type: MetricType
    value: float
    timestamp: float
    queue_number: int
    client_id: str

    def __init__(self,
                 type: MetricType,
                 value: float,
                 timestamp: float,
                 queue_number: int = None,
                 client_id: str = None):
        self.type = type
        self.value = value
        self.timestamp = timestamp
        self.queue_number = queue_number
        self.client_id = client_id

    def as_dict(self):
        return {
            'type': str(self.type),
            'value': self.value,
            'timestamp': self.timestamp,
            'queue_number': self.queue_number,
            'client_id': self.client_id
        }