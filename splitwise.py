import os
import requests
import json

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

auth_url = "https://secure.splitwise.com/api/v3.0/"


def get_headers():
    access_token = os.getenv("API_KEY")
    headers = {"Authorization": "Bearer {token}".format(token=access_token)}
    return headers


def get_current_user():
    access_token = get_headers()
    r = requests.get(
        auth_url + "get_current_user",
        headers=access_token,
    )
    r_json = r.json()
    return json.dumps(r_json, indent=2)  # formatted with json.dumps for development


print(get_current_user())
