ARRIVAL = 'ARRIVAL'
DEPARTURE = 'DEPARTURE'

class Simulator3:
    def __init__(self) -> None:
        self.__event_q = []
        self.__waiting_qs = [[],[]]
        self.__current_service = None
        self.__current_timestamp = 0.0
        self.__client_counter = 1
    
    def get_client_counter(self):
        current = self.__client_counter

        self.__client_counter += 1

        return current

    def schedule_new_system_arrival(self,):
        arrival_time = 1
        self.__event_q.append((ARRIVAL, 1, self.__current_timestamp + arrival_time, None))

    def remove_current_service_system_departure(self,):
        service_client, _ = self.__current_service

        self.__event_q = list(filter(lambda x: x[0] == DEPARTURE and x[1] == 2 and x[3] == service_client, self.__event_q))

    def handle_event(self, event):
        event_type = event[0]
        event_queue = event[1]
        event_timestamp = event[2]
        event_client = event[3]

        if(event_type == ARRIVAL and event_queue == 1):
            client_id = self.get_client_counter()

            if(self.__current_service == None):
                service_time = 1
                self.__current_service = (client_id, event_queue, service_time)
                self.__event_q.append((DEPARTURE, 1, self.__current_timestamp + service_time, client_id))
            else:
                service_client, service_queue, _ = self.__current_service
                if(service_queue == 1):
                    self.__waiting_qs[0].append(client_id)
                elif(service_queue == 2):
                    self.remove_current_service_system_departure()
                    self.__current_service = (client_id, event_queue)
                    self.__event_q.append((DEPARTURE, 1, self.__current_timestamp + service_time, client_id))
            
            self.schedule_new_system_arrival()
        elif(event_type == ARRIVAL and event_queue == 2):
            service_time = 1
            self.__current_service = (next_client_id, 1, service_time)
            self.__event_q.append((DEPARTURE, 2, self.__current_timestamp + service_time, next_client_id))
        elif(event_type == DEPARTURE and event_queue == 1):
            self.__current_service = None
            self.__waiting_qs[1].append(event_client)

            if(len(self.__waiting_qs[0]) > 0):
                next_client_id = self.__waiting_qs[0].pop(0)
                service_time = 1
                self.__current_service = (next_client_id, 1, service_time)
                self.__event_q.append((DEPARTURE, 1, self.__current_timestamp + service_time, next_client_id))
            
            self.__event_q.append((ARRIVAL, 1, self.__current_timestamp + service_time, next_client_id))
        elif(event_type == DEPARTURE and event_queue == 2):
            self.__current_service = None

    def run(self,):
        
        self.schedule_new_system_arrival()

        while(len(self.__event_q) > 0):
            event = self.__event_q.pop(0)
            self.__current_timestamp = event[2]

            print(event)

            self.handle_event(event)