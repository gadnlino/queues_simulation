from simulator import Simulator

if (__name__ == "__main__"):
    simulator = Simulator(utilization_pct=0.99,
                          service_rate=1.0,
                          number_of_rounds=500,
                          round_sample_size=100,
                          save_metric_per_round_file=True,
                          save_raw_event_log_file=False,
                          plot_metrics_per_round = True)
    simulator.run()