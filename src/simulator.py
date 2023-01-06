import bisect
import random
import os
import csv
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from models.event import Event
from models.event_type import EventType
from models.metric import Metric
from models.metric_type import MetricType
from utils.estimator import Estimator

#tipos diferentes de métricas coletadas
METRIC_TYPES = [
    MetricType.W1, MetricType.W2, MetricType.X1, MetricType.X2, MetricType.T1,
    MetricType.T2, MetricType.NQ1, MetricType.NQ2, MetricType.N1, MetricType.N2
]

#tipos diferentes de eventos
EVENT_TYPES = [
    EventType.ARRIVAL, EventType.START_SERVICE_1, EventType.END_SERVICE_1,
    EventType.START_SERVICE_2, EventType.HALT_SERVICE_2, EventType.DEPARTURE
]

#E[T1], E[W1], E[N1], E[Nq1], E[T2], E[W2], E[N2],E[Nq2], V[W1], e V[W2]


class Simulator:
    """Parameters
        ----------
        arrival_process : str
            O processo de chegada de clientes ao sistema. Valores: 'exponential', 'deterministic'.
        
        utilization_pct: float
            A porcentagem de utilização do sistema(rho).
        
        service_process: str
            O processo de serviço do sistema. Valores: 'exponential', 'deterministic'.
        
        service_rate: float
            A taxa de serviço do sistema(mu).
        
        number_of_rounds: int
            O número de rodadas da simulação.
        
        samples_per_round: int
            O número de amostras que serão coletadas a cada rodada de simulação.
        
        services_until_steady_state: int
            O número de serviços executados no sistema(ciclo completo de um cliente no sistema) até atingir o estado de equilíbrio no sistema.
        
        seed: int
            A semente inicial para geração de variáveis aleatórias no sistema.
        
        save_metric_per_round_file: bool
            Caso True, salva um arquivo .csv com a evolução das métricas por rodada.
        
        save_raw_event_log_file: bool
            Caso True, salva um arquivo .csv com todos os eventos da simulação(para depuração).
        
        plot_metrics_per_round: bool
            Caso True, gera gráficos com o tempo de espera médio e o número médio de clientes em cada fila.
        """

    ######### Inicialização e variváveis de controle #########
    def __init__(self,
                 arrival_process: str = 'exponential',
                 utilization_pct: float = 0.5,
                 service_process: str = 'exponential',
                 service_rate: float = 1.0,
                 number_of_rounds: int = 5,
                 samples_per_round: int = 5,
                 services_until_steady_state: int = 0,
                 seed: int = None,
                 save_metric_per_round_file: bool = True,
                 save_raw_event_log_file: bool = False,
                 plot_metrics_per_round: bool=False):

        self.__simulation_running = False
        """Variável de controle para o loop principal do simulador."""

        self.__utilization_pct: float = utilization_pct
        """Taxa de utilização(rho)."""

        self.__arrival_rule = arrival_process
        """Tipos de chegada(determinística ou exponencial)."""

        self.__service_rate: float = service_rate
        """Taxa de serviço(mu)."""

        self.__service_rule = service_process
        """Tipos de serviço(determinístico ou exponencial)."""

        self.__arrival_rate: float = (self.__utilization_pct *
                                      self.__service_rate)
        """Taxa de chegada(lambda)(é obtida a partir das taxas de serviço e utilização, pela formula utilization_pct = (arrival_rate/service_rate))"""

        self.__number_of_rounds: int = number_of_rounds
        """Número de rodadas da simulação"""

        self.__samples_per_round: int = samples_per_round
        """Número de amostras por rodada"""

        self.__services_until_steady_state = services_until_steady_state
        """Número de serviços da fase transiente"""

        self.__seed = seed
        """Seed para geração de variáveis aleatórias da simulação."""

        if (seed != None):
            #setando seed para a simulação
            np.random.seed(seed=self.__seed)

        self.__number_of_qs: int = 2
        """Número de filas do sistema"""

        self.__current_round: int = 0
        """Rodada atual"""

        self.__current_timestamp = 0.0
        """Tempo atual da simulação"""

        self.__current_service = None
        """Cliente atualmente em serviço"""

        self.__event_q: list[Event] = []
        """Lista de eventos principal do simulador"""

        self.__waiting_qs = list(
            map(lambda _: list(), range(0, self.__number_of_qs)))
        """Representação das filas de espera do sistema, seguindo o número de filas indicado por self.__number_of_qs"""

        self.__clients_in_system = {}
        """Todos os clientes presentes no sistema"""

        self.__number_of_arrivals = 0
        """Número de chegadas no sistema"""

        self.__number_of_departures = 0
        """Número de partidas do sistema"""

        self.__collected_samples_current_round = 0
        """Número de amostras coletadas na rodada atual"""

        self.__collected_samples_simulation = 0
        """Número de amostras coletadas em toda a simulação"""

        self.__steady_state = False
        """Indicador de estado de equilíbrio"""

        self.__metric_estimators_current_round = {
            str(MetricType.W1): Estimator(),
            str(MetricType.W2): Estimator(),
            str(MetricType.X1): Estimator(),
            str(MetricType.X2): Estimator(),
            str(MetricType.T1): Estimator(),
            str(MetricType.T2): Estimator(),
            str(MetricType.NQ1): Estimator(),
            str(MetricType.NQ2): Estimator(),
            str(MetricType.N1): Estimator(),
            str(MetricType.N2): Estimator(),
        }
        """Estimadores das métricas de uma rodada da simulação.
        Serão incrementados a cada partida"""

        self.__metric_estimators_simulation = {
            f'{str(MetricType.W1)}_est_mean': Estimator(),
            f'{str(MetricType.W1)}_est_var': Estimator(),
            f'{str(MetricType.W2)}_est_mean': Estimator(),
            f'{str(MetricType.W2)}_est_var': Estimator(),
            f'{str(MetricType.X1)}_est_mean': Estimator(),
            f'{str(MetricType.X1)}_est_var': Estimator(),
            f'{str(MetricType.X2)}_est_mean': Estimator(),
            f'{str(MetricType.X2)}_est_var': Estimator(),
            f'{str(MetricType.NQ1)}_est_mean': Estimator(),
            f'{str(MetricType.NQ1)}_est_var': Estimator(),
            f'{str(MetricType.NQ2)}_est_mean': Estimator(),
            f'{str(MetricType.NQ2)}_est_var': Estimator(),
            f'{str(MetricType.N1)}_est_mean': Estimator(),
            f'{str(MetricType.N1)}_est_var': Estimator(),
            f'{str(MetricType.N2)}_est_mean': Estimator(),
            f'{str(MetricType.N2)}_est_var': Estimator(),
        }
        """Estimadores para métricas alvo da simulação.
        Serão incrementados ao final de cada rodada."""

        self.__metrics_per_round = pd.DataFrame(columns=[
            'round',
            f'{str(MetricType.W1)}_est_mean',
            f'{str(MetricType.W1)}_est_var',
            f'{str(MetricType.W2)}_est_mean',
            f'{str(MetricType.W2)}_est_var',
            f'{str(MetricType.X1)}_est_mean',
            f'{str(MetricType.X1)}_est_var',
            f'{str(MetricType.X2)}_est_mean',
            f'{str(MetricType.X2)}_est_var',
            f'{str(MetricType.NQ1)}_est_mean',
            f'{str(MetricType.NQ1)}_est_var',
            f'{str(MetricType.NQ2)}_est_mean',
            f'{str(MetricType.NQ2)}_est_var',
            f'{str(MetricType.N1)}_est_mean',
            f'{str(MetricType.N1)}_est_var',
            f'{str(MetricType.N2)}_est_mean',
            f'{str(MetricType.N2)}_est_var',
        ])
        """Dataframe com o registro de todas as métricas alvo da simulação a cada rodada.
        É usado para gerar um arquivo csv com esses dados ao final da simulação."""

        self.__opt_save_metric_per_round_file = save_metric_per_round_file
        """Flag para salvar o arquivo de métricas por rodada ao final da simulação"""

        self.__opt_save_raw_event_log_file = save_raw_event_log_file
        """Flag para salvar o arquivo de log de eventos ao final da simulação"""

        self.__opt_plot_metrics_per_round = plot_metrics_per_round
        """Flag para plotar um gráfico com a evolução das métricas ao final da simulação"""

        self.__event_log_raw = []
        """Log de eventos(para depuração posterior)."""

        self.__results_folder = f'./results_{str(datetime.utcnow().timestamp()).replace(".", "")}'
        """Pasta onde os arquivos de resultado da simulação serão salvos"""

        self.__event_log_raw_file: str = f'{self.__results_folder}/event_log_raw.csv'
        """Arquivo onde o log de eventos da simulação serão salvos"""

    def __reset_round_control_variables(self):
        """Reseta variáveis de controle da rodada para seus valores iniciais."""

        self.__collected_samples_current_round = 0

        #reseta o estimador de todas as métricas da rodada para os valores iniciais
        for k in self.__metric_estimators_current_round:
            self.__metric_estimators_current_round[k].clear()

    ######### Utilidades #########
    def __save_event_logs_raw_file(self):
        """Salva o log de eventos em um arquivo .csv."""

        if (os.path.exists(self.__event_log_raw_file)):
            os.remove(self.__event_log_raw_file)

        if (len(self.__event_log_raw) > 0):
            with open(self.__event_log_raw_file, 'a+',
                      newline='') as output_file:

                fieldnames = [
                    'round', 'reference', 'type', 'queue_number', 'timestamp',
                    'client_id', 'remaining_service_time', 'in_the_front'
                ]

                dict_writer = csv.DictWriter(output_file,
                                             fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(self.__event_log_raw)

    def __save_metric_per_round_file(self):
        """Salva as métricas de todas as rodadas em um arquivo .csv."""

        file_name = f'{self.__results_folder}/metric_per_round_{datetime.utcnow().timestamp()}.csv'

        if (os.path.exists(file_name)):
            os.remove(file_name)

        if (len(self.__metrics_per_round) > 0):
            self.__metrics_per_round.to_csv(file_name,
                                            sep=',',
                                            encoding='utf-8',
                                            index=False)

            self.__debug_print(f'Metric per round file saved at {file_name}')

    def __plot_metrics_per_round(self):
        """Gera um gráfico com as a evolução das métricas E[NQ1], E[NQ2], E[W1], E[W2]."""
        title = f'rho={self.__utilization_pct}, mu={self.__service_rate}, lambda={self.__arrival_rate}, samples_per_round={self.__samples_per_round}'

        plt.xlabel('rounds')

        plt.plot(self.__metrics_per_round['round'],
                 self.__metrics_per_round[f'{str(MetricType.W1)}_est_mean'],
                 label='E[W1]',
                 color='blue')

        plt.plot(self.__metrics_per_round['round'],
                 list(
                     map(
                         lambda x: self.__metric_estimators_simulation[
                             f'{str(MetricType.W1)}_est_mean'].mean(),
                         self.__metrics_per_round['round'])),
                 '--',
                 color='red')

        plt.plot(self.__metrics_per_round['round'],
                 self.__metrics_per_round[f'{str(MetricType.W2)}_est_mean'],
                 label='E[W2]',
                 color='orange')

        plt.plot(self.__metrics_per_round['round'],
                 list(
                     map(
                         lambda x: self.__metric_estimators_simulation[
                             f'{str(MetricType.W2)}_est_mean'].mean(),
                         self.__metrics_per_round['round'])),
                 '--',
                 color='black')

        plt.title(title)

        plt.legend()

        wait_time_file_name = f'{self.__results_folder}/wait_time_plot_{datetime.utcnow().timestamp()}.png'

        plt.savefig(wait_time_file_name)

        plt.close()

        self.__debug_print(f'Wait time plot saved at {wait_time_file_name}')

        plt.plot(self.__metrics_per_round['round'],
                 self.__metrics_per_round[f'{str(MetricType.NQ1)}_est_mean'],
                 label='E[NQ1]',
                 color='blue')

        plt.plot(self.__metrics_per_round['round'],
                 list(
                     map(
                         lambda x: self.__metric_estimators_simulation[
                             f'{str(MetricType.NQ1)}_est_mean'].mean(),
                         self.__metrics_per_round['round'])),
                 '--',
                 color='red')

        plt.plot(self.__metrics_per_round['round'],
                 self.__metrics_per_round[f'{str(MetricType.NQ2)}_est_mean'],
                 label='E[NQ2]',
                 color='orange')

        plt.plot(self.__metrics_per_round['round'],
                 list(
                     map(
                         lambda x: self.__metric_estimators_simulation[
                             f'{str(MetricType.NQ2)}_est_mean'].mean(),
                         self.__metrics_per_round['round'])),
                 '--',
                 color='black')

        plt.title(title)

        plt.legend()

        q_size_file_name = f'{self.__results_folder}/q_size_plot_{datetime.utcnow().timestamp()}.png'

        plt.savefig(q_size_file_name)

        plt.close()

        self.__debug_print(f'Queue size plot saved at {q_size_file_name}')

    def __debug_print(self, message: str):
        """Função utilitária para prints no console."""
        now = datetime.now()
        print(f'{now.strftime("%d/%m/%Y, %H:%M:%S")} | {message}')

    ######### Métricas #########
    def __generate_round_metrics(self):
        """Gera as métricas da rodada(média e variância) para todos os valores observados na rodada."""
        current_round_metrics = {
            'round':
            self.__current_round,
            f'{str(MetricType.W1)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.W1)].mean(),
            f'{str(MetricType.W1)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.W1)].variance(),
            f'{str(MetricType.W2)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.W2)].mean(),
            f'{str(MetricType.W2)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.W2)].variance(),
            f'{str(MetricType.X1)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.X1)].mean(),
            f'{str(MetricType.X1)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.X1)].variance(),
            f'{str(MetricType.X2)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.X2)].mean(),
            f'{str(MetricType.X2)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.X2)].variance(),
            f'{str(MetricType.T1)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.T1)].mean(),
            f'{str(MetricType.T1)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.T1)].variance(),
            f'{str(MetricType.T2)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.T2)].mean(),
            f'{str(MetricType.T2)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.T2)].variance(),
            f'{str(MetricType.NQ1)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.NQ1)].mean(),
            f'{str(MetricType.NQ1)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.NQ1)].variance(),
            f'{str(MetricType.NQ2)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.NQ2)].mean(),
            f'{str(MetricType.NQ2)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.NQ2)].variance(),
            f'{str(MetricType.N1)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.N1)].mean(),
            f'{str(MetricType.N1)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.N1)].variance(),
            f'{str(MetricType.N2)}_est_mean':
            self.__metric_estimators_current_round[str(MetricType.N2)].mean(),
            f'{str(MetricType.N2)}_est_var':
            self.__metric_estimators_current_round[str(
                MetricType.N2)].variance(),
        }

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

    def __generate_q_size_metrics(self):
        """Coleta as métricas E[NQ1], E[NQ2], E[N1], E[N2]"""
        if (not self.__steady_state):
            return

        _, current_source_event_type = self.__get_current_service()
        nq1 = self.__get_waiting_q_size(1)
        nq2 = self.__get_waiting_q_size(2)

        self.__metric_estimators_current_round[str(
            MetricType.NQ1)].add_sample(nq1)

        self.__metric_estimators_current_round[str(
            MetricType.NQ2)].add_sample(nq2)

        if (current_source_event_type != None
                and current_source_event_type == EventType.START_SERVICE_1):
            self.__metric_estimators_current_round[str(
                MetricType.N1)].add_sample(nq1 + 1)
            self.__metric_estimators_current_round[str(
                MetricType.N2)].add_sample(nq2)
        elif (current_source_event_type != None
              and current_source_event_type == EventType.START_SERVICE_2):
            self.__metric_estimators_current_round[str(
                MetricType.N1)].add_sample(nq1)
            self.__metric_estimators_current_round[str(
                MetricType.N2)].add_sample(nq2 + 1)
        else:
            self.__metric_estimators_current_round[str(
                MetricType.N1)].add_sample(nq1)
            self.__metric_estimators_current_round[str(
                MetricType.N2)].add_sample(nq2)

    ######### Geração de VA's #########
    def __get_arrival_time(self):
        """Obtém o tempo de chegada de um novo cliente, a partir de uma distribuição exponencial com taxa self.__arrival_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de chegada."""

        if (self.__arrival_rule == 'exponential'):
            return np.random.exponential(scale=1.0 / self.__arrival_rate)
        elif (self.__arrival_rule == 'deterministic'):
            return self.__arrival_rate

    def __get_service_time(self):
        """Obtém o tempo de serviço de um cliente, a partir de uma distribuição exponencial com taxa self.__service_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de serviço."""

        if (self.__service_rule == 'exponential'):
            return np.random.exponential(scale=1.0 / self.__service_rate)
        elif (self.__service_rule == 'deterministic'):
            return self.__service_rate

    ######### Ciclo de vida do simulador #########
    def __enqueue_event(self, event: Event, in_the_front: bool = False):
        """Insere um evento na lista de eventos.\n
        Os eventos são inseridos de maneira que a lista sempre se mantém ordenada pelo timestamp de ocorrência dos eventos.

        Parameters
        ----------
        event : Event
            O evento a ser inserido na lista de eventos.
        in_the_front: bool, optional
            Caso seja informado como True, o evento é inserido na primeira posição da lista(para tratamento imediato)."""

        if (in_the_front):
            self.__event_q.insert(0, event)
        else:
            bisect.insort(self.__event_q, event)

    def __dequeue_event(self) -> Event:
        """Remove um evento na lista de eventos. O evento removido é inserido no log de eventos(self.__event_list_raw).

        Returns
        -------
        event: Event
            O evento na primeira posição da lista."""
        event = self.__event_q.pop(0)

        if (self.__opt_save_raw_event_log_file):
            self.__event_log_raw.append({
                'reference':
                'event',
                **event.as_dict(), 'round':
                self.__current_round
            })

        return event

    def __dequeue_from_waiting_q(self, queue_number: int):
        """Remove um cliente da fila de espera.\n
        O evento de remoção do cliente é inserido no log de eventos(self.__event_list_raw).

        Parameters
        ----------
        queue_number : int
            O número da fila de espera que o cliente será removido.

        Returns
        -------
        next_client: int
            O id do cliente na primeira posição da fila."""

        next_client = self.__waiting_qs[queue_number - 1].pop(0)

        if (self.__opt_save_raw_event_log_file):
            self.__event_log_raw.append({
                'reference':
                'dequeue',
                'queue_number':
                queue_number,
                'timestamp':
                self.__current_timestamp,
                'client_id':
                next_client[0],
                'remaining_service_time':
                next_client[1],
                'round':
                self.__current_round
            })

        return next_client

    def __enqueue_in_waiting_q(self,
                               client_id: int,
                               queue_number: int,
                               remaining_service_time: float = None,
                               in_the_front: bool = False):
        """Insere um cliente em uma fila de espera.

        Parameters
        ----------
        client_id : int
            O id do cliente a ser inserido na fila de espera.
        queue_number : int
            O número da fila de espera para inserir o cliente.
        remaining_service_time : float, optional
            O tempo de serviço restante do serviço interrrompido do cliente.
        in_the_front : bool, optional
            Caso True, insere o cliente na primeira posição da fila."""
        if (in_the_front):
            self.__waiting_qs[queue_number - 1].insert(
                0, (client_id, remaining_service_time))
        else:
            self.__waiting_qs[queue_number - 1].append(
                (client_id, remaining_service_time))

        if (self.__opt_save_raw_event_log_file):
            self.__event_log_raw.append({
                'reference': 'enqueue',
                'queue_number': queue_number,
                'timestamp': self.__current_timestamp,
                'client_id': client_id,
                'remaining_service_time': remaining_service_time,
                'in_the_front': in_the_front,
                'round': self.__current_round
            })

    def __remove_current_service_departure(self):
        """Remove a partida do sistema agendada para o cliente atualmente em serviço.\n
        Essa função só é chamada em casos em que há preempção de serviço."""
        current_client_id, _ = self.__get_current_service()

        departures_current_service = list(
            filter(
                lambda x: x.type == EventType.DEPARTURE and x.client_id ==
                current_client_id and x.queue_number == 2, self.__event_q))

        self.__event_q.remove(departures_current_service[0])

    def __add_client_in_system(self, client_id: str):
        """Adiciona um cliente ao sistema. Esse é inicializado com os seus valores iniciais.

        Parameters
        ----------
        client_id : str
            O id do cliente entrante no sistema."""
        self.__clients_in_system[client_id] = {
            'events': [],
            str(MetricType.W1): 0,
            str(MetricType.X1): 0,
            str(MetricType.W2): 0,
            str(MetricType.X2): 0,
        }

    def __get_last_event(self, client_id: int, event_type: EventType):
        """Obtém o ultimo do tipo espeficificado para um cliente.

        Parameters
        ----------
        client_id : str
            O id do cliente entrante no sistema.
        
        event_type: EventType
            O tipo do evento.

        Returns
        ----------
        event: Event | None
            O evento mais recente do cliente.
        """
        events = [
            x for x in self.__clients_in_system[client_id]['events']
            if x.type == event_type
        ]

        if (len(events) > 0):
            return events[0]

        return None

    def __add_client_event(self, client_id: str, event: Event):
        """Adiciona um evento na lista de eventos de um cliente específico.
        Esses eventos serão utilizados para o cálculo das métricas desse cliente.

        Parameters
        ----------
        client_id : str
            O id do cliente.
        event: Event
            O evento associado.
        """
        self.__clients_in_system[client_id]['events'].append(event)

    def __remove_client_from_system(self, client_id: str):
        """Remove um cliente do sistema.

        Parameters
        ----------
        client_id : str
            O id do cliente."""
        self.__clients_in_system.pop(client_id)

    def __get_next_client_in_waiting_q(self, queue_number: int) -> int:
        """Obtém(sem remover) o cliente na primeira posição de uma fila de espera.

        Parameters
        ----------
        queue_number : int
            O número da fila de espera para obter o cliente.
        
        Returns
        ----------
        client_id: int
            o id do cliente na primeira posição da fila de espera."""
        return self.__waiting_qs[queue_number - 1][0]

    def __get_waiting_q_size(self, queue_number: int) -> int:
        """Obtém o número de clientes presentes na fila de espera.

        Parameters
        ----------
        queue_number : int
            O número da fila de espera especificada.
        
        Returns
        ----------
        length: int
            O número de clientes presentes na fila de espera."""
        return len(self.__waiting_qs[queue_number - 1])

    def __get_end_of_current_service(self):
        """Obtém o timestamp do término do seviço corrente.
        
        Returns
        ----------
        timestamp: float
            O instante do término do serviço corrente."""
        current_client_id, _ = self.__get_current_service()

        departures_current_service = list(filter(lambda x: x.type == EventType.DEPARTURE \
                        and x.client_id == current_client_id
                        and x.queue_number == 2, self.__event_q))

        departures_current_service.sort(key=lambda x: x.timestamp)

        end_of_current_service = departures_current_service[0].timestamp

        return end_of_current_service

    def __get_current_service(self):
        """Obtém as informações do serviço corrente.
        
        Returns
        ----------
        timestamp: tuple[int, EventType]
            O client_id do cliente do serviço corrente, e o tipo de evento originário do serviço."""
        if (self.__current_service == None):
            return None, None

        return self.__current_service

    def __set_current_service(self, client_id: int,
                              source_event_type: EventType):
        """Salva as informações do serviço corrente.
        
        Parameters
        ----------
        client_id: int
            O id do cliente servido.
        source_event_type:EventType
            O tipo do evento que originou o serviço corrente."""

        self.__current_service = (client_id, source_event_type)

    def __schedule_next_arrival(self):
        """Agenda a próxima chegada de um cliente ao sistema.\n
        O tempo de chegada do próximo cliente é determinado pela função self.__get_arrival_time."""
        next_arrival_time = self.__current_timestamp + self.__get_arrival_time(
        )

        self.__enqueue_event(
            Event(timestamp=next_arrival_time,
                  type=EventType.ARRIVAL,
                  queue_number=1))

    def __advance_round(self, ):
        """Avança a rodada atual e gera as métricas da rodada. 
        Caso tenham sido executadas todas as rodadas, a simulação é encerrada."""
        if (self.__current_round == self.__number_of_rounds):
            self.__simulation_running = False
            return

        self.__debug_print(
            f'completed round {self.__current_round+1} / {self.__number_of_rounds}'
        )

        self.__generate_round_metrics()

        self.__reset_round_control_variables()

        self.__current_round += 1

    def __handle_arrival(self, event: Event):
        """Trata o evento do tipo EventType.ARRIVAL.\n
        Se não há serviço corrente, o cliente recém chegado inicia imediatamente o seu serviço(EventType.START_SERVICE_1).\n
        Se o serviço corrente é oriundo da fila de espera 1, o cliente é inserido na fila de espera 1.\n
        Caso o serviço corrente seja oriundo da fila de espera 2, o serviço desse cliente é interrompido(EventType.HALT_SERVICE_2), 
        e o cliente recém chegado inicia o serviço imediatamente."""
        self.__add_client_in_system(event.client_id)
        self.__add_client_event(event.client_id, event)
        current_client_id, current_source_event_type = self.__get_current_service(
        )

        if (current_client_id == None):
            next_client = Event(timestamp=self.__current_timestamp,
                                type=EventType.START_SERVICE_1,
                                queue_number=1,
                                client_id=event.client_id)

            self.__enqueue_in_waiting_q(event.client_id, 1)
            self.__enqueue_event(next_client, True)
        elif (current_source_event_type == EventType.START_SERVICE_1):
            self.__enqueue_in_waiting_q(event.client_id, 1)
        else:
            self.__enqueue_in_waiting_q(event.client_id, 1)

            if (self.__get_waiting_q_size(1) == 1):
                next_client = Event(timestamp=self.__current_timestamp,
                                    type=EventType.START_SERVICE_1,
                                    queue_number=1,
                                    client_id=event.client_id)

                self.__enqueue_event(next_client, True)

                current_client_id, _ = self.__get_current_service()

                halt_service = Event(timestamp=self.__current_timestamp,
                                     type=EventType.HALT_SERVICE_2,
                                     queue_number=2,
                                     client_id=current_client_id)

                self.__enqueue_event(halt_service, True)

        self.__number_of_arrivals = self.__number_of_arrivals + 1

        self.__schedule_next_arrival()

        #gera métricas
        self.__generate_q_size_metrics()

    def __handle_start_service_1(self, event: Event):
        """Trata o evento do tipo EventType.START_SERVICE_1.\n
        O cliente é removido da fila de espera 1.\n
        É obtido o tempo do serviço, e agendada o evento de término do serviço(EventType.END_SERVICE_1)."""
        self.__add_client_event(event.client_id, event)
        next_client, _ = self.__dequeue_from_waiting_q(event.queue_number)

        self.__set_current_service(next_client, event.type)

        self.__enqueue_event(
            Event(timestamp=self.__current_timestamp +
                  self.__get_service_time(),
                  type=EventType.END_SERVICE_1,
                  queue_number=1,
                  client_id=event.client_id))

        # gera métricas
        client_arrival = self.__get_last_event(event.client_id,
                                               EventType.ARRIVAL)

        self.__clients_in_system[event.client_id][str(
            MetricType.W1)] += (self.__current_timestamp -
                                client_arrival.timestamp)

        #gera métricas
        self.__generate_q_size_metrics()

    def __handle_end_service_1(self, event: Event):
        """Trata o evento do tipo EventType.END_SERVICE_1.\n
        Caso as filas de esperas 1 e 2 estejam vazias, o cliente inicia o seu segundo serviço imediatamente(EventType.START_SERVICE_2).\n
        Caso haja clientes em alguma fila de espera, o cliente é enfileirado na fila de espera 2, e o serviço da fila mais prioritária é iniciado."""
        self.__add_client_event(event.client_id, event)
        next_event = Event(timestamp=self.__current_timestamp,
                           type=EventType.START_SERVICE_2,
                           queue_number=2,
                           client_id=event.client_id)

        self.__enqueue_in_waiting_q(event.client_id, 2)
        self.__set_current_service(None, None)

        if (self.__get_waiting_q_size(1) < 1
                and self.__get_waiting_q_size(2) == 1):
            self.__enqueue_event(next_event, True)
        elif (self.__get_waiting_q_size(1) > 0):
            next_client_id, _ = self.__get_next_client_in_waiting_q(1)

            next_event = Event(client_id=next_client_id,
                               type=EventType.START_SERVICE_1,
                               timestamp=self.__current_timestamp,
                               queue_number=1)

            self.__enqueue_event(next_event, True)
        elif (self.__get_waiting_q_size(2) > 0):
            next_client_id, _ = self.__get_next_client_in_waiting_q(2)

            next_event = Event(client_id=next_client_id,
                               type=EventType.START_SERVICE_2,
                               timestamp=self.__current_timestamp,
                               queue_number=2)

            self.__enqueue_event(next_event, True)

        # gera métricas
        client_start_service_1 = self.__get_last_event(
            event.client_id, EventType.START_SERVICE_1)

        self.__clients_in_system[event.client_id][str(
            MetricType.X1)] += (self.__current_timestamp -
                                client_start_service_1.timestamp)

        #gera métricas
        self.__generate_q_size_metrics()

    def __handle_start_service_2(self, event: Event):
        """Trata o evento do tipo EventType.START_SERVICE_2.\n
        O cliente é removido da fila de espera 2.\n
        É obtido o tempo do serviço, e agendada o evento de saída do sistema(EventType.DEPARTURE)."""
        self.__add_client_event(event.client_id, event)
        next_client, remaining_service_time = self.__dequeue_from_waiting_q(
            event.queue_number)

        self.__set_current_service(next_client, event.type)

        if (remaining_service_time == None):
            self.__enqueue_event(
                Event(timestamp=self.__current_timestamp +
                      self.__get_service_time(),
                      type=EventType.DEPARTURE,
                      queue_number=2,
                      client_id=event.client_id))
        else:
            self.__enqueue_event(
                Event(timestamp=self.__current_timestamp +
                      remaining_service_time,
                      type=EventType.DEPARTURE,
                      queue_number=2,
                      client_id=event.client_id))

        # gera métricas
        client_end_service_1 = self.__get_last_event(event.client_id,
                                                     EventType.END_SERVICE_1)
        client_halt_service_2 = self.__get_last_event(event.client_id,
                                                      EventType.HALT_SERVICE_2)

        if (client_halt_service_2 != None):
            self.__clients_in_system[event.client_id][str(
                MetricType.W2)] += (self.__current_timestamp -
                                    client_halt_service_2.timestamp)
        else:
            self.__clients_in_system[event.client_id][str(
                MetricType.W2)] += (self.__current_timestamp -
                                    client_end_service_1.timestamp)

        #gera métricas
        self.__generate_q_size_metrics()

    def __handle_halt_service_2(self, event: Event):
        """Trata o evento do tipo EventType.HALT_SERVICE_2.\n
        O evento de saída do sistema do cliente atual é removido da fila de eventos, e o cliente é enfileirado na primeira posição da fila 2."""
        self.__add_client_event(event.client_id, event)
        client_id, _ = self.__get_current_service()

        remaining_service_time = \
                    self.__get_end_of_current_service() - self.__current_timestamp

        if (not (remaining_service_time > 0.0)):
            remaining_service_time = None

        self.__remove_current_service_departure()

        self.__enqueue_in_waiting_q(
            client_id,
            2,
            in_the_front=True,
            remaining_service_time=remaining_service_time)

        self.__set_current_service(None, None)

        # gera métricas
        client_start_service_2 = self.__get_last_event(
            event.client_id, EventType.START_SERVICE_2)

        self.__clients_in_system[event.client_id][str(
            MetricType.X2)] += (self.__current_timestamp -
                                client_start_service_2.timestamp)

        #gera métricas
        self.__generate_q_size_metrics()

    def __handle_departure(self, event: Event):
        """Trata o evento do tipo EventType.DEPARTURE.\n
        O cliente é removido do serviço corrente, e o cliente da primeira posição da fila mais prioritária tem o serviço iniciado."""
        self.__add_client_event(event.client_id, event)
        if (self.__get_waiting_q_size(1) > 0):
            next_client_id, _ = self.__get_next_client_in_waiting_q(1)

            next_event = Event(client_id=next_client_id,
                               type=EventType.START_SERVICE_1,
                               timestamp=self.__current_timestamp,
                               queue_number=1)

            self.__enqueue_event(next_event, in_the_front=True)
        elif (self.__get_waiting_q_size(2) > 0):
            next_client_id, _ = self.__get_next_client_in_waiting_q(2)

            next_event = Event(client_id=next_client_id,
                               type=EventType.START_SERVICE_2,
                               timestamp=self.__current_timestamp,
                               queue_number=2)

            self.__enqueue_event(next_event, in_the_front=True)

        self.__set_current_service(None, None)

        self.__number_of_departures += 1

        # gera métricas do cliente atual
        client_start_service_2 = self.__get_last_event(
            event.client_id, EventType.START_SERVICE_2)

        self.__clients_in_system[event.client_id][str(
            MetricType.X2)] += (self.__current_timestamp -
                                client_start_service_2.timestamp)

        if (self.__number_of_departures == self.__services_until_steady_state +
                1):
            self.__debug_print('reached steady state')
            self.__steady_state = True

        if (self.__steady_state):
            # coleta métricas do cliente atual
            self.__metric_estimators_current_round[str(
                MetricType.W1)].add_sample(
                    self.__clients_in_system[event.client_id][str(
                        MetricType.W1)])

            self.__metric_estimators_current_round[str(
                MetricType.X1)].add_sample(
                    self.__clients_in_system[event.client_id][str(
                        MetricType.X1)])

            self.__metric_estimators_current_round[str(
                MetricType.T1
            )].add_sample(
                self.__clients_in_system[event.client_id][str(MetricType.X1)] +
                self.__clients_in_system[event.client_id][str(MetricType.W1)])

            self.__metric_estimators_current_round[str(
                MetricType.W2)].add_sample(
                    self.__clients_in_system[event.client_id][str(
                        MetricType.W2)])

            self.__metric_estimators_current_round[str(
                MetricType.X2)].add_sample(
                    self.__clients_in_system[event.client_id][str(
                        MetricType.X2)])

            self.__metric_estimators_current_round[str(
                MetricType.T2
            )].add_sample(
                self.__clients_in_system[event.client_id][str(MetricType.X2)] +
                self.__clients_in_system[event.client_id][str(MetricType.W2)])

            self.__collected_samples_current_round = self.__collected_samples_current_round + 1
            self.__collected_samples_simulation = self.__collected_samples_simulation + 1

            #gera métricas do tamanho da fila
            self.__generate_q_size_metrics()

            if (self.__collected_samples_current_round >=
                    self.__samples_per_round):
                self.__advance_round()

        self.__remove_client_from_system(event.client_id)

    ######### Loop principal #########
    def run(self):
        """Loop principal do simulador.\n
        Remove-se o evento na primeira posição da lista de eventos, e delega-se para a função de tratamento adequada.
        Ao final da execução de todas as rodadas, salva o log de eventos no arquivo .csv"""

        finished_success = False
        start_time = datetime.utcnow().timestamp()
        try:
            self.__simulation_running = True
            #enfileirando a primeira chegada na fila mais prioritária
            self.__enqueue_event(
                Event(timestamp=self.__current_timestamp +
                      self.__get_arrival_time(),
                      type=EventType.ARRIVAL,
                      queue_number=1))

            #while (len(self.__event_q) > 0):
            while (self.__simulation_running):
                event: Event = self.__dequeue_event()

                self.__current_timestamp = event.timestamp

                #self.__debug_print(event)

                if (event.type == EventType.ARRIVAL):
                    self.__handle_arrival(event)
                elif (event.type == EventType.START_SERVICE_1):
                    self.__handle_start_service_1(event)
                elif (event.type == EventType.END_SERVICE_1):
                    self.__handle_end_service_1(event)
                elif (event.type == EventType.START_SERVICE_2):
                    self.__handle_start_service_2(event)
                elif (event.type == EventType.HALT_SERVICE_2):
                    self.__handle_halt_service_2(event)
                elif (event.type == EventType.DEPARTURE):
                    self.__handle_departure(event)

            self.__generate_round_metrics()

            finished_success = True
        finally:
            if (finished_success):
                end_time = datetime.utcnow().timestamp()
                simulation_time = end_time - start_time

                self.__debug_print(
                    f'Total simulation time: {simulation_time} s')

                self.__debug_print(
                    f'Results after {self.__number_of_rounds} rounds of simulation'
                )

                os.mkdir(self.__results_folder)

                if (self.__opt_save_metric_per_round_file):
                    self.__save_metric_per_round_file()

                if (self.__opt_save_raw_event_log_file):
                    self.__save_event_logs_raw_file()

                if (self.__opt_plot_metrics_per_round):
                    self.__plot_metrics_per_round()