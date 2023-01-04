from enum import Enum

class MetricType(Enum):
    def __str__(self):
        return str(self.value)
        
    W1 = "W1"
    W2 = "W2"
    X1 = "X1"
    X2 = "X2"
    NQ1 = "NQ1"
    NQ2 = "NQ2"
    N1 = "N1"
    N2 = "N2"
    