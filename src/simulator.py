import json
from models.event import Event
from models.queue_event_type import QueueEventType
import heapq
import os
import numpy as np
import bisect

class Simulator:
    def __init__(self):
        self.__event_history_file = './event_history.json'

        self.__event_queue: list[Event] = []

        self.__event_history: list[Event] = []

        self.__arrival_interval_time_rate = 1
        
        self.__service_time_rate = 1

        #tempo máximo de chegada de pessoas no sistema(tempo de funcionamento da loja)
        self.__system_max_arrival_time = 10000

        self.__current_timestamp = 0.0

        self.__current_service = None

        self.__utilization = 0.2

    #insere um evento na fila de eventos
    def __enqueue_event(self, event: Event):
        #heapq.heappush(self.__event_queue, event)
        bisect.insort(self.__event_queue, event)

    #remove um evento na fila de eventos
    def __dequeue_event(self) -> Event:
        #event = heapq.heappop(self.__event_queue)

        event = self.__event_queue[0]

        #adicionando no histórico de eventos
        self.__event_history.append(event)

        self.__event_queue.pop(0)

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

    #determine if and arrive should occur, based on a utilization factor
    def __should_arrive(self):
        return True
        #return np.random.uniform(low=0, high=1) > 1 - self.__utilization

    def __get_end_of_current_service(self):
        departures_current_client = list(filter(lambda x: x.type == QueueEventType.DEPARTURE \
                        and x.client_id == self.__current_service.client_id
                        and x.queue_number == self.__current_service.queue_number, self.__event_queue))

        if(len(departures_current_client) < 1):
            print()

        departures_current_client.sort(key= lambda x : x.timestamp)

        end_of_current_service = departures_current_client[0].timestamp
        
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
                        type=QueueEventType.ARRIVAL, queue_number=1))

        should_schedule_next_arrival = False

        if(event.queue_number == 1):
            if(self.__current_service == None): #serviço livre, posso processar cliente atual
                print('caso 1')
                #agenda a saída do cliente atual da fila 1
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + self.__get_service_time(),\
                        type=QueueEventType.DEPARTURE, queue_number=event.queue_number, client_id=event.client_id))

                should_schedule_next_arrival = True

                self.__current_service = event
            elif(self.__current_service.queue_number == 1):#serviço ocupado por alguem da fila 1, agendo uma nova chegada desse cliente para o final do serviço atual
                print('caso 2')
                print(self.__current_service)
                self.__enqueue_event(\
                        Event(timestamp=self.__get_end_of_current_service(),\
                            type=QueueEventType.ARRIVAL, queue_number=event.queue_number, client_id=event.client_id))
            else:#serviço ocupado por alguem da fila 2, agendo uma nova chegada desse cliente para o final do serviço atual
                print('caso 3')
                end_of_current_service = self.__get_end_of_current_service()
                remaining_service_time = \
                    end_of_current_service - self.__current_timestamp

                self.__enqueue_event(\
                    Event(timestamp=end_of_current_service,\
                        type=QueueEventType.ARRIVAL, queue_number=self.__current_service.queue_number,\
                             client_id=self.__current_service.client_id,\
                                 remaining_service_time=remaining_service_time))

                #agenda a saída do cliente do evento atual da fila 1
                self.__enqueue_event(\
                    Event(timestamp=self.__current_timestamp + self.__get_service_time(),\
                        type=QueueEventType.DEPARTURE, queue_number=event.queue_number, client_id=event.client_id))
                
                should_schedule_next_arrival = True

                self.__current_service = event
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
                        type=QueueEventType.DEPARTURE, queue_number=event.queue_number, client_id=event.client_id))

                self.__current_service = event
            else:
                print('caso 5')
                print(self.__current_service)
                self.__enqueue_event(\
                        Event(timestamp=self.__get_end_of_current_service(),\
                            type=QueueEventType.ARRIVAL, queue_number=event.queue_number, client_id=event.client_id))

        if(should_schedule_next_arrival):
            schedule_next_arrival()

    def __handle_departure(self, event: Event):
        self.__current_timestamp = event.timestamp
        self.__current_service = None

        if(event.queue_number == 1):
            #agenda a chegada do cliente atual na fila 2
            self.__enqueue_event(\
                Event(timestamp=self.__current_timestamp,\
                    type=QueueEventType.ARRIVAL, queue_number=2, client_id=event.client_id))

    #executa passos da simulação
    def run(self):
        #enfileirando a primeira chegada na fila 1
        self.__enqueue_event(\
            Event(\
                timestamp=self.__current_timestamp + self.__get_arrival_time(), \
                    type=QueueEventType.ARRIVAL, queue_number=1))
        
        try:
            while(len(self.__event_queue) > 0):
                self.__current_event: Event = self.__dequeue_event()
                # print(self.__current_event)
                # print(len(self.__event_queue))            
                
                if(self.__current_event.type == QueueEventType.ARRIVAL):
                    self.__handle_arrival(self.__current_event)
                elif (self.__current_event.type == QueueEventType.DEPARTURE):
                    self.__handle_departure(self.__current_event)
        finally:
            if(os.path.exists(self.__event_history_file)):
                os.remove(self.__event_history_file)

            if(len(self.__event_history) > 0):
                    self.__flush_event_history()