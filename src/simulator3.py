import random
import math
import csv
import os
from datetime import datetime
from models.metric_type import MetricType
from utils.estimator import Estimator
import pandas as pd
import matplotlib.pyplot as plt

ARRIVAL = 'ARRIVAL'
DEPARTURE = 'DEPARTURE'

METRIC_TYPES = [
    MetricType.W1, MetricType.W2, MetricType.X1, MetricType.X2, MetricType.T1,
    MetricType.T2, MetricType.NQ1, MetricType.NQ2, MetricType.N1, MetricType.N2
]

MEAN_SUFFIX = '_est_mean'
VARIANCE_SUFFIX = '_est_var'

MEAN_VAR_COLUMNS = sorted(
    list(map(lambda x: f'{str(x)}{MEAN_SUFFIX}', METRIC_TYPES)) +
    list(map(lambda x: f'{str(x)}{VARIANCE_SUFFIX}', METRIC_TYPES)))


class Simulator3:

    def __init__(self,
                 arrival_process: str = 'exponential',
                 service_process: str = 'exponential',
                 number_of_rounds=20,
                 samples_per_round=50,
                 arrivals_until_steady_state: int = 0,
                 predefined_system_arrival_times: list[float] = None,
                 seed: int = None,
                 save_raw_event_log_file=False,
                 save_metric_per_round_file=True,
                 plot_metrics_per_round = False) -> None:
        self.__number_of_queues = 2
        self.__event_q = []
        self.__waiting_qs = list(
            map(lambda _: [], range(0, self.__number_of_queues)))
        self.__current_service = None
        self.__current_timestamp = 0.0
        self.__client_counter = 1

        self.__arrival_process = arrival_process
        self.__arrival_rate = 1.0

        self.__service_process = service_process
        self.__service_rate = 1.0

        self.__number_of_rounds = number_of_rounds
        self.__samples_per_round = samples_per_round
        self.__arrivals_until_steady_state = arrivals_until_steady_state

        self.__current_round = 1
        """Rodada atual do simulador."""
        self.__number_of_arrivals = 0
        """Número de chegadas ao sistema(na fila 1)."""

        self.__interrupted_service = None
        """Variável auxiliar para guardar o valor do cliente que teve seu serviço interrompido por uma chegada à fila 1."""

        self.__predefined_system_arrival_times = predefined_system_arrival_times
        """Instantes de chegada ao sistema pré-definidos. Utilizados para depuração do simulador."""

        self.__metric_estimators_current_round = {
            str(x): Estimator()
            for x in METRIC_TYPES
        }
        """Métricas da rodada atual."""

        self.__metrics_per_round = pd.DataFrame(columns=['round'] +
                                                MEAN_VAR_COLUMNS)
        """Dataframe com o registro de todas as métricas alvo da simulação a cada rodada.
        É usado para gerar um arquivo csv com esses dados ao final da simulação."""

        self.__metric_estimators_simulation = {
            str(x): Estimator()
            for x in MEAN_VAR_COLUMNS
        }

        self.__seed = seed
        """Seed para geração de variáveis aleatórias da simulação."""

        if (seed != None):
            random.seed(self.__seed)

        self.__event_log = []
        """Log de eventos(para depuração posterior)."""
        self.__opt_save_raw_event_log_file = save_raw_event_log_file
        """Flag para salvar o arquivo de log de eventos ao final da simulação"""
        self.__opt_save_metric_per_round_file = save_metric_per_round_file
        """Flag para salvar o arquivo de métricas por rodada ao final da simulação"""
        self.__opt_plot_metrics_per_round = plot_metrics_per_round
        """Flag para plotar um gráfico com a evolução das métricas ao final da simulação"""
        self.__results_folder = f'./results_{str(datetime.utcnow().timestamp()).replace(".", "")}'
        """Pasta onde os arquivos de resultado da simulação serão salvos"""

    def debug_print(self, *message):
        # now = datetime.now()
        # print(now.strftime("%d/%m/%Y, %H:%M:%S"), message)
        print(message)

    def save_event_logs_raw_file(self):
        """Salva o log de eventos em um arquivo .csv."""

        event_log_file: str = f'{self.__results_folder}/event_log_raw.csv'
        """Arquivo onde o log de eventos da simulação serão salvos"""

        if (os.path.exists(event_log_file)):
            os.remove(event_log_file)

        if (len(self.__event_log) > 0):
            with open(event_log_file, 'a+', newline='') as output_file:

                fieldnames = list(self.__event_log[0].keys())

                dict_writer = csv.DictWriter(output_file,
                                             fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(self.__event_log)

    def get_client_counter(self):
        current = self.__client_counter

        self.__client_counter += 1

        return current

    def schedule_new_system_arrival(self, next_arrival_time: float = None):
        if (self.__predefined_system_arrival_times == None
                and self.__current_round <= self.__number_of_rounds):
            arrival_time = self.get_arrival_time()

            self.insert_event(ARRIVAL, 1,
                              self.__current_timestamp + arrival_time,
                              self.get_client_counter())
        elif (self.__predefined_system_arrival_times != None
              and next_arrival_time != None):
            self.insert_event(ARRIVAL, 1,
                              self.__current_timestamp + next_arrival_time,
                              self.get_client_counter())

    def insert_event(self, event_type, event_queue, event_timestamp,
                     event_client):

        index = 0

        for e in self.__event_q:
            if (e['event_timestamp'] > event_timestamp):
                break

            index += 1

        self.__event_q.insert(
            index, {
                'event_client': event_client,
                'event_type': event_type,
                'event_queue': event_queue,
                'event_timestamp': event_timestamp
            })

    def remove_current_service_system_departure_event(self, ):
        service_client = self.__current_service['client']

        self.__event_q = list(
            filter(
                lambda x: not (x['event_type'] == DEPARTURE and x[
                    'event_queue'] == 2 and x['event_client'] == service_client
                               ), self.__event_q))

    def set_current_service(self, client, queue, service_time):
        self.__current_service = {
            'client': client,
            'queue': queue,
            'start_time': self.__current_timestamp,
            'service_time': service_time
        }

    def remove_current_service(self, ):
        self.__current_service = None

    def set_interrupted_service(self, client, queue, start_time, service_time):
        self.__interrupted_service = {
            'client':
            client,
            'queue':
            queue,
            'start_time':
            start_time,
            'service_time':
            service_time,
            'remaining_time':
            (start_time + service_time) - self.__current_timestamp
        }

    def remove_interrupted_service(self):
        self.__interrupted_service = None

    def collect_queue_size_metrics(self, queue_number: int):
        nq = len(self.__waiting_qs[queue_number - 1])
        n = nq

        if (self.__current_service != None
                and self.__current_service['queue'] == queue_number):
            n += 1

        if (queue_number == 1):
            self.__metric_estimators_current_round[str(
                MetricType.NQ1)].add_sample(nq)
            self.__metric_estimators_current_round[str(
                MetricType.N1)].add_sample(n)
        elif (queue_number == 2):
            self.__metric_estimators_current_round[str(
                MetricType.NQ2)].add_sample(nq)
            self.__metric_estimators_current_round[str(
                MetricType.N2)].add_sample(n)

    def insert_in_waiting_queue(self,
                                queue_number: int,
                                client: int,
                                in_the_front=False):
        if (in_the_front):
            self.__waiting_qs[queue_number - 1].insert(0, client)
        else:
            self.__waiting_qs[queue_number - 1].append(client)

        self.collect_queue_size_metrics(queue_number)

    def pop_from_waiting_queue(self, queue_number: int):
        client = self.__waiting_qs[queue_number - 1].pop(0)

        self.collect_queue_size_metrics(queue_number)

        return client

    def get_arrival_time(self):
        """Obtém o tempo de chegada de um novo cliente, a partir de uma distribuição exponencial com taxa self.__arrival_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de chegada."""

        if (self.__arrival_process == 'exponential'):
            u = random.random()
            return math.log(u) / (-self.__arrival_rate)
        elif (self.__arrival_process == 'deterministic'):
            return self.__arrival_rate

    def get_service_time(self):
        """Obtém o tempo de serviço de um cliente, a partir de uma distribuição exponencial com taxa self.__service_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de serviço."""
        if (self.__service_process == 'exponential'):
            u = random.random()
            return math.log(u) / (-self.__service_rate)
        elif (self.__service_process == 'deterministic'):
            return self.__service_rate

    def advance_round(self, ):
        self.debug_print(f'completed round {self.__current_round + 1}')

        self.__current_round += 1

        self.generate_round_metrics()

        self.reset_round_control_variables()

    def generate_round_metrics(self):
        """Gera as métricas da rodada(média e variância) para todos os valores observados na rodada."""

        current_round_metrics = {'round': self.__current_round}

        for c in MEAN_VAR_COLUMNS:
            [tp, _, stat] = c.split("_")

            if (stat == 'mean'):
                current_round_metrics[
                    c] = self.__metric_estimators_current_round[tp].mean()
            elif (stat == 'var'):
                current_round_metrics[
                    c] = self.__metric_estimators_current_round[tp].variance()

        self.__metrics_per_round = \
            pd.concat([self.__metrics_per_round, pd.DataFrame(current_round_metrics, index=[self.__current_round])])

        for k in self.__metric_estimators_simulation:
            [tp, _, stat] = k.split("_")

            if (stat == 'mean'):
                self.__metric_estimators_simulation[k].add_sample(
                    self.__metric_estimators_current_round[tp].mean())
            elif (stat == 'var'):
                self.__metric_estimators_simulation[k].add_sample(
                    self.__metric_estimators_current_round[tp].variance())

    def reset_round_control_variables(self):
        """Reseta variáveis de controle da rodada para seus valores iniciais."""

        #self.__collected_samples_current_round = 0

        #reseta o estimador de todas as métricas da rodada para os valores iniciais
        for k in self.__metric_estimators_current_round:
            self.__metric_estimators_current_round[k].clear()

    def save_metric_per_round_evolution_file(self):
        """Salva as métricas de todas as rodadas em um arquivo .csv."""

        file_name = f'{self.__results_folder}/metric_per_round_evolution_{datetime.utcnow().timestamp()}.csv'

        if (os.path.exists(file_name)):
            os.remove(file_name)

        if (len(self.__metrics_per_round) > 0):
            self.__metrics_per_round.to_csv(file_name,
                                            sep=',',
                                            encoding='utf-8',
                                            index=False)

            self.debug_print(f'Metric per round file saved at {file_name}')

    def plot_metrics_per_round_evolution(self):
        """Gera gráficos com as a evolução das métricas coletadas na simulação."""

        def plot_metric_and_save(xname :str, yname: str, mean: float):
            plt.xlabel(xname)

            plt.plot(self.__metrics_per_round[xname],
                    self.__metrics_per_round[yname],
                    label=yname,
                    color='blue')

            plt.plot(self.__metrics_per_round[xname],
                    list(
                        map(
                            lambda x: mean,
                            self.__metrics_per_round[xname])),
                    '--',
                    color='red')

            plt.title(f'{yname}_X_{xname}')

            plt.legend()

            file_name = f'{self.__results_folder}/{yname}_X_{xname}.png'

            plt.savefig(file_name)

            plt.close()
        
        for c in MEAN_VAR_COLUMNS:
            mean = self.__metric_estimators_simulation[c].mean()
            plot_metric_and_save('round', c, mean)

        self.debug_print('Metric plots saved.')

    def handle_event(self, event):
        event_type = event['event_type']
        event_queue = event['event_queue']
        event_client = event['event_client']

        if (event_type == ARRIVAL and event_queue == 1):

            if (self.__current_service == None):
                service_time = self.get_service_time()
                self.set_current_service(event_client, 1, service_time)
                self.insert_event(DEPARTURE, 1,
                                  self.__current_timestamp + service_time,
                                  event_client)
            else:
                service_client = self.__current_service['client']
                service_queue = self.__current_service['queue']

                if (service_queue == 1):
                    self.insert_in_waiting_queue(1, event_client)
                elif (service_queue == 2):
                    self.remove_current_service_system_departure_event()
                    self.set_interrupted_service(
                        self.__current_service['client'],
                        self.__current_service['queue'],
                        self.__current_service['start_time'],
                        self.__current_service['service_time'])
                    self.remove_current_service()
                    self.insert_in_waiting_queue(2,
                                                 service_client,
                                                 in_the_front=True)

                    service_time = self.get_service_time()
                    self.set_current_service(event_client, 1, service_time)
                    self.insert_event(DEPARTURE, 1,
                                      self.__current_timestamp + service_time,
                                      event_client)

            self.schedule_new_system_arrival()

            self.__number_of_arrivals += 1

            if (self.__number_of_arrivals >=
                    self.__arrivals_until_steady_state +
                (self.__samples_per_round * self.__current_round)):
                self.advance_round()

        elif (event_type == ARRIVAL and event_queue == 2):
            self.insert_in_waiting_queue(2, event_client)

            if (len(self.__waiting_qs[0]) == 0
                    and self.__current_service == None):
                next_client_id = self.pop_from_waiting_queue(2)

                service_time = None

                if (self.__interrupted_service != None
                        and self.__interrupted_service['client']
                        == next_client_id):
                    service_time = self.__interrupted_service['remaining_time']
                    self.remove_interrupted_service()
                else:
                    service_time = self.get_service_time()

                self.set_current_service(next_client_id, 2, service_time)
                self.insert_event(DEPARTURE, 2,
                                  self.__current_timestamp + service_time,
                                  next_client_id)
        elif (event_type == DEPARTURE and event_queue == 1):
            self.remove_current_service()

            if (len(self.__waiting_qs[0]) > 0):
                next_client_id = self.pop_from_waiting_queue(1)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 1, service_time)
                self.insert_event(DEPARTURE, 1,
                                  self.__current_timestamp + service_time,
                                  next_client_id)

            self.insert_event(ARRIVAL, 2, self.__current_timestamp,
                              event_client)
        elif (event_type == DEPARTURE and event_queue == 2):
            self.remove_current_service()

            if (len(self.__waiting_qs[0]) > 0):
                next_client_id = self.pop_from_waiting_queue(1)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 1, service_time)
                self.insert_event(DEPARTURE, 1,
                                  self.__current_timestamp + service_time,
                                  next_client_id)
            elif (len(self.__waiting_qs[1]) > 0):
                next_client_id = self.pop_from_waiting_queue(2)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 2, service_time)
                self.insert_event(DEPARTURE, 2,
                                  self.__current_timestamp + service_time,
                                  next_client_id)

    def run(self, ):

        if (self.__predefined_system_arrival_times == None):
            self.schedule_new_system_arrival()
        else:
            """Agendando chegadas pré determinadas ao sistema."""
            for t in self.__predefined_system_arrival_times:
                self.schedule_new_system_arrival(t)

        while (len(self.__event_q) > 0):
            event = self.__event_q.pop(0)

            if (self.__opt_save_raw_event_log_file):
                self.__event_log.append(event)

            self.__current_timestamp = event['event_timestamp']

            #self.debug_print(event, self.__current_service)

            self.handle_event(event)

        os.mkdir(self.__results_folder)

        if (self.__opt_save_raw_event_log_file):
            self.save_event_logs_raw_file()

        if (self.__opt_save_metric_per_round_file):
            self.save_metric_per_round_evolution_file()
        
        if (self.__opt_plot_metrics_per_round):
            self.plot_metrics_per_round_evolution()