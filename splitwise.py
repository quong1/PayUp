import os
import requests
import json  # for development

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

auth_url = "https://secure.splitwise.com/api/v3.0/"


# API key authentication
def get_headers():
    headers = {"Authorization": "Bearer {token}".format(token=os.getenv("API_KEY"))}
    return headers


# Only returns first name
def get_current_user():
    headers = get_headers()
    r = requests.get(
        auth_url + "get_current_user",
        headers=headers,
    )
    r_json = r.json()
    return r_json["user"]["first_name"]


# Only returns a first name based on user's ID
def get_another_user(user_id):
    headers = get_headers()
    r = requests.get(
        auth_url + "get_user/{id}".format(id=user_id),
        headers=headers,
    )
    r_json = r.json()
    return r_json["user"]["first_name"]


# Returns all the group names you are in
def get_groups():
    headers = get_headers()
    r = requests.get(
        auth_url + "get_groups",
        headers=headers,
    )
    r_json = r.json()
    try:
        for group in r_json["groups"]:
            print(group["name"])
    except KeyError:
        return "Couldn't get group names"
