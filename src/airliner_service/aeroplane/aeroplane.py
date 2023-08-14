from src.airliner_service.airiner.airline import Airline

class AeroPlane(Airline):
    def __init__(self, airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity):
        """
        :rtype: object
        """
        # airliner_logger.info("Received :: airlines_name :: {0}, airlines_type :: {1}, maker :: {2}, model:: {3} , seating_capacity :: {4}, fuel_capacity :: {5}".format(airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity))
        self.airlines_type = airlines_type + ' ' + 'AeroPlanes'
        self.aircraft_type = 'AeroPlanes'
        # airliner_logger.info("Assigned :: airlines_type - {0}, aircraft_type - {1}".format(self.airlines_type, self.aircraft_type))
        super().__init__(airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity)
        # airliner_logger.info("Assigned :: airlines_name :: {0},airlines_type :: {1}, aircraft_type :: {2}, maker :: {3}"", model:: {4}, seating_capacity :: {5}, fuel_capacity :: {6}".format(self.airlines_name,self.airlines_type, self.aircraft_type, self.maker, self.model, self.seating_capacity, self.fuel_capacity))

    def __repr__(self):
        return f"airlines_name :: {self.airlines_name}, airlines_type :: {self.airlines_type}, aircraft_type :: {self.aircraft_type}," \
               f" maker :: {self.maker}, model :: {self.model}," \
               f" seating_capacity :: {self.seating_capacity}," \
               f" fuel_capacity :: {self.fuel_capacity}, airlines_type :: {self.airlines_type}," \
               f" created_at :: {self.created_at}, updated_at :: {self.updated_at}"


