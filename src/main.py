from simulator import Simulator

if (__name__ == "__main__"):

    #utilization_pct: 0.2, 0.4, 0.6, 0.8, 0.9
    simulator = Simulator(
                        #arrival_process='exponential',
                        #arrival_process='deterministic',
                        arrival_process='deterministic',
                        inter_arrival_time = 2.0,
                        utilization_pct=0.6,
                        service_process='deterministic',
                        service_time=1.0,
                        service_rate=1.0,
                        number_of_rounds=20,
                        target_precision = 0.05,
                        samples_per_round=50,
                        services_until_steady_state=10000,
                        seed = 0,
                        confidence= 0.95,
                        save_metric_per_round_file=True,
                        save_raw_event_log_file = False,
                        plot_metrics_per_round = True)
    simulator.run()