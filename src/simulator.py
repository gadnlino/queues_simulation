from models.event import Event
from models.event_type import EventType
import heapq

class Simulator:
    def __init__(self):
        self.__event_queue = []
        self.__arrival_interval_time = 4
        self.__service_time = 10
        self.__max_events_buffered = 100
        self.__current_timestamp = 0
        self.__enqueue_event(\
            Event(timestamp=self.__current_timestamp, type=EventType.ARRIVAL, queue_number=1))

    #insere um evento na fila de eventos
    def __enqueue_event(self, event: Event):
        heapq.heappush(self.__event_queue, (event.timestamp, event))
        #self.__event_queue.put()

    #remove um evento na fila de eventos
    def __dequeue_event(self) -> Event:
        priority, event = heapq.heappop(self.__event_queue)
        return event

    #tratando os eventos do tipo EventType.ARRIVAL
    def __handle_arrival(self, event: Event):
        self.__current_timestamp = event.timestamp

        #agenda a próxima chegada na fila 1
        self.__enqueue_event(\
            Event(timestamp=self.__current_timestamp + self.__arrival_interval_time,\
                 type=EventType.ARRIVAL, queue_number=1))

        #agenda a saída do cliente atual da fila 1
        self.__enqueue_event(\
            Event(timestamp=self.__current_timestamp + self.__service_time,\
                 type=EventType.DEPARTURE, queue_number=1))

    def __handle_departure(self, event):
        #agenda a chegada do cliente atual na fila 2
        self.__enqueue_event(\
            Event(timestamp=self.__current_timestamp + 1,\
                 type=EventType.ARRIVAL, queue_number=2))

    def run(self):
        while(len(self.__event_queue) > 0):
            self.__current_event: Event = self.__dequeue_event()
            print(self.__current_event)
            
            if(self.__current_event.type == EventType.ARRIVAL):
                self.__handle_arrival(self.__current_event)
            elif (self.__current_event.type == EventType.DEPARTURE):
                self.__handle_departure(self.__current_event)