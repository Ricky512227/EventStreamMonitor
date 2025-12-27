from src.airliner_service.aeroplane.aeroplane import AeroPlane


def test_create_aeroplane():
    test_aeroplane_1 = AeroPlane('American Airlines', 'Business', 'AA', 2010, 250, 500000)
    print("****")
    print(test_aeroplane_1.airlines_name, test_aeroplane_1.airlines_type, test_aeroplane_1.maker, test_aeroplane_1.model,test_aeroplane_1.seating_capacity, test_aeroplane_1.fuel_capacity)
    assert ('American Airlines', 'Business', 'AA', 2010, 250, 500000) == (test_aeroplane_1.airlines_name,test_aeroplane_1.airlines_type, test_aeroplane_1.maker, test_aeroplane_1.model, test_aeroplane_1.seating_capacity, test_aeroplane_1.fuel_capacity)
