import math
from scipy import stats

from utils.confidence_interval_calculator import chi2_dist_ci, t_dist_ci

#https://www.embeddedrelated.com/showarticle/785.php
class IncrementalEstimator:
    def __init__(self) -> None:
        self.clear()
    
    def clear(self):
        self.__s = 0
        self.__s2 = 0
        self.__n = 0

    def nsamples(self):
        return self.__n
    
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
    
    # #https://aegis4048.github.io/comprehensive_confidence_intervals_for_python_developers#python_ci_var
    # def variance_ci(self, confidence : float):
    #     return chi2_dist_ci(self.variance(), self.__n, confidence)
        
    #     # alpha = 1-confidence

    #     # low_ppf = stats.chi2.ppf(alpha / 2, self.__n)
    #     # high_ppf = stats.chi2.ppf(1 - (alpha / 2), self.__n)

    #     # upper = (self.__n) * self.variance() / low_ppf
    #     # lower = (self.__n) * self.variance() / high_ppf

    #     # precision = (high_ppf - low_ppf) / (high_ppf + low_ppf)

    #     # return (lower, upper, precision)
    
    # #https://www.geeksforgeeks.org/how-to-calculate-confidence-intervals-in-python/
    # def mean_ci(self, confidence: float):
    #     return t_dist_ci(self.mean(), self.std(), self.__n, confidence)

    #     # alpha = 1-confidence

    #     # #percentil da distribuição t com n-1 graus de liberdade
    #     # percentile = stats.t(df=self.__n-1).ppf(1 - (alpha/2))

    #     # term = percentile * (std / math.sqrt(self.__n))

    #     # lower = mean - term
    #     # upper = mean + term
    #     # precision = 100 * percentile * (std/(mean * math.sqrt(self.__n)))

    #     # return (lower, upper, precision)

    def __str__(self):
        return str({
            'n': self.__n,
            'mean': self.mean(),
            'variance': self.variance()
        })
        