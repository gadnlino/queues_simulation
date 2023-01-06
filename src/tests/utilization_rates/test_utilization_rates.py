from simulator import Simulator

utilization_rates = [.2, .4, .6, .8, .9]

for rho in utilization_rates:
    print(f'Running simulation with utilization_pct = {rho}')

    simulator = Simulator(utilization_pct=rho,
                          service_rate=1.0,
                          number_of_rounds=20,
                          samples_per_round=100,
                          services_until_steady_state=1000,
                          seed = 0,
                          save_metric_per_round_file=True,
                          save_raw_event_log_file=False,
                          plot_metrics_per_round = True)
    simulator.run()