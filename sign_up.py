import requests
import json


def signup_user(email, password, api_key):
    """
    Sign up a new user with Firebase
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print("User created successfully!")
        print(f"UID: {data['localId']}")
        print(f"Email: {data['email']}")
        print(f"ID Token: {data['idToken']}")
        return data
    else:
        print(f"Error: {response.status_code}")
        error_data = response.json()
        print(f"Error message: {error_data.get('error', {}).get('message', 'Unknown error')}")
        return None


def signin_user(email, password, api_key):
    """
    Sign in an existing user
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print("User signed in successfully!")
        print(f"ID Token: {data['idToken']}")
        return data['idToken']
    else:
        print(f"Error: {response.status_code}")
        error_data = response.json()
        print(f"Error message: {error_data.get('error', {}).get('message', 'Unknown error')}")
        return None


# Usage
if __name__ == "__main__":
    API_KEY = "AIzaSyBr97NgG9khklR0QkemyQP7I9_36qi6y7o"  # Get this from Firebase Console

    # Sign up new user
    email = "chaudhari.piyush@therealbrokerage.com"
    password = "Piyush@04"

    user_data = signup_user(email, password, API_KEY)

    if user_data:
        print("\n--- Now signing in with the same credentials ---")
        token = signin_user(email, password, API_KEY)

        if token:
            print(f"\nUse this token in Postman:")
            print(f"Authorization: Bearer {token}")