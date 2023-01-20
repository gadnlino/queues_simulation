import random
import math

ARRIVAL = 'ARRIVAL'
DEPARTURE = 'DEPARTURE'


class Simulator3:

    def __init__(self, save_raw_event_log_file=False) -> None:
        self.__event_q = []
        self.__waiting_qs = [[], []]
        self.remove_current_service()
        self.__current_timestamp = 0.0
        self.__client_counter = 1

        self.__arrival_process = 'exponential'
        self.__arrival_rate = 1.0

        self.__service_process = 'exponential'
        self.__service_rate = 1.0

        self.__interrupted_service = None

        self.__event_log = []
        self.__save_raw_event_log_file = save_raw_event_log_file

    def get_client_counter(self):
        current = self.__client_counter

        self.__client_counter += 1

        return current

    def schedule_new_system_arrival(self, ):
        arrival_time = self.get_arrival_time()
        self.insert_event(ARRIVAL, 1, self.__current_timestamp + arrival_time,
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

    def get_arrival_time(self):
        """Obtém o tempo de chegada de um novo cliente, a partir de uma distribuição exponencial com taxa self.__arrival_rate.

        Returns
        ----------
        time: float
            Uma amostra de uma variável exponencial, representando um tempo de chegada."""

        if (self.__arrival_process == 'exponential'):
            u = random.random()
            return math.log(u) / (-self.__arrival_rate)
            #return np.random.exponential(scale=1.0 / self.__arrival_rate)
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
            #return np.random.exponential(scale=1.0 / self.__service_rate)
        elif (self.__service_process == 'deterministic'):
            return self.__service_time

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
                    self.__waiting_qs[0].append(event_client)
                elif (service_queue == 2):
                    self.remove_current_service_system_departure_event()
                    self.set_interrupted_service(
                        self.__current_service['client'],
                        self.__current_service['queue'],
                        self.__current_service['start_time'],
                        self.__current_service['service_time'])
                    self.remove_current_service()
                    self.__waiting_qs[1].insert(0, service_client)

                    service_time = self.get_service_time()
                    self.set_current_service(event_client, 1, service_time)
                    self.insert_event(DEPARTURE, 1,
                                      self.__current_timestamp + service_time,
                                      event_client)

            self.schedule_new_system_arrival()
        elif (event_type == ARRIVAL and event_queue == 2):
            self.__waiting_qs[1].append(event_client)

            if (len(self.__waiting_qs[0]) == 0
                    and self.__current_service == None):
                next_client_id = self.__waiting_qs[1].pop(0)

                service_time = None

                if(self.__interrupted_service != None and self.__interrupted_service['client'] == next_client_id):
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
                next_client_id = self.__waiting_qs[0].pop(0)
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
                next_client_id = self.__waiting_qs[0].pop(0)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 1, service_time)
                self.insert_event(DEPARTURE, 1,
                                  self.__current_timestamp + service_time,
                                  next_client_id)
            elif (len(self.__waiting_qs[1]) > 0):
                next_client_id = self.__waiting_qs[1].pop(0)
                service_time = self.get_service_time()
                self.set_current_service(next_client_id, 2, service_time)
                self.insert_event(DEPARTURE, 2,
                                  self.__current_timestamp + service_time,
                                  next_client_id)

    def run(self, ):

        self.schedule_new_system_arrival()

        while (len(self.__event_q) > 0):
            event = self.__event_q.pop(0)

            if (self.__save_raw_event_log_file):
                self.__event_log.append(event)

            self.__current_timestamp = event['event_timestamp']

            print(event, self.__current_service)

            self.handle_event(event)