import numpy as np

class DataPointEstimator:
    def __init__(self) -> None:
        self.clear()
    
    def clear(self):
        self.__samples = []

    def nsamples(self):
        return len(self.__samples)
    
    def add_sample(self, value: float):
        self.__samples.append(value)
    
    def mean(self):
        return np.mean(self.__samples)

    def variance(self):
        return np.var(self.__samples)

    def std(self):
        return np.std(self.__samples)