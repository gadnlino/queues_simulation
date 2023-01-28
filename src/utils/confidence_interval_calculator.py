import math
import numpy as np
from scipy import stats

def t_dist_ci(mean, variance, n, confidence):
    std = math.sqrt(variance)        

    alpha = 1-confidence

    #percentil da distribuição t com n-1 graus de liberdade
    percentile = stats.t(df=n-1).ppf(1 - (alpha/2))

    term = percentile * (std / math.sqrt(n))

    lower = mean - term
    upper = mean + term
    precision = percentile * (std/(mean * math.sqrt(n)))

    return lower, upper, precision

def chi2_dist_ci(variance, n, confidence):
    alpha = 1 - confidence

    lower_ppf = stats.chi2.ppf(alpha / 2, n-1)
    higher_ppf = stats.chi2.ppf(1-(alpha / 2), n-1)

    lower = ((n-1)*variance)/higher_ppf
    upper = ((n-1)*variance)/lower_ppf

    precision = (higher_ppf - lower_ppf)/(higher_ppf + lower_ppf)

    return lower, upper, precision

if(__name__ == '__main__'):
    i = 1

    target = 0.05

    #comparação com os valores da tabela na página 133 da apostila
    confidence = 0.95
    table = [
        [20, 0.562],
        [30, 0.473],
        [40, 0.417],
        [50, 0.376],
        [60, 0.346],
        [70, 0.322],
        [80, 0.302],
        [90, 0.286],
        [100, 0.272],
        [200, 0.194],
        [300, 0.159],
        [400, 0.138],
        [500, 0.123],
        [1000, 0.087],
        [2000, 0.062],
        [3000, 0.051],
        [4000, 0.044],
        [5000, 0.039],
    ]

    for row in table:
        n = row[0]
        reference_value = row[1]
        _, _, obtained = chi2_dist_ci(0, n, confidence)
        print(f'n = {n}, reference value = {reference_value}, obtained = {obtained}')

    # 3071 amostras necessárias para obter precisão <= 5%
    while True:
        _,_,precision = chi2_dist_ci(0, i, confidence)

        if(precision <= target):
            print('chi2_dist_ci', 'n', i, 'precision', precision)
            break

        i += 1
    
    #data = [12, 12, 13, 13, 15, 16, 17, 22, 23, 25, 26, 27, 28, 28, 29]

    #create 95% confidence interval for population mean weight
    #print(stats.t.interval(alpha=0.95, df=len(data)-1, loc=np.mean(data), scale=stats.sem(data)) )
    #print(stats.t.interval(confidence = 0.99,df=3300, loc=0.8375237267138028,scale=0.00038917548069624866))

    