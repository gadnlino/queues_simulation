import math
from scipy import stats

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
    
    #https://aegis4048.github.io/comprehensive_confidence_intervals_for_python_developers#python_ci_var
    def variance_ci(self, confidence : float):
        alpha = 1-confidence

        low_ppf = stats.chi2.ppf(alpha / 2, self.__n-1)
        high_ppf = stats.chi2.ppf(1 - alpha / 2, self.__n-1)

        upper = (self.__n - 1) * self.variance() / low_ppf
        lower = (self.__n - 1) * self.variance() / high_ppf

        precision = (high_ppf - low_ppf) / (high_ppf + low_ppf)

        return (lower, upper, precision)
    
    #https://www.geeksforgeeks.org/how-to-calculate-confidence-intervals-in-python/
    def mean_ci(self, confidence: float):
        std = self.std()
        mean = self.mean()

        #percentil da distribuição t com n graus de liberdade
        percentile = stats.t(df=self.__n).ppf(confidence)

        a = (std / math.sqrt(self.__n)) * percentile

        precision = a / mean
        upper_limit = mean + a
        lower_limit = mean - a

        return (lower_limit, upper_limit, precision)

        # lower, upper = stats.t.interval(alpha=confidence,
        #       df=self.__n-1,
        #       loc=mean, 
        #       scale=std)
            
        # precision = (upper - lower) / (upper + lower)

        # return upper, lower, precision
        