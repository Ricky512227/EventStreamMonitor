import requests
import json
import time

BASE_URL = "http://localhost:5002/api/v1/airliner/bookings"
HEADERS = {
    "Host": "localhost:5002",
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Postman-Token": "test-token"
}


def create_booking(user_id, flight_id, number_of_seats):
    """Create a booking"""
    payload = {
        "userId": user_id,
        "flightId": flight_id,
        "numberOfSeats": number_of_seats
    }
    print(f"\n============================================================")
    print(f"Creating booking for user {user_id}, flight {flight_id}")
    print(f"============================================================")
    try:
        response = requests.post(BASE_URL, headers=HEADERS, json=payload)
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response Body: {response.text}")
        return response.status_code, response.json() if response.status_code in [200, 201] else None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def get_booking(booking_id):
    """Get booking details"""
    url = f"{BASE_URL}/{booking_id}"
    print(f"\n============================================================")
    print(f"Getting booking: {booking_id}")
    print(f"============================================================")
    try:
        response = requests.get(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response Body: {response.text}")
        return response.status_code, response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def cancel_booking(booking_id):
    """Cancel a booking"""
    url = f"{BASE_URL}/{booking_id}/cancel"
    print(f"\n============================================================")
    print(f"Cancelling booking: {booking_id}")
    print(f"============================================================")
    try:
        response = requests.put(url, headers=HEADERS)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Response Body: {response.text}")
        return response.status_code, response.json() if response.status_code == 200 else None
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None, None
    except Exception as e:
        print(f"Error: {e}")
        return None, None


if __name__ == "__main__":
    print("============================================================")
    print("FLIGHT BOOKING SERVICE TESTS")
    print("============================================================")
    
    # Note: These tests assume flights and users exist in the database
    # In a real scenario, you'd need to create flights first
    
    # Test 1: Create booking (will fail if flight doesn't exist)
    print("\n[TEST 1] Creating booking...")
    status_1, booking_data = create_booking(1000, 1000, 2)
    
    if booking_data and "booking" in booking_data:
        booking_id = booking_data["booking"]["bookingId"]
        
        # Test 2: Get booking
        print("\n[TEST 2] Getting booking...")
        status_2, _ = get_booking(booking_id)
        
        # Test 3: Cancel booking
        print("\n[TEST 3] Cancelling booking...")
        status_3, _ = cancel_booking(booking_id)
        
        # Test 4: Try to get cancelled booking
        print("\n[TEST 4] Getting cancelled booking...")
        status_4, _ = get_booking(booking_id)
        
        # Summary
        print("\n============================================================")
        print("TEST SUMMARY")
        print("============================================================")
        passed = 0
        total = 4
        
        if status_1 in [200, 201]:
            print("Test 1 - Create Booking: ✓ PASSED")
            passed += 1
        else:
            print(f"Test 1 - Create Booking: ✗ FAILED (Status: {status_1})")
        
        if status_2 == 200:
            print("Test 2 - Get Booking: ✓ PASSED")
            passed += 1
        else:
            print(f"Test 2 - Get Booking: ✗ FAILED (Status: {status_2})")
        
        if status_3 == 200:
            print("Test 3 - Cancel Booking: ✓ PASSED")
            passed += 1
        else:
            print(f"Test 3 - Cancel Booking: ✗ FAILED (Status: {status_3})")
        
        if status_4 == 200:
            print("Test 4 - Get Cancelled Booking: ✓ PASSED")
            passed += 1
        else:
            print(f"Test 4 - Get Cancelled Booking: ✗ FAILED (Status: {status_4})")
        
        print(f"\nTotal: {passed}/{total} tests passed")
    else:
        print("\n⚠️  Booking creation failed. Make sure:")
        print("  1. Flight with ID 1000 exists in the database")
        print("  2. User with ID 1000 exists in the database")
        print("  3. Flight has available seats")

