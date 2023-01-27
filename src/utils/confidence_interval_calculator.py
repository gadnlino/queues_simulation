import math
from scipy import stats

def t_dist_ci(mean, variance, n, confidence):
    std = math.sqrt(variance)        

    alpha = 1-confidence

    #percentil da distribuição t com n-1 graus de liberdade
    percentile = stats.t(df=n-1).ppf(1 - (alpha/2))

    term = percentile * (std / math.sqrt(n))

    lower = mean - term
    upper = mean + term
    #precision = 100 * percentile * (std/(mean * math.sqrt(n)))
    precision = percentile * (std/(mean * math.sqrt(n)))

    return lower, upper, precision

def chi2_dist_ci(variance, n, confidence):
    alpha = 1 - confidence

    lower_ppf = stats.chi2.ppf(alpha / 2, n-1)
    higher_ppf = stats.chi2.ppf(1-(alpha / 2), n-1)

    lower = ((n-1)*variance)/higher_ppf
    upper = ((n-1)*variance)/(lower_ppf)

    precision = (higher_ppf - lower_ppf)/(higher_ppf + lower_ppf)

    return lower, upper, precision

