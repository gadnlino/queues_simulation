import bisect
import heapq
import json
import os
import csv

import numpy as np

from models.event import Event
from models.event_type import EventType


class Simulator:

    def __init__(self):
        self.__event_list_raw_file = './event_list_raw.csv'

        self.__event_list_raw = []

        self.__number_of_qs = 2

        self.__utilization_pct = 0.99

        #tempo máximo de chegada de pessoas no sistema(tempo de funcionamento da loja)
        self.__system_max_arrival_time = 1000

        self.__service_rate = 1

        self.__arrival_rate = 1 / (self.__utilization_pct *
                                   self.__service_rate)

        self.__number_of_rounds = 3

        self.__current_round = 0
    
    def __reset_simulation_variables(self):
        #simulation variables

        self.__current_timestamp = 0.0

        self.__current_service = None

        self.__event_q: list[Event] = []

        self.__waiting_qs = list(
            map(lambda _: list(), range(0, self.__number_of_qs)))

    #get an arrival time, given the poisson distribution(exponential inter arrivals)
    def __get_arrival_time(self):
        return np.random.exponential(scale=1.0 / self.__arrival_rate)

    #get an service time, given the exponential distribution
    def __get_service_time(self):
        return np.random.exponential(scale=1.0 / self.__service_rate)

    #insere um evento na fila de eventos
    def __enqueue_event(self, event: Event, in_the_front=False):
        if (in_the_front):
            self.__event_q.insert(0, event)
        else:
            bisect.insort(self.__event_q, event)

    #remove um evento na fila de eventos
    def __dequeue_event(self) -> Event:
        event = self.__event_q.pop(0)

        self.__event_list_raw.append({
            'reference': 'event',
            **event.as_dict(), 
            'round': self.__current_round
        })

        return event

    def __dequeue_from_waiting_q(self, queue_number: int):
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
                               in_the_front=False):

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
        current_client_id, _ = self.__get_current_service()

        departures_current_service = list(
            filter(
                lambda x: x.type == EventType.DEPARTURE and x.client_id ==
                current_client_id and x.queue_number == 2, self.__event_q))

        self.__event_q.remove(departures_current_service[0])

    def __get_next_client_in_waiting_q(self, queue_number: int) -> int:
        return self.__waiting_qs[queue_number - 1][0]

    def __get_waiting_q_size(self, queue_number: int) -> int:
        return len(self.__waiting_qs[queue_number - 1])

    def __get_end_of_current_service(self):
        current_client_id, _ = self.__get_current_service()

        departures_current_service = list(filter(lambda x: x.type == EventType.DEPARTURE \
                        and x.client_id == current_client_id
                        and x.queue_number == 2, self.__event_q))

        departures_current_service.sort(key=lambda x: x.timestamp)

        end_of_current_service = departures_current_service[0].timestamp

        return end_of_current_service

    def __get_current_service(self):
        if (self.__current_service == None):
            return None, None

        return self.__current_service

    def __set_current_service(self, client_id: int,
                              source_event_type: EventType):
        self.__current_service = (client_id, source_event_type)

    def __schedule_next_arrival(self):
        next_arrival_time = \
            self.__current_timestamp + self.__get_arrival_time()

        if (next_arrival_time <= self.__system_max_arrival_time):
            self.__enqueue_event(
                Event(timestamp=next_arrival_time,
                      type=EventType.ARRIVAL,
                      queue_number=1))

    def __handle_arrival(self, event: Event):

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

    def __handle_start_service_1(self, event: Event):
        next_client, _ = self.__dequeue_from_waiting_q(event.queue_number)

        self.__set_current_service(next_client, event.type)

        self.__enqueue_event(
            Event(timestamp=self.__current_timestamp +
                  self.__get_service_time(),
                  type=EventType.END_SERVICE_1,
                  queue_number=1,
                  client_id=event.client_id))

    def __handle_end_service_1(self, event: Event):
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

    def __handle_start_service_2(self, event: Event):
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

    def __handle_halt_service_2(self, event: Event):
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

    def __handle_departure(self, event: Event):

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

        self.__schedule_next_arrival()

    def __save_event_list_raw(self):
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
        try:
            for round_number in range(0, self.__number_of_rounds):
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
