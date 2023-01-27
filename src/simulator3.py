import random
import math
import csv
import os
from datetime import datetime
from models.metric_type import MetricType
from utils.area_estimator import AreaEstimator
from utils.incremental_estimator import IncrementalEstimator
import pandas as pd
import matplotlib.pyplot as plt
import inspect
import json

#tipos de eventos
ARRIVAL = 'ARRIVAL'
DEPARTURE = 'DEPARTURE'

#partidas são processadas primeiro do que as chegadas às filas
EVENT_PRIORITY = { DEPARTURE: 0, ARRIVAL: 1 }

#métricas relacionadas aos clientes
CLIENT_METRICS = [
    MetricType.W1, MetricType.W2, MetricType.X1, MetricType.X2, MetricType.T1, MetricType.T2,
]

#métricas relacionadas às filas de espera
QUEUE_METRICS = [
    MetricType.NQ1, MetricType.NQ2, MetricType.N1, MetricType.N2
]

#variáveis auxiliares para geração de métricas
MEAN_SUFFIX = '_est_mean'
VARIANCE_SUFFIX = '_est_var'
MEAN_VAR_COLUMNS = sorted(
    list(map(lambda x: f'{str(x)}{MEAN_SUFFIX}', CLIENT_METRICS)) +
    list(map(lambda x: f'{str(x)}{VARIANCE_SUFFIX}', CLIENT_METRICS)) + 
    list(map(lambda x: f'{str(x)}{MEAN_SUFFIX}', QUEUE_METRICS)) + 
    list(map(lambda x: f'{str(x)}{VARIANCE_SUFFIX}', QUEUE_METRICS)))

class Simulator3:

    def __init__(self,
                 arrival_process: str = 'exponential',
                 inter_arrival_time: float = None,
                 service_process: str = 'exponential',
                 utilization_pct: float = 0.5,
                 service_rate: float = 1.0,
                 service_time: float = None,
                 number_of_rounds=20,
                 samples_per_round=50,
                 arrivals_until_steady_state: int = 0,
                 predefined_system_arrival_times: list[float] = None,
                 confidence: float = 0.95,
                 seed: int = None,
                 save_raw_event_log_file=False,
                 save_metric_per_round_file=True,
                 plot_metrics_per_round=False) -> None:
        self.__number_of_queues = 2
        self.__event_q = []
        self.__waiting_qs = list(
            map(lambda _: [], range(0, self.__number_of_queues)))
        self.__current_service = None
        self.__current_timestamp = 0.0
        self.__client_counter = 1

        self.__confidence = confidence
        """A porcentagem do intervalo de confiança determinado nas métricas coletadas no sistema."""

        self.__utilization_pct: float = utilization_pct

        self.__arrival_process = arrival_process
        self.__arrival_rate = self.__utilization_pct / 2.0
        """Pelo enunciado do trabalho, 2*lambda = rho"""
        self.__inter_arrival_time = inter_arrival_time

        self.__service_process = service_process
        self.__service_rate = service_rate
        self.__service_time = service_time

        self.__number_of_rounds = number_of_rounds
        self.__samples_per_round = samples_per_round
        self.__arrivals_until_steady_state = arrivals_until_steady_state

        self.__current_round = 1
        """Rodada atual do simulador."""
        self.__number_of_arrivals = 0
        """Número de chegadas ao sistema(na fila 1)."""

        self.__clients_in_system = {}
        """Todos os clientes presentes no sistema"""

        self.__interrupted_service = None
        """Variável auxiliar para guardar o valor do cliente que teve seu serviço interrompido por uma chegada à fila 1."""

        self.__predefined_system_arrival_times = predefined_system_arrival_times
        """Instantes de chegada ao sistema pré-definidos. Utilizados para depuração do simulador."""

        self.__metric_estimators_current_round = {}
        """Métricas da rodada atual."""

        for x in CLIENT_METRICS:
            self.__metric_estimators_current_round[str(x)] = IncrementalEstimator()
        
        for x in QUEUE_METRICS:
            self.__metric_estimators_current_round[str(x)] = AreaEstimator()

        self.__metrics_per_round = pd.DataFrame(columns=['round'] +
                                                MEAN_VAR_COLUMNS)
        """Dataframe com o registro de todas as métricas alvo da simulação a cada rodada.
        É usado para gerar um arquivo csv com esses dados ao final da simulação."""

        self.__metric_estimators_simulation = {
            str(x): IncrementalEstimator()
            for x in MEAN_VAR_COLUMNS
        }
        """Estimadores para métricas alvo da simulação.
        Serão incrementados ao final de cada rodada."""

        self.__seed = seed
        """Seed para geração de variáveis aleatórias da simulação."""

        if (seed != None):
            random.seed(self.__seed)

        self.__last_event = {
            'event_timestamp': 0.0
        }
        """Último evento processado pelo simulador.
        Utilizado para o cálculo do número de clientes em fila."""

        self.__event_log = []
        """Log de eventos(para depuração posterior)."""
        self.__opt_save_raw_event_log_file = save_raw_event_log_file
        """Flag para salvar o arquivo de log de eventos ao final da simulação"""
        self.__opt_save_metric_per_round_file = save_metric_per_round_file
        """Flag para salvar o arquivo de métricas por rodada ao final da simulação"""
        self.__opt_plot_metrics_per_round = plot_metrics_per_round
        """Flag para plotar um gráfico com a evolução das métricas ao final da simulação"""
        self.__results_folder = f'./results_{str(datetime.utcnow().timestamp()).replace(".", "")}_simulator3'
        """Pasta onde os arquivos de resultado da simulação serão salvos"""

        self.__execution_parameters = {}
        """Parametros de execução do simulador. Utilizado para depuração."""
        
        self.record_execution_parameters()
    
    def record_execution_parameters(self):
        param_names = []
        for name, _ in inspect.signature(self.__init__).parameters.items():
            param_names.append(name)

        self.__execution_parameters = {}

        for k in self.__dict__:
            name = k.removeprefix('_Simulator3__')
            
            if(name in param_names):
                self.__execution_parameters[name] = self.__dict__[k]

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

            if (e['event_timestamp'] == event_timestamp
                    and EVENT_PRIORITY[e['event_type']] >
                    EVENT_PRIORITY[event_type]):
                break

            index += 1

        self.__event_q.insert(
            index, {
                'event_client': event_client,
                'event_type': event_type,
                'event_queue': event_queue,
                'event_timestamp': event_timestamp
            })

    def cancel_current_service_system_departure_event(self, ):
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

        #coleta métricas relacionadas ao tempo de espera
        if (queue == 1):
            last_event = self.get_last_event(client, ARRIVAL, 1)
            wait_time = self.__current_timestamp - last_event['event_timestamp']
            self.__clients_in_system[client]['metrics'][str(
                MetricType.W1)] += wait_time
        elif (queue == 2 and self.__interrupted_service == None):
            last_event = self.get_last_event(client, ARRIVAL, 2)
            wait_time = self.__current_timestamp - last_event['event_timestamp']
            self.__clients_in_system[client]['metrics'][str(
                MetricType.W2)] += wait_time
        elif (queue == 2 and self.__interrupted_service != None
              and self.__interrupted_service['client'] == client):
            wait_time = self.__current_timestamp - self.__interrupted_service[
                'interruption_time']
            self.__clients_in_system[client]['metrics'][str(
                MetricType.W2)] += wait_time

    def remove_current_service(self, ):
        service_client = self.__current_service['client']
        service_queue = self.__current_service['queue']
        start_time = self.__current_service['start_time']

        if (service_queue == 1):
            self.__clients_in_system[service_client]['metrics'][str(
                MetricType.X1)] += (self.__current_timestamp - start_time)
        elif (service_queue == 2):
            self.__clients_in_system[service_client]['metrics'][str(
                MetricType.X2)] += (self.__current_timestamp - start_time)

        self.__current_service = None

    def set_interrupted_service(self, client, queue, start_time, service_time):
        self.__interrupted_service = {
            'client': client,
            'queue': queue,
            'start_time': start_time,
            'service_time': service_time,
            'interruption_time': self.__current_timestamp
        }

    def remove_interrupted_service(self):
        self.__interrupted_service = None

    def collect_queue_size_metrics(self, queue_number: int):
        nq = len(self.__waiting_qs[queue_number - 1])
        n = nq

        dt = self.__current_timestamp - self.__last_event['event_timestamp']

        if (self.__current_service != None
                and self.__current_service['queue'] == queue_number):
            n += 1

        if (queue_number == 1):
            self.__metric_estimators_current_round[str(
                MetricType.NQ1)].add_sample(nq, dt)
            self.__metric_estimators_current_round[str(
                MetricType.N1)].add_sample(n, dt)
        elif (queue_number == 2):
            self.__metric_estimators_current_round[str(
                MetricType.NQ2)].add_sample(nq, dt)
            self.__metric_estimators_current_round[str(
                MetricType.N2)].add_sample(n, dt)

    def insert_in_waiting_queue(self,
                                queue_number: int,
                                client: int,
                                in_the_front=False):
        if (in_the_front):
            self.__waiting_qs[queue_number - 1].insert(0, client)
        else:
            self.__waiting_qs[queue_number - 1].append(client)

    def pop_from_waiting_queue(self, queue_number: int):
        client = self.__waiting_qs[queue_number - 1].pop(0)

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
            return self.__inter_arrival_time

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
            return self.__service_time

    def advance_round(self, ):
        self.debug_print(f'completed round {self.__current_round}')

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
        """Reseta variáveis de controle e estimadores da rodada para seus valores iniciais."""

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

    def save_simulation_metrics_file(self):
        """Salva o log de eventos em um arquivo .csv."""

        simulation_metrics_file: str = f'{self.__results_folder}/simulation_metrics.csv'
        """Arquivo onde o log de eventos da simulação serão salvos"""

        if (os.path.exists(simulation_metrics_file)):
            os.remove(simulation_metrics_file)

        with open(simulation_metrics_file, 'a+', newline='') as output_file:

            #fieldnames = list(map(lambda x: str(x), self.__metric_estimators_simulation.keys()))

            fieldnames = [
                'metric', 'lower', 'mean', 'upper', 'variance', 'precision',
                'confidence', 'rounds'
            ]

            rows = []

            for metric in self.__metric_estimators_simulation:
                lower = ''
                upper = ''
                precision = ''

                if (metric.endswith(MEAN_SUFFIX)):
                    lower, upper, precision = self.__metric_estimators_simulation[
                        metric].mean_ci(confidence=self.__confidence)
                elif (metric.endswith(VARIANCE_SUFFIX)):
                    lower, upper, precision = self.__metric_estimators_simulation[
                        metric].variance_ci(confidence=self.__confidence)

                rows.append({
                    'metric':
                    metric,
                    'lower':
                    lower,
                    'mean':
                    self.__metric_estimators_simulation[metric].mean(),
                    'upper':
                    upper,
                    'variance':
                    self.__metric_estimators_simulation[metric].variance(),
                    'precision':
                    precision,
                    'confidence':
                    self.__confidence,
                    'rounds':
                    self.__current_round
                })

            dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
            dict_writer.writeheader()
            dict_writer.writerows(rows)

            self.debug_print(
                f'Final simulation results saved at {simulation_metrics_file}')

    def save_execution_parameters_config(self):
        signature = inspect.signature(self.__init__)

        config_file: str = f'{self.__results_folder}/execution_parameters.json'
        """Arquivo onde o log de eventos da simulação serão salvos"""

        if (os.path.exists(config_file)):
            os.remove(config_file)

        with open(config_file, 'a+', newline='') as output_file:
            output_file.write(json.dumps(self.__execution_parameters))

            self.debug_print(f'Execution paramaters config saved at {config_file}')

    def plot_metrics_per_round_evolution(self):
        """Gera gráficos com as a evolução das métricas coletadas na simulação."""

        def plot_metric_and_save(xname: str, yname: str, mean: float):
            plt.xlabel(xname)

            plt.plot(self.__metrics_per_round[xname],
                     self.__metrics_per_round[yname],
                     label=yname,
                     color='blue')

            plt.plot(self.__metrics_per_round[xname],
                     list(map(lambda x: mean,
                              self.__metrics_per_round[xname])),
                     '--',
                     color='red')

            plt.title(f'{yname}_X_{xname}')

            plt.legend()

            file_name = f'{self.__results_folder}/{yname}_X_{xname}.png'

            plt.savefig(file_name)

            plt.close()

        for c in list(
                filter(lambda x: not (str(x).endswith(VARIANCE_SUFFIX)),
                       MEAN_VAR_COLUMNS)):
            mean = self.__metric_estimators_simulation[c].mean()
            plot_metric_and_save('round', c, mean)

        self.debug_print('Metric plots saved.')

    def get_last_event(self, client: int, event_type: str, event_queue: int):
        """Obtém o último evento do tipo espeficificado para um cliente.

        Parameters
        ----------
        client_id : str
            O id do cliente entrante no sistema.
        
        event_type: EventType
            O tipo do evento.

        Returns
        ----------
        event: dict | None
            O evento mais recente do cliente.
        """
        events = [
            x for x in self.__clients_in_system[client]['events'] if
            x['event_type'] == event_type and x['event_queue'] == event_queue
        ]

        if (len(events) > 0):
            return events[0]

        return None

    def add_client_event(self, client: int, event: dict):
        """Adiciona um evento na lista de eventos de um cliente específico(se não existir, cria um novo resgistro para o cliente).
        Esses eventos serão utilizados para o cálculo das métricas desse cliente.

        Parameters
        ----------
        client_id : str
            O id do cliente.
        event: Event
            O evento associado.
        """

        if (client not in self.__clients_in_system):
            self.__clients_in_system[client] = {
                'events': [],
                'metrics': {
                    str(MetricType.W1): 0.0,
                    str(MetricType.X1): 0.0,
                    str(MetricType.T1): 0.0,
                    str(MetricType.W2): 0.0,
                    str(MetricType.X2): 0.0,
                    str(MetricType.T2): 0.0,
                }
            }

        self.__clients_in_system[client]['events'].append(event)

    def remove_client_from_system(self, client: int):
        """Remove um cliente do sistema.

        Parameters
        ----------
        client_id : str
            O id do cliente."""

        x1 = self.__clients_in_system[client]['metrics'][str(MetricType.X1)]
        w1 = self.__clients_in_system[client]['metrics'][str(MetricType.W1)]

        #consolidando os valores de T1 e T2 para o cliente
        self.__clients_in_system[client]['metrics'][str(MetricType.T1)] = x1 + w1

        x2 = self.__clients_in_system[client]['metrics'][str(MetricType.X2)]
        w2 = self.__clients_in_system[client]['metrics'][str(MetricType.W2)]

        self.__clients_in_system[client]['metrics'][str(MetricType.T2)] = x2 + w2

        client_metrics = list(
            self.__clients_in_system[client]['metrics'].keys())

        #adicionando amostras do cliente às amostras da rodada
        for m in client_metrics:
            self.__metric_estimators_current_round[m].add_sample(
                self.__clients_in_system[client]['metrics'][m])

        self.__clients_in_system.pop(client)

    def handle_event(self, event):
        event_type = event['event_type']
        event_queue = event['event_queue']
        event_client = event['event_client']

        self.add_client_event(event_client, event)

        if (event_type == ARRIVAL and event_queue == 1):

            #fila 1 está vazia, 
            if(len(self.__waiting_qs[0]) == 0):
                
                #não há serviço corrente, inicia o serviço do cliente recém chegado
                if (self.__current_service == None):
                    service_time = self.get_service_time()
                    self.set_current_service(event_client, 1, service_time)
                    self.insert_event(DEPARTURE, 1,
                                    self.__current_timestamp + service_time,
                                    event_client)

                #há serviço corrente
                else:
                    service_client = self.__current_service['client']
                    service_queue = self.__current_service['queue']

                    #serviço corrente é da fila 1, cliente recém chegado vai para a fila de espera
                    if (service_queue == 1):
                        self.insert_in_waiting_queue(1, event_client)

                    #serviço corrente é da fila 2
                    #interrompe serviço corrente, 
                    #cliente recém chegado inicia o seu serviço
                    elif (service_queue == 2):
                        self.cancel_current_service_system_departure_event()
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
            elif(len(self.__waiting_qs[0]) > 0):
                self.insert_in_waiting_queue(1, event_client)

            #agenda nova chegada de cliente na fila 1
            self.schedule_new_system_arrival()

            self.__number_of_arrivals += 1

            if (self.__number_of_arrivals >=
                    self.__arrivals_until_steady_state +
                (self.__samples_per_round * self.__current_round)):
                self.advance_round()

            #coleta métricas das filas
            self.collect_queue_size_metrics(1)
            self.collect_queue_size_metrics(2)
        elif (event_type == ARRIVAL and event_queue == 2):

            #sistema está ocioso
            #cliente recém chegado a fila 2 inicia o seu serviço e tem sua partida da fila 2 agendada
            if(len(self.__waiting_qs[0]) == 0 and len(self.__waiting_qs[1]) == 0 and self.__current_service == None):
                service_time = self.get_service_time()
                self.set_current_service(event_client, 2, service_time)
                self.insert_event(DEPARTURE, 2,
                                  self.__current_timestamp + service_time,
                                  event_client)
            #sistema não está ocioso, cliente vai para a fila de espera 2
            else:
                self.insert_in_waiting_queue(2, event_client)

            #coleta métricas das filas
            self.collect_queue_size_metrics(1)
            self.collect_queue_size_metrics(2)
        elif (event_type == DEPARTURE and event_queue == 1):
            self.remove_current_service()

            #fila 1 tem clientes em espera
            #inicia o serviço do primeiro cliente da fila 1
            if (len(self.__waiting_qs[0]) > 0):
                next_client_id = self.pop_from_waiting_queue(1)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 1, service_time)
                self.insert_event(DEPARTURE, 1,
                                  self.__current_timestamp + service_time,
                                  next_client_id)
            elif (len(self.__waiting_qs[1]) > 0):
                next_client_id = self.pop_from_waiting_queue(2)
                service_time = None
                remove_interrumpted_service = False

                if (self.__interrupted_service != None
                        and self.__interrupted_service['client']
                        == next_client_id):
                    service_time = self.__interrupted_service[
                        'start_time'] + self.__interrupted_service[
                            'service_time'] - self.__interrupted_service[
                                'interruption_time']
                    remove_interrumpted_service = True
                else:
                    service_time = self.get_service_time()

                self.set_current_service(next_client_id, 2, service_time)

                if (remove_interrumpted_service):
                    self.remove_interrupted_service()

                self.insert_event(DEPARTURE, 2,
                                  self.__current_timestamp + service_time,
                                  next_client_id)

            self.insert_event(ARRIVAL, 2, self.__current_timestamp,
                              event_client)

            #coleta métricas das filas
            self.collect_queue_size_metrics(1)
            self.collect_queue_size_metrics(2)
        elif (event_type == DEPARTURE and event_queue == 2):
            self.remove_current_service()

            #fila 1 não está vazia
            #inicia serviço do primeiro cliente da fila 1
            if (len(self.__waiting_qs[0]) > 0):
                next_client_id = self.pop_from_waiting_queue(1)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 1, service_time)
                self.insert_event(DEPARTURE, 1,
                                  self.__current_timestamp + service_time,
                                  next_client_id)
            
            #fila 2 não está vazia
            #inicia serviço do primeiro cliente da fila 2
            elif (len(self.__waiting_qs[1]) > 0):
                next_client_id = self.pop_from_waiting_queue(2)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 2, service_time)
                self.insert_event(DEPARTURE, 2,
                                  self.__current_timestamp + service_time,
                                  next_client_id)

            #remove cliente do sistema
            self.remove_client_from_system(event_client)

            #coleta métricas das filas
            self.collect_queue_size_metrics(1)
            self.collect_queue_size_metrics(2)

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

            self.__last_event = event

        os.mkdir(self.__results_folder)

        if (self.__opt_save_raw_event_log_file):
            self.save_event_logs_raw_file()

        if (self.__opt_save_metric_per_round_file):
            self.save_metric_per_round_evolution_file()

        if (self.__opt_plot_metrics_per_round):
            self.plot_metrics_per_round_evolution()

        self.save_simulation_metrics_file()

        self.save_execution_parameters_config()