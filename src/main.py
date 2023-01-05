from simulator import Simulator

if (__name__ == "__main__"):

    #utilization_pct: 0.2, 0.4, 0.6, 0.8, 0.9
    simulator = Simulator(utilization_pct=0.2,
                          service_rate=1.0,
                          number_of_rounds=100,
                          samples_per_round=25,
                          arrivals_until_steady_state=50,
                          seed = 0,
                          save_metric_per_round_file=True,
                          save_raw_event_log_file=False,
                          plot_metrics_per_round = True)
    simulator.run()