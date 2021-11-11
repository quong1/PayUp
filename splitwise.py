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
def get_another_user(id):
    headers = get_headers()
    r = requests.get(
        auth_url + "get_user/{id}".format(id=id),
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


"""
Format for group must have name of group, users__{index}__{property}
{property} is 'id' and must be provided

EXAMPLE:
    'name': 'The Brain Trust',
    'group_type': 'trip',
    'users__0__first_name': 'Alan',
    'users__0__last_name': 'Turing',
    'users__0__email': 'alan@example.org',
    'users__1__id': 5823
"""


def create_group(name, group_type, id):
    headers = get_headers()
    data = {
        "name": name,
        "group_type": group_type,
        "users__{index}__{property}": id,
    }
    r = requests.post(
        auth_url + "create_group",
        headers=headers,
        data=data,
    )


# print(get_current_user())
# print(get_another_user(6716973))
# print(get_groups())
