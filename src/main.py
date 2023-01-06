from simulator import Simulator

if (__name__ == "__main__"):

    #utilization_pct: 0.2, 0.4, 0.6, 0.8, 0.9
    simulator = Simulator(
                        arrival_process='exponential',
                        utilization_pct=0.49,
                        service_process='exponential',
                        service_rate=1,
                        number_of_rounds=20000,
                        samples_per_round=10,
                        services_until_steady_state=2000,
                        seed = 0,
                        save_metric_per_round_file=True,
                        save_raw_event_log_file=False,
                        plot_metrics_per_round = True)
    simulator.run()