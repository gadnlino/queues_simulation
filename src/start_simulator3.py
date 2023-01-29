from simulator3 import Simulator3
import numpy as np

if (__name__ == "__main__"):

    #utilization_pct: 0.2, 0.4, 0.6, 0.8, 0.9
    simulator = Simulator3(
        #service_process= 'deterministic',
        service_process='exponential',
        #service_time = 1.0,
        service_rate=1.0,
        arrival_process='exponential',
        #arrival_process= 'deterministic',
        #inter_arrival_time=1.5,
        #utilization_pct=0.2,
        utilization_pct=0.9,
        number_of_rounds=200,
        samples_per_round=2000,
        collect_all=False,
        arrivals_until_steady_state=0,
        #predefined_system_arrival_times=list(np.arange(0, 30, 1.5)),
        confidence=0.95,
        seed=100000,
        save_raw_event_log_file=False,
        save_metric_per_round_file = False,
        plot_metrics_per_round=False)

    simulator.run()