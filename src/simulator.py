import json
from models.event import Event
from models.event_type import EventType
import heapq
import os
import numpy as np

class Simulator:
    def __init__(self):
        self.__event_history_file = './event_history.json'

        self.__event_queue: list[Event] = []

        self.__event_history: list[Event] = []

        self.__arrival_interval_time_rate = 4.5
        
        self.__service_time_rate = 10

        #tempo máximo de chegada de pessoas no sistema(tempo de funcionamento da loja)
        self.__system_max_arrival_time = 50

        self.__current_timestamp = 0

        self.__current_service = None

    #insere um evento na fila de eventos
    def __enqueue_event(self, event: Event):
        heapq.heappush(self.__event_queue, event)

    #remove um evento na fila de eventos
    def __dequeue_event(self) -> Event:
        event = heapq.heappop(self.__event_queue)

        #adicionando no histórico de eventos
        self.__event_history.append(event)

        return event

    #realizando flush do histórico de eventos
    def __flush_event_history(self):
        f1 = open(self.__event_history_file, 'a+')

        try:
            event_history_list = []

            file_contents = f1.read()

            if(not(not(file_contents))):
                event_history_list = json.loads(file_contents)

            for event in self.__event_history:
                event_history_list.append(event.as_dict())
            
            f1.write(json.dumps(event_history_list))
            
            self.__event_history.clear()
        finally:
            f1.close()

    #get an arrival time, given the poisson distribution
    def __get_arrival_time(self):
        #return self.__arrival_interval_time_rate
        return np.random.exponential(scale=self.__arrival_interval_time_rate) 
    
    #get an service time, given the exponential distribution
    def __get_service_time(self):
        #return self.__service_time_rate
        return np.random.exponential(scale=self.__service_time_rate)

    def __get_end_of_current_service(self):
        end_of_current_service = \
                    list(filter(lambda x: x.type == EventType.DEPARTURE \
                        and x.id == self.__current_service.id
                        and x.queue_number == self.__current_service.queue_number, self.__event_queue))[0].timestamp
        
        return end_of_current_service

    #tratando os eventos do tipo EventType.ARRIVAL
    def __handle_arrival(self, event: Event):
        self.__current_timestamp = event.timestamp
        
        #agenda a próxima chegada na fila 1
        def schedule_next_arrival():
            next_arrival_time = self.__current_timestamp + self.__get_arrival_time()

            if(next_arrival_time <= self.__system_max_arrival_time):
                self.__enqueue_event(\
                    Event(timestamp=next_arrival_time,\
                        type=EventType.ARRIVAL, queue_number=1))

        if(event.queue_number == 1):
            if(self.__current_service == None):
                #agenda a saída do cliente atual da fila 1
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + self.__get_service_time(),\
                        type=EventType.DEPARTURE, queue_number=1, id=event.id))

                schedule_next_arrival()

                self.__current_service = event
            elif(self.__current_service.queue_number == 1):
                self.__enqueue_event(\
                        Event(timestamp=self.__get_end_of_current_service(),\
                            type=EventType.ARRIVAL, queue_number=1, id=event.id))
            else:
                remaining_service_time = \
                    self.__get_end_of_current_service() - self.__current_timestamp

                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp,\
                        type=EventType.ARRIVAL, queue_number=2,\
                             id=self.__current_service.id,\
                                 remaining_service_time=remaining_service_time))

                #agenda a saída do cliente do evento atual da fila 1
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + self.__get_service_time(),\
                        type=EventType.DEPARTURE, queue_number=1, id=event.id))
                
                schedule_next_arrival()

                self.__current_service = event
        else:
            if(self.__current_service == None):
                service_time = None

                if(event.remaining_service_time != None):
                    service_time = event.remaining_service_time
                else:
                    service_time = self.__get_service_time()

                #agenda a saída do cliente atual da fila 2
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + service_time,\
                        type=EventType.DEPARTURE, queue_number=2, id=event.id))

                self.__current_service = event
            else:
                self.__enqueue_event(\
                        Event(timestamp=self.__get_end_of_current_service(),\
                            type=EventType.ARRIVAL, queue_number=2, id=event.id))

    def __handle_departure(self, event: Event):
        self.__current_timestamp = event.timestamp
        self.__current_service = None

        if(event.queue_number == 1):
            #agenda a chegada do cliente atual na fila 2
            self.__enqueue_event(\
                Event(timestamp=self.__current_timestamp,\
                    type=EventType.ARRIVAL, queue_number=2, id=event.id))

    #executa passos da simulação
    def run(self):
        if(os.path.exists(self.__event_history_file)):
            os.remove(self.__event_history_file)

        #enfileirando a primeira chegada na fila 1
        self.__enqueue_event(\
            Event(\
                timestamp=self.__current_timestamp + self.__get_arrival_time(), \
                    type=EventType.ARRIVAL, queue_number=1))
        
        try:
            while(len(self.__event_queue) > 0):
                self.__current_event: Event = self.__dequeue_event()
                print(self.__current_event)
                print(len(self.__event_queue))            
                
                if(self.__current_event.type == EventType.ARRIVAL):
                    self.__handle_arrival(self.__current_event)
                elif (self.__current_event.type == EventType.DEPARTURE):
                    self.__handle_departure(self.__current_event)
        finally:
            if(len(self.__event_history) > 0):
                    self.__flush_event_history()