from simulator import Simulator

if (__name__ == "__main__"):

    #utilization_pct: 0.2, 0.4, 0.6, 0.8, 0.9
    simulator = Simulator(
                        #arrival_process='exponential',
                        #arrival_process='deterministic',
                        arrival_process='exponential',
                        inter_arrival_time = 1.0,
                        utilization_pct=0.2,
                        service_process='exponential',
                        service_time=1.0,
                        service_rate=1.0,
                        #target_precision = 0.05,
                        target_precision = None,
                        number_of_rounds=50000,
                        samples_per_round=50,
                        services_until_steady_state=10000,
                        seed = 10000000,
                        confidence= 0.95,
                        save_metric_per_round_file=True,
                        save_raw_event_log_file = False,
                        plot_metrics_per_round = True)
    simulator.run()