import datetime
class Airline:
    aircraft_type = None
    created_at = str(datetime.datetime.now())
    updated_at = str(datetime.datetime.now())
    def __init__(self, airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity) -> None:
        """
        :rtype: object
        """
        # #airliner_logger.info("Received Airline.__init__ :: airlines_name :: {0},airlines_type :: {1}, maker :: {2}, model:: {3}, seating_capacity :: {4}, fuel_capacity :: {5}".format(airlines_name, airlines_type, maker, model, seating_capacity, fuel_capacity))
        self.airlines_name = airlines_name
        self.airlines_type = airlines_type
        self.maker = maker
        self.model = model
        self.seating_capacity = seating_capacity
        self.fuel_capacity = fuel_capacity
        # #airliner_logger.info("Assign Airline.__init__ :: airlines_name :: {0},airlines_type :: {1}, maker :: {2}, model:: {3}, seating_capacity :: {4}, fuel_capacity :: {5}".format(self.airlines_name, self.airlines_type,self.maker, self.model, self.seating_capacity, self.fuel_capacity))

    def set_airlines_name(self, airlines_name):
        # #airliner_logger.info("Received airlines_name :: {0}".format(airlines_name))
        self.airlines_name = airlines_name
        # #airliner_logger.info("Setting airlines_name :: {0}".format(self.airlines_name))
        return self.airlines_name

    def get_airlines_name(self):
        #airliner_logger.info("Fetching airlines_name :: {0}".format(self.airlines_name))
        return self.airlines_name

    def set_airlines_type(self, airlines_type):
        #airliner_logger.info("Received airlines_type :: {0}".format(airlines_type))
        self.airlines_type = airlines_type
        #airliner_logger.info("Setting airlines_type :: {0}".format(self.airlines_type))
        return self.airlines_type

    def get_airlines_type(self):
        #airliner_logger.info("Fetching airlines_type :: {0}".format(self.airlines_type))
        return self.airlines_type

    def set_model(self, model):
        #airliner_logger.info("Received model :: {0}".format(model))
        self.model = model
        #airliner_logger.info("Setting model :: {0}".format(self.model))
        return self.model

    def get_model(self):
        #airliner_logger.info("Fetching model :: {0}".format(self.model))
        return self.model

    def get_fuel_capacity(self):
        #airliner_logger.info("Fetching fuel_capacity :: {0}".format(self.fuel_capacity))
        return self.fuel_capacity

    def set_fuel_capacity(self, fuel_capacity):
        #airliner_logger.info("Received fuel_capacity :: {0}".format(fuel_capacity))
        self.fuel_capacity = fuel_capacity
        #airliner_logger.info("Setting model :: {0}".format(self.fuel_capacity))
        return self.fuel_capacity

