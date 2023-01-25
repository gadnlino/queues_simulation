class AreaEstimator:
    def __init__(self):
        # Soma das areas
        self.nqueue_area_sum = 0.0
        # Soma dos intervalos de tempo
        self.dt_sum = 0.0
    def add_sample(self, nqueue: float, dt: float):
        self.nqueue_area_sum += nqueue * dt
        self.dt_sum += dt
    def mean(self):
        return self.nqueue_area_sum / self.dt_sum