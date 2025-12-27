from src.airliner_service.aeroplane.aeroplane import AeroPlane

aero_boy1: AeroPlane = AeroPlane(airlines_name = 'American Airlines' , airlines_type= 'Business',
                                 maker= 'AA', model= 2010,
                                 seating_capacity=250, fuel_capacity=500000)
print(aero_boy1)

aero_boy2: AeroPlane = AeroPlane(airlines_type= 'Business',
                                 maker= 'AA', model= 2010,
                                 seating_capacity=250, fuel_capacity=500000)
print(aero_boy2)