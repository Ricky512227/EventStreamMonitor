#!/usr/bin/env python3
"""
Script to create test data in the database
"""
import requests
import json
import time

BASE_URL = "http://localhost:5001"
REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/eventstreammonitor/users/register"

# Required headers based on schema
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Host": "localhost:5001",
    "User-Agent": "test-data-creator/1.0",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate"
}

# Test users to create
test_users = [
    {
        "username": "admin_user",
        "firstName": "Admin",
        "lastName": "User",
        "email": "admin@eventstreammonitor.com",
        "password": "AdminPass123!",
        "dateOfBirth": "1985-01-01"
    },
    {
        "username": "pilot_john",
        "firstName": "John",
        "lastName": "Pilot",
        "email": "john.pilot@eventstreammonitor.com",
        "password": "PilotPass456!",
        "dateOfBirth": "1990-05-15"
    },
    {
        "username": "steward_mary",
        "firstName": "Mary",
        "lastName": "Steward",
        "email": "mary.steward@eventstreammonitor.com",
        "password": "StewardPass789!",
        "dateOfBirth": "1992-08-20"
    },
    {
        "username": "passenger_alice",
        "firstName": "Alice",
        "lastName": "Passenger",
        "email": "alice.passenger@example.com",
        "password": "PassengerPass123!",
        "dateOfBirth": "1995-12-10"
    },
    {
        "username": "passenger_bob",
        "firstName": "Bob",
        "lastName": "Traveler",
        "email": "bob.traveler@example.com",
        "password": "TravelerPass456!",
        "dateOfBirth": "1988-07-25"
    }
]

def create_user(user_data):
    """Create a user via API"""
    try:
        response = requests.post(
            REGISTER_ENDPOINT,
            json=user_data,
            headers=headers,
            timeout=10
        )

        if response.status_code == 201:
            print(f" Successfully created user: {user_data['username']}")
            return True
        elif response.status_code == 400:
            print(f" User might already exist: {user_data['username']} (Status: 400)")
            return False
        else:
            print(f" Failed to create user: {user_data['username']} (Status: {response.status_code})")
            print(f"  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f" Error creating user {user_data['username']}: {str(e)}")
        return False

def main():
    print("="*60)
    print("CREATING TEST DATA IN DATABASE")
    print("="*60)
    print(f"Endpoint: {REGISTER_ENDPOINT}\n")

    success_count = 0
    total_count = len(test_users)

    for user_data in test_users:
        if create_user(user_data):
            success_count += 1
        time.sleep(0.5)  # Small delay between requests

    print("\n" + "="*60)
    print(f"SUMMARY: Created {success_count}/{total_count} users")
    print("="*60)

    # Verify by querying database
    print("\nTo verify, run:")
    print("docker-compose exec registration-db psql -U airlineradmin -d REGISTRATIONS -c 'SELECT \\\"ID\\\", \\\"Username\\\", \\\"Email\\\" FROM users;'")

if __name__ == "__main__":
    main()
