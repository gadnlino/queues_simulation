import bisect
import heapq
import json
import os

import numpy as np

from models.event import Event
from models.event_type import EventType


class Simulator:
    def __init__(self):
        self.__event_q = []

        self.__event_q_history = []
        
        self.__number_of_qs = 2

        self.__waiting_qs: list[list[Event]] = \
            list(map(lambda _ : list(), range(0, self.__number_of_qs)))

        self.__utilization_pct = 0.2

        #tempo máximo de chegada de pessoas no sistema(tempo de funcionamento da loja)
        self.__system_max_arrival_time = 10
        
        self.__service_rate = 1

        self.__arrival_rate = 1/(self.__utilization_pct * self.__service_rate)

        self.__current_timestamp = 0.0

        self.__current_service : Event = None

    #get an arrival time, given the poisson distribution(exponential inter arrivals)
    def __get_arrival_time(self):
        return np.random.exponential(scale=1.0/self.__arrival_rate) 
    
    #get an service time, given the exponential distribution
    def __get_service_time(self):
        return np.random.exponential(scale=1.0/self.__service_rate)

    #insere um evento na fila de eventos
    def __enqueue_event(self, event: Event):
        bisect.insort(self.__event_q, event)

    #remove um evento na fila de eventos
    def __dequeue_event(self) -> Event:
        event = self.__event_q[0]

        #adicionando no histórico de eventos
        self.__event_q_history.append(event)

        self.__event_q.pop(0)

        return event

    def __handle_arrival(self, event: Event):
        self.__current_timestamp = event.timestamp

        #agenda a próxima chegada na fila 1
        def schedule_next_arrival():
            next_arrival_time = self.__current_timestamp + self.__get_arrival_time()

            if(next_arrival_time <= self.__system_max_arrival_time):
                self.__enqueue_event(\
                    Event(timestamp=next_arrival_time,\
                        type=EventType.ARRIVAL, queue_number=1))

        if(self.__current_service == None):                      
           self.__event_q.insert(0, \
               Event(timestamp=self.__current_timestamp,type=EventType.START_SERVICE_1, queue_number=1))

           schedule_next_arrival()
        elif(self.__current_service.queue_number == 1):
            #enfileira cliente
            self.__waiting_qs[event.queue_number-1].append(event)
        else:
            self.__event_q.insert(0, \
               Event(timestamp=self.__current_timestamp,type=EventType.START_SERVICE_1, queue_number=1))

            self.__event_q.insert(0, \
               Event(timestamp=self.__current_timestamp,type=EventType.HALT_SERVICE_2, queue_number=2))

            #enfileira novamente o servico atual na fila 2
            # self.__waiting_qs[self.__current_service.queue_number-1]\
            #     .insert(0, self.__current_service)

            # self.__current_service = event

            schedule_next_arrival()

    def __handle_start_service_1(self, event: Event):
        next_client = self.__waiting_qs[event.queue_number-1][0]
        self.__waiting_qs[event.queue_number-1].pop()
        self.__current_service = next_client

    def __handle_departure(self, event: Event):
        self.__current_timestamp = event.timestamp

        # self.__service_events_history.append(
        #     ServiceEvent(type=ServiceEventType.SERVICE_FINISHED, timestamp=self.__current_timestamp, client_id=self.__current_service.client_id, queue_number=self.__current_service.queue_number))

        self.__current_service = None

        if(event.queue_number == 1):
            #agenda a chegada do cliente atual na fila 2
            self.__enqueue_event(\
                Event(timestamp=self.__current_timestamp,\
                    type=EventType.ARRIVAL, queue_number=2, client_id=event.client_id))

    def run(self):
        #enfileirando a primeira chegada na fila 1
        self.__enqueue_event(\
            Event(\
                timestamp=self.__current_timestamp + self.__get_arrival_time(), \
                    type=EventType.ARRIVAL, queue_number=1))
        
        try:
            while(len(self.__event_q) > 0):
                event: Event = self.__dequeue_event()

                print(event.timestamp)

                if(event.type == EventType.ARRIVAL):
                    self.__handle_arrival(event)
                elif (event.type == EventType.START_SERVICE_1):
                    self.__handle_departure(event)
                elif (event.type == EventType.END_SERVICE_1):
                    self.__handle_departure(event)
                elif (event.type == EventType.START_SERVICE_2):
                    self.__handle_departure(event)
                elif (event.type == EventType.HALT_SERVICE_2):
                    self.__handle_departure(event)
                elif (event.type == EventType.DEPARTURE):
                    self.__handle_departure(event)
        finally:
            pass
            # if(os.path.exists(self.__q_events_history_file)):
            #     os.remove(self.__q_events_history_file)

            # if(len(self.__q_events_history) > 0):
            #         self.__save_event_history(self.__q_events_history, self.__q_events_history_file)
            #         self.__q_events_history.clear()

            # if(os.path.exists(self.__service_events_history_file)):
            #     os.remove(self.__service_events_history_file)

            # if(len(self.__service_events_history) > 0):
            #         self.__save_event_history(self.__service_events_history, self.__service_events_history_file)
            #         self.__service_events_history.clear()
