import bisect
import heapq
import json
import os

import numpy as np

from models.event import Event
from models.event_type import EventType

class Simulator:
    def __init__(self):
        self.__q_events: list[Event] = []

        self.__q_events_history: list[Event] = []

        self.__q_events_history_file = './q_events_history.json'

        self.__service_events_history : list[ServiceEvent] = []

        self.__service_events_history_file = './service_events_history.json'

        self.__utilization_pct = 0.2

        #tempo máximo de chegada de pessoas no sistema(tempo de funcionamento da loja)
        self.__system_max_arrival_time = 10
        
        self.__service_rate = 1

        self.__arrival_rate = 1/(self.__utilization_pct * self.__service_rate)

        self.__current_timestamp = 0.0

        self.__current_service = None

    #insere um evento na fila de eventos
    def __enqueue_event(self, event: Event):
        bisect.insort(self.__q_events, event)

    #remove um evento na fila de eventos
    def __dequeue_event(self) -> Event:
        event = self.__q_events[0]

        #adicionando no histórico de eventos
        self.__q_events_history.append(event)

        self.__q_events.pop(0)

        return event

    #realizando flush do histórico de eventos
    def __save_event_history(self, event_list, out_file):
        f1 = open(out_file, 'a+')

        try:
            event_history_list = []

            file_contents = f1.read()

            if(not(not(file_contents))):
                event_history_list = json.loads(file_contents)

            for event in event_list:
                event_history_list.append(event.as_dict())
            
            f1.write(json.dumps(event_history_list))
        finally:
            f1.close()

    #get an arrival time, given the poisson distribution(exponential inter arrivals)
    def __get_arrival_time(self):
        return np.random.exponential(scale=1.0/self.__arrival_rate) 
    
    #get an service time, given the exponential distribution
    def __get_service_time(self):
        return np.random.exponential(scale=1.0/self.__service_rate)

    #determine if and arrive should occur, based on a utilization factor
    def __should_arrive(self):
        return True
        #return np.random.uniform(low=0, high=1) > 1 - self.__utilization

    def __remove_current_service_departure(self):
        departures_current_service = list(filter(lambda x: x.type == EventType.DEPARTURE \
                        and x.client_id == self.__current_service.client_id
                        and x.queue_number == self.__current_service.queue_number, self.__q_events))

        self.__q_events.remove(departures_current_service[0])

    def __get_end_of_current_service(self):
        departures_current_service = list(filter(lambda x: x.type == EventType.DEPARTURE \
                        and x.client_id == self.__current_service.client_id
                        and x.queue_number == self.__current_service.queue_number, self.__q_events))
                        
        departures_current_service.sort(key= lambda x : x.timestamp)

        end_of_current_service = departures_current_service[0].timestamp
        
        return end_of_current_service

    #tratando os eventos do tipo EventType.ARRIVAL
    def __handle_arrival(self, event: Event):
        self.__current_timestamp = event.timestamp
        
        #agenda a próxima chegada na fila 1
        def schedule_next_arrival():
            next_arrival_time = self.__current_timestamp + self.__get_arrival_time()

            if(next_arrival_time <= self.__system_max_arrival_time and self.__should_arrive()):
                self.__enqueue_event(\
                    Event(timestamp=next_arrival_time,\
                        type=EventType.ARRIVAL, queue_number=1))

        should_schedule_next_arrival = False

        if(event.queue_number == 1):
            if(self.__current_service == None): #serviço livre, posso processar cliente atual
                print('caso 1')
                
                #agenda a saída do cliente atual da fila 1
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + self.__get_service_time(),\
                        type=EventType.DEPARTURE, queue_number=event.queue_number, client_id=event.client_id))

                should_schedule_next_arrival = True

                self.__current_service = event

                self.__service_events_history.append(
                    ServiceEvent(type=ServiceEventType.SERVICE_STARTED, timestamp=self.__current_timestamp, client_id=event.client_id, queue_number=event.queue_number))
            elif(self.__current_service.queue_number == 1):#serviço ocupado por alguem da fila 1, agendo uma nova chegada desse cliente para o final do serviço atual
                print('caso 2')
                
                self.__enqueue_event(\
                        Event(timestamp=self.__get_end_of_current_service(),\
                            type=EventType.ARRIVAL, queue_number=event.queue_number, client_id=event.client_id))
            else:#serviço ocupado por alguem da fila 2, agendo uma nova chegada desse cliente para o final do serviço atual
                print('caso 3')
                end_of_current_service = self.__get_end_of_current_service()
                remaining_service_time = \
                    end_of_current_service - self.__current_timestamp

                self.__service_events_history.append(
                    ServiceEvent(type=ServiceEventType.SERVICE_HALTED, \
                        timestamp=self.__current_timestamp, \
                            client_id=self.__current_service.client_id, \
                                queue_number=self.__current_service.queue_number))

                #remover partida posterior do serviço que veio da fila 2 e agora foi interrompido
                self.__remove_current_service_departure()

                self.__enqueue_event(\
                    Event(timestamp=end_of_current_service,\
                        type=EventType.ARRIVAL, queue_number=self.__current_service.queue_number,\
                             client_id=self.__current_service.client_id,\
                                 remaining_service_time=remaining_service_time))

                #agenda a saída do cliente do evento atual da fila 1
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + self.__get_service_time(),\
                        type=EventType.DEPARTURE, queue_number=event.queue_number, client_id=event.client_id))
                
                should_schedule_next_arrival = True

                self.__current_service = event

                self.__service_events_history.append(
                    ServiceEvent(type=ServiceEventType.SERVICE_STARTED, timestamp=self.__current_timestamp, client_id=event.client_id, queue_number=event.queue_number))
        else:
            if(self.__current_service == None):
                print('caso 4')
                service_time = None

                if(event.remaining_service_time != None):
                    service_time = event.remaining_service_time
                else:
                    service_time = self.__get_service_time()

                #agenda a saída do cliente atual da fila 2
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + service_time,\
                        type=EventType.DEPARTURE, queue_number=event.queue_number, client_id=event.client_id))

                self.__current_service = event

                self.__service_events_history.append(
                    ServiceEvent(type=ServiceEventType.SERVICE_STARTED, timestamp=self.__current_timestamp, client_id=event.client_id, queue_number=event.queue_number))

            else:
                print('caso 5')
                
                self.__enqueue_event(\
                        Event(timestamp=self.__get_end_of_current_service(),\
                            type=EventType.ARRIVAL, queue_number=event.queue_number, client_id=event.client_id))

        if(should_schedule_next_arrival):
            schedule_next_arrival()

    def __handle_departure(self, event: Event):
        self.__current_timestamp = event.timestamp

        self.__service_events_history.append(
            ServiceEvent(type=ServiceEventType.SERVICE_FINISHED, timestamp=self.__current_timestamp, client_id=self.__current_service.client_id, queue_number=self.__current_service.queue_number))

        self.__current_service = None

        if(event.queue_number == 1):
            #agenda a chegada do cliente atual na fila 2
            self.__enqueue_event(\
                Event(timestamp=self.__current_timestamp,\
                    type=EventType.ARRIVAL, queue_number=2, client_id=event.client_id))

    #executa passos da simulação
    def run(self):
        #enfileirando a primeira chegada na fila 1
        self.__enqueue_event(\
            Event(\
                timestamp=self.__current_timestamp + self.__get_arrival_time(), \
                    type=EventType.ARRIVAL, queue_number=1))
        
        try:
            while(len(self.__q_events) > 0):
                event: Event = self.__dequeue_event()

                print(event.timestamp)

                if(event.type == EventType.ARRIVAL):
                    self.__handle_arrival(event)
                elif (event.type == EventType.DEPARTURE):
                    self.__handle_departure(event)
        finally:
            if(os.path.exists(self.__q_events_history_file)):
                os.remove(self.__q_events_history_file)

            if(len(self.__q_events_history) > 0):
                    self.__save_event_history(self.__q_events_history, self.__q_events_history_file)
                    self.__q_events_history.clear()

            if(os.path.exists(self.__service_events_history_file)):
                os.remove(self.__service_events_history_file)

            if(len(self.__service_events_history) > 0):
                    self.__save_event_history(self.__service_events_history, self.__service_events_history_file)
                    self.__service_events_history.clear()
