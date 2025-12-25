# import requests
# import os
# import json
# from django.conf import settings
# from datetime import datetime, timedelta

# TOKEN_FILE = os.path.join(settings.BASE_DIR, "tatmeen_token.json")

# def save_token_data(data):
#     data["fetched_at"] = datetime.utcnow().isoformat()
#     with open(TOKEN_FILE, "w") as f:
#         json.dump(data, f)

# def load_token_data():
#     if os.path.exists(TOKEN_FILE):
#         with open(TOKEN_FILE) as f:
#             return json.load(f)
            
#     return {}

# def is_token_expired(token_data):
#     if not token_data:
#         return True
#     fetched_at = datetime.fromisoformat(token_data["fetched_at"])
#     expires_in = token_data.get("expires_in", 3600)
#     return datetime.utcnow() >= fetched_at + timedelta(seconds=expires_in - 60)

# def get_tatmeen_token():
#     token_data = load_token_data()
#     if token_data and not is_token_expired(token_data):
#         return token_data["access_token"]

#     # Try refresh if available
#     if token_data.get("refresh_token"):
#         try:
#             return refresh_tatmeen_token(token_data["refresh_token"])
#         except:
#             pass  # fallback to full re-auth

#     return fetch_new_token()

# def fetch_new_token():
#     url = "https://tatmeenapim.mohap.gov.ae/v1/auth"
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "apikey": settings.TATMEEN_API_KEY
#     }
#     data = {
#         "grant_type": "password",
#         "username": settings.TATMEEN_USERNAME,
#         "password": settings.TATMEEN_PASSWORD
#     }

#     res = requests.post(url, headers=headers, data=data)
#     res.raise_for_status()
#     token_data = res.json()
#     save_token_data(token_data)
#     return token_data["access_token"]

# def refresh_tatmeen_token(refresh_token):
#     url = "https://tatmeenapim.mohap.gov.ae/v1/auth"
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "apikey": settings.TATMEEN_API_KEY
#     }
#     data = {
#         "grant_type": "refresh_token",
#         "refresh_token": refresh_token
#     }

#     res = requests.post(url, headers=headers, data=data)
#     res.raise_for_status()
#     token_data = res.json()
#     save_token_data(token_data)
#     return token_data["access_token"]



import json
import os
from django.conf import settings
import requests
from datetime import datetime, timedelta

TOKEN_FILE = os.path.join(settings.BASE_DIR, "tatmeen_token.json")


def get_token_from_tatmeen():
    url = "https://tatmeenapim.mohap.gov.ae/v1/auth"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": settings.TATMEEN_API_KEY
    }

    data = {
        "username": settings.TATMEEN_USERNAME,
        "password": settings.TATMEEN_PASSWORD,
        "grant_type": settings.TATMEEN_GRANT_TYPE
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        token_data["expires_at"] = (datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat()
        save_token_data(token_data)
        return token_data
    else:
        raise Exception(f"Token request failed: {response.status_code} {response.text}")


def refresh_token(refresh_token_value):
    url = "https://tatmeenapim.mohap.gov.ae/v1/auth"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": settings.TATMEEN_API_KEY
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        token_data["expires_at"] = (datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))).isoformat()
        save_token_data(token_data)
        return token_data
    else:
        raise Exception(f"Token refresh failed: {response.status_code} {response.text}")


def save_token_data(token_data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f)


def load_token_data():
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None




# def get_valid_token():
#     token_data = load_token_data()
#     if token_data:
#         expires_at_str = token_data.get("expires_at")
#         if expires_at_str:
#             try:
#                 expires_at = datetime.fromisoformat(expires_at_str)
#                 if datetime.now() < expires_at:
#                     return token_data
#                 else:
#                     # Token expired, try to refresh
#                     if token_data.get("refresh_token"):
#                         return refresh_token(token_data["refresh_token"])
#             except ValueError:
#                 # Invalid datetime format — treat as no token
#                 pass
#     return get_token_from_tatmeen()


def get_valid_token():
    token_data = load_token_data()
    if token_data:
        expires_at_str = token_data.get("expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.now() < expires_at:
                    return token_data
                else:
                    # Token expired, try to refresh
                    if token_data.get("refresh_token"):
                        try:
                            return refresh_token(token_data["refresh_token"])
                        except Exception as e:
                            print("Refresh token expired or invalid. Getting new token...")
                            return get_token_from_tatmeen()
            except ValueError:
                # Invalid datetime format — treat as no token
                pass
    # If no token data or invalid format
    return get_token_from_tatmeen()


