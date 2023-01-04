import math

#https://www.embeddedrelated.com/showarticle/785.php
class Estimator:
    def __init__(self) -> None:
        self.clear()
    
    def clear(self):
        self.__s = 0
        self.__s2 = 0
        self.__n = 0

    def add_sample(self, value: float):
        self.__n = self.__n + 1

        self.__s = self.__s + value

        self.__s2 = self.__s2 + value*value
    
    def mean(self):
        if(self.__n > 0):
            return self.__s / self.__n
        
        return 0

    def variance(self):
        if(self.__n > 1):
            return (self.__s2 - (self.__s**2)/self.__n)/(self.__n - 1)
        
        return 0

    def std(self):
        return math.sqrt(self.variance())