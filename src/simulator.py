import bisect
import heapq
import json
import os
import csv

import numpy as np

from models.event import Event
from models.event_type import EventType
from models.metric import Metric
from models.metric_type import MetricType


class Simulator:

    def __init__(self):
        #arquivo onde o log de eventos da simulação serão salvos
        self.__event_list_raw_file: str = './event_list_raw.csv'

        #log de eventos(para depuração posterior)
        self.__event_list_raw = []

        #número de filas do sistema
        self.__number_of_qs: int = 2

        #taxa de utilização(rho)
        self.__utilization_pct: float = 0.99

        #tempo máximo de chegada de pessoas no sistema(tempo de funcionamento)
        self.__system_max_arrival_time: float = 1000

        #taxa de serviço(definido no enunciado do trabalho)
        self.__service_rate: float = 1

        #taxa de chegada(é obtida a partir das taxas de serviço e utilização, pela formula utilization_pct = (arrival_rate/service_rate))
        self.__arrival_rate: float = (self.__utilization_pct *
                                      self.__service_rate)

        #número de rodadas da simulação
        self.__number_of_rounds: int = 5

        #rodada atual
        self.__current_round: int = 0

        self.__metrics_accumulated = {
            str(MetricType.W1): 0,
            str(MetricType.W2): 0,
            str(MetricType.X1): 0,
            str(MetricType.X2): 0,
            str(MetricType.T1): 0,
            str(MetricType.T2): 0,
            str(MetricType.NQ1): 0,
            str(MetricType.NQ2): 0,
            str(MetricType.N1): 0,
            str(MetricType.N2): 0
        }

        self.__events_current_round: list[Event] = []

        self.__metrics_current_round: list[Metric] = []

    def __reset_simulation_variables(self):
        """Reseta variáveis de controle para seus valores iniciais."""

        #tempo atual da simulação
        self.__current_timestamp = 0.0

        #cliente atualmente em serviço
        self.__current_service = None

        #lista de eventos principal do simulador
        self.__event_q: list[Event] = []
        """representação das filas de espera do sistema, seguindo o número de filas indicado por self.__number_of_qs"""
        self.__waiting_qs = list(
            map(lambda _: list(), range(0, self.__number_of_qs)))

        self.__events_current_round: list[Event] = []

        self.__metrics_current_round: list[Metric] = []

    def __generate_metrics(self, metric_list: 'list[MetricType]'):

        for m in metric_list:

            metric = None

            if (m == MetricType.W1):
                queue_number = 1
                client_id, current_event = self.__get_current_service()
                client_arrival = list(
                    filter(
                        lambda x: x.type == EventType.ARRIVAL and x.client_id
                        == client_id, self.__events_current_round))
                value = self.__current_timestamp - client_arrival[0].timestamp
                metric = Metric(MetricType.W1, value, self.__current_timestamp,
                                queue_number, client_id)
            elif (m == MetricType.X1):
                queue_number = 1
                end_service_1 = list(
                    filter(lambda x: x.type == EventType.END_SERVICE_1,
                           self.__events_current_round))
                end_service_1.sort(key=lambda x: x.timestamp, reverse=True)
                last_end_service_1 = end_service_1[0]
                start_service_1 = list(
                    filter(
                        lambda x: x.type == EventType.START_SERVICE_1 and x.
                        client_id == last_end_service_1.client_id,
                        self.__events_current_round))[0]
                value = (last_end_service_1.timestamp -
                         start_service_1.timestamp)
                metric = Metric(MetricType.X1, value, self.__current_timestamp,
                                queue_number, last_end_service_1.client_id)
            elif (m == MetricType.T1):
                queue_number = 1
                end_service_1 = list(
                    filter(lambda x: x.type == EventType.END_SERVICE_1,
                           self.__events_current_round))
                end_service_1.sort(key=lambda x: x.timestamp, reverse=True)
                last_client = end_service_1[0].client_id

                w1 = list(
                    filter(
                        lambda x: x.type == MetricType.W1 and x.client_id ==
                        last_client, self.__metrics_current_round))[0].value
                x1 = list(
                    filter(
                        lambda x: x.type == MetricType.X1 and x.client_id ==
                        last_client, self.__metrics_current_round))[0].value

                value = w1 + x1
                metric = Metric(MetricType.T1, value, self.__current_timestamp,
                                queue_number, last_client)
            elif (m == MetricType.NQ1):
                queue_number = 1
                value = self.__get_waiting_q_size(queue_number)
                metric = Metric(MetricType.NQ1, value,
                                self.__current_timestamp, queue_number)
            elif (m == MetricType.N1):
                queue_number = 1
                value = self.__get_waiting_q_size(queue_number)

                _, current_event = self.__get_current_service()

                if (current_event == EventType.START_SERVICE_1):
                    value = value + 1

                metric = Metric(MetricType.NQ1, value,
                                self.__current_timestamp, queue_number)
            elif (m == MetricType.W2):
                queue_number = 2
                departures = list(
                    filter(lambda x: x.type == EventType.DEPARTURE,
                           self.__events_current_round))
                departures.sort(key=lambda x: x.timestamp, reverse=True)
                last_departed_client = departures[0].client_id

                events_last_departed_client = list(
                    filter(
                        lambda x: x.client_id == last_departed_client and x.
                        type in [
                            EventType.END_SERVICE_1,
                            EventType.START_SERVICE_2, EventType.
                            HALT_SERVICE_2, EventType.DEPARTURE
                        ], self.__events_current_round))
                events_last_departed_client.sort(key=lambda x: x.timestamp)
                
                value = 0

                for i in range(0, len(events_last_departed_client)):
                    if(events_last_departed_client[i].type in [EventType.START_SERVICE_2]):
                        idle_interval = events_last_departed_client[i].timestamp - events_last_departed_client[i-1].timestamp
                        value = value + idle_interval
                
                metric = Metric(MetricType.W2, value,
                                self.__current_timestamp, queue_number, last_departed_client)
            elif (m == MetricType.X2):
                queue_number = 2
                departures = list(
                    filter(lambda x: x.type == EventType.DEPARTURE,
                           self.__events_current_round))
                departures.sort(key=lambda x: x.timestamp, reverse=True)
                last_departed_client = departures[0].client_id

                events_last_departed_client = list(
                    filter(
                        lambda x: x.client_id == last_departed_client and x.
                        type in [
                            EventType.START_SERVICE_2, EventType.
                            HALT_SERVICE_2, EventType.DEPARTURE
                        ], self.__events_current_round))
                events_last_departed_client.sort(key=lambda x: x.timestamp)
                
                value = 0

                for i in range(0, len(events_last_departed_client)):
                    if(events_last_departed_client[i].type in [EventType.HALT_SERVICE_2, EventType.DEPARTURE]):
                        idle_interval = events_last_departed_client[i].timestamp - events_last_departed_client[i-1].timestamp
                        value = value + idle_interval
                
                metric = Metric(MetricType.X2, value,
                                self.__current_timestamp, queue_number, last_departed_client)
            elif (m == MetricType.T2):
                queue_number = 2
                departures = list(
                    filter(lambda x: x.type == EventType.DEPARTURE,
                           self.__events_current_round))
                departures.sort(key=lambda x: x.timestamp, reverse=True)
                last_departure = departures[0]

                end_service_1 = list(
                    filter(
                        lambda x: x.type == EventType.END_SERVICE_1 and x.
                        client_id == last_departure.client_id,
                        self.__events_current_round))[0]

                value = last_departure.timestamp - end_service_1.timestamp
                metric = Metric(MetricType.T2, value, self.__current_timestamp,
                                queue_number, last_departure.client_id)
            elif (m == MetricType.NQ2):
                queue_number = 2
                value = self.__get_waiting_q_size(queue_number)
                metric = Metric(MetricType.NQ2, value,
                                self.__current_timestamp, queue_number)
            elif (m == MetricType.N2):
                queue_number = 2
                value = self.__get_waiting_q_size(queue_number)

                _, current_event = self.__get_current_service()

                if (current_event == EventType.START_SERVICE_2):
                    value = value + 1

                metric = Metric(MetricType.NQ1, value,
                                self.__current_timestamp, queue_number)

            if (metric != None):
                self.__metrics_current_round.append(metric)

    def __get_arrival_time(self):
        """Obtém o tempo de chegada de um novo cliente, a partir de uma distribuição exponencial com taxa self.__arrival_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de chegada."""

        return np.random.exponential(scale=1.0 / self.__arrival_rate)

    def __get_service_time(self):
        """Obtém o tempo de serviço de um cliente, a partir de uma distribuição exponencial com taxa self.__service_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de serviço."""
        return np.random.exponential(scale=1.0 / self.__service_rate)

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

        self.__events_current_round.append(event)

        self.__event_list_raw.append({
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

        self.__event_list_raw.append({
            'reference': 'dequeue',
            'queue_number': queue_number,
            'timestamp': self.__current_timestamp,
            'client_id': next_client[0],
            'remaining_service_time': next_client[1],
            'round': self.__current_round
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

        self.__event_list_raw.append({
            'reference': 'enqueue',
            'queue_number': queue_number,
            'timestamp': self.__current_timestamp,
            'client_id': client_id,
            'remaining_service_time': remaining_service_time,
            'in_the_front': in_the_front,
            'round': self.__current_round
        })

        if (in_the_front):
            self.__waiting_qs[queue_number - 1].insert(
                0, (client_id, remaining_service_time))
        else:
            self.__waiting_qs[queue_number - 1].append(
                (client_id, remaining_service_time))

    def __remove_current_service_departure(self):
        """Remove a partida do sistema agendada para o cliente atualmente em serviço.\n
        Essa função só é chamada em casos em que há preempção de serviço."""
        current_client_id, _ = self.__get_current_service()

        departures_current_service = list(
            filter(
                lambda x: x.type == EventType.DEPARTURE and x.client_id ==
                current_client_id and x.queue_number == 2, self.__event_q))

        self.__event_q.remove(departures_current_service[0])

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

        next_arrival_time = \
            self.__current_timestamp + self.__get_arrival_time()

        if (next_arrival_time <= self.__system_max_arrival_time):
            self.__enqueue_event(
                Event(timestamp=next_arrival_time,
                      type=EventType.ARRIVAL,
                      queue_number=1))

    def __handle_arrival(self, event: Event):
        """Trata o evento do tipo EventType.ARRIVAL.\n
        Se não há serviço corrente, o cliente recém chegado inicia imediatamente o seu serviço(EventType.START_SERVICE_1).\n
        Se o serviço corrente é oriundo da fila de espera 1, o cliente é inserido na fila de espera 1.\n
        Caso o serviço corrente seja oriundo da fila de espera 2, o serviço desse cliente é interrompido(EventType.HALT_SERVICE_2), 
        e o cliente recém chegado inicia o serviço imediatamente."""

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
            #enfileira cliente na fila 1
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

        self.__schedule_next_arrival()
        self.__generate_metrics([MetricType.NQ1])

    def __handle_start_service_1(self, event: Event):
        """Trata o evento do tipo EventType.START_SERVICE_1.\n
        O cliente é removido da fila de espera 1.\n
        É obtido o tempo do serviço, e agendada o evento de término do serviço(EventType.END_SERVICE_1)."""

        next_client, _ = self.__dequeue_from_waiting_q(event.queue_number)

        self.__set_current_service(next_client, event.type)

        self.__enqueue_event(
            Event(timestamp=self.__current_timestamp +
                  self.__get_service_time(),
                  type=EventType.END_SERVICE_1,
                  queue_number=1,
                  client_id=event.client_id))

        self.__generate_metrics([MetricType.NQ1, MetricType.N1, MetricType.W1])

    def __handle_end_service_1(self, event: Event):
        """Trata o evento do tipo EventType.END_SERVICE_1.\n
        Caso as filas de esperas 1 e 2 estejam vazias, o cliente inicia o seu segundo serviço imediatamente(EventType.START_SERVICE_2).\n
        Caso haja clientes em alguma fila de espera, o cliente é enfileirado na fila de espera 2, e o serviço da fila mais prioritária é iniciado."""

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

        self.__generate_metrics([MetricType.X1, MetricType.T1])

    def __handle_start_service_2(self, event: Event):
        """Trata o evento do tipo EventType.START_SERVICE_2.\n
        O cliente é removido da fila de espera 2.\n
        É obtido o tempo do serviço, e agendada o evento de saída do sistema(EventType.DEPARTURE)."""

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

        self.__generate_metrics([MetricType.NQ2, MetricType.N2])

    def __handle_halt_service_2(self, event: Event):
        """Trata o evento do tipo EventType.HALT_SERVICE_2.\n
        O evento de saída do sistema do cliente atual é removido da fila de eventos, e o cliente é enfileirado na primeira posição da fila 2."""

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

        self.__generate_metrics([MetricType.NQ2])

    def __handle_departure(self, event: Event):
        """Trata o evento do tipo EventType.DEPARTURE.\n
        O cliente é removido do serviço corrente, e o cliente da primeira posição da fila mais prioritária tem o serviço iniciado."""

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

        self.__current_service = None

        self.__generate_metrics([MetricType.W2, MetricType.X2, MetricType.T2])

    def __save_event_list_raw(self):
        """Salva o evento no log de eventos."""

        if (os.path.exists(self.__event_list_raw_file)):
            os.remove(self.__event_list_raw_file)

        if (len(self.__event_list_raw) > 0):
            with open(self.__event_list_raw_file, 'a+',
                      newline='') as output_file:

                fieldnames = [
                    'reference', 'type', 'queue_number', 'timestamp',
                    'client_id', 'remaining_service_time', 'in_the_front',
                    'round'
                ]

                dict_writer = csv.DictWriter(output_file,
                                             fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(self.__event_list_raw)

    def run(self):
        """Loop principal do simulador.\n
        Remove-se o evento na primeira posição da lista de eventos, e delega-se para a função de tratamento adequada.
        Ao final da execução de todas as rodadas, salva o log de eventos no arquivo .csv"""

        try:
            for round_number in range(0, self.__number_of_rounds):
                #print(self.__metrics_accumulated)
                self.__reset_simulation_variables()

                #enfileirando a primeira chegada na fila 1
                self.__enqueue_event(
                    Event(timestamp=self.__current_timestamp +
                          self.__get_arrival_time(),
                          type=EventType.ARRIVAL,
                          queue_number=1))

                self.__current_round = round_number

                while (len(self.__event_q) > 0):
                    event: Event = self.__dequeue_event()

                    self.__current_timestamp = event.timestamp

                    #print(event)

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
                
        finally:
            self.__save_event_list_raw()
