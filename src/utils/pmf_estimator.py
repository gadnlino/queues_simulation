class PMFEstimator:
    def __init__(self):
        # Soma dos quadrados dos Nqis coletados vezes o intervalo de tempo
        self.nqueue_squares_sum = 0.0
        # Soma dos Nqis coletados vezes o intervalo de tempo
        self.nqueue_sum = 0.0
        # Soma dos intervalos de tempo
        self.dt_sum = 0.0
    def add_sample(self, nqueue, dt):
        self.nqueue_squares_sum += (nqueue**2) * dt
        self.nqueue_sum += nqueue * dt
        self.dt_sum += dt
    def variance(self):
        second_moment = self.nqueue_squares_sum / self.dt_sum
        first_moment = self.nqueue_sum / self.dt_sum
        return second_moment - (first_moment**2)