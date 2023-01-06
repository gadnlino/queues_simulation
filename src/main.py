from simulator import Simulator

if (__name__ == "__main__"):

    #utilization_pct: 0.2, 0.4, 0.6, 0.8, 0.9
    simulator = Simulator(
                        #arrival_process='exponential',
                        arrival_process='deterministic',
                        inter_arrival_time = 1.0,
                        utilization_pct=0.6,
                        service_process='deterministic',
                        service_time=2.1,
                        service_rate=0.5,
                        number_of_rounds=2,
                        samples_per_round=2,
                        services_until_steady_state=0,
                        seed = 0,
                        save_metric_per_round_file=True,
                        save_raw_event_log_file = True,
                        plot_metrics_per_round = True)
    simulator.run()