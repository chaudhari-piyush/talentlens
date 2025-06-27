import requests
import json


def get_firebase_token(email, password, api_key):
    """
    Get Firebase ID token using email/password
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
        return data['idToken']
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        return None


if __name__ == '__main__':
    # Usage
    API_KEY = "AIzaSyBr97NgG9khklR0QkemyQP7I9_36qi6y7o"
    EMAIL = "newuser@example.com"
    PASSWORD = "securePassword123"

    token = get_firebase_token(EMAIL, PASSWORD, API_KEY)
    if token:
        print("ID Token:")
        print(token)