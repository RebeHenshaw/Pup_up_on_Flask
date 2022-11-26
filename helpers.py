import os
import requests
import random


def get_access_token(url, client_id, client_secret):
    """Automatically refresh the access token."""
    response = requests.post(url, data={"grant_type": "client_credentials"}, auth=(client_id, client_secret))
    return response.json()['access_token']



CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = 'https://api.petfinder.com/v2/oauth2/token'
URL_BASE = "https://api.petfinder.com/v2/animals"
TOKEN = get_access_token(TOKEN_URL, CLIENT_ID, CLIENT_SECRET)
HEADER = {"Authorization": f"Bearer {TOKEN}"}

def get_image(dog):
    """Returns URL to dog photo or stock photo if there's no photo"""
    try:
        url = dog['photos'][0]['medium']
    except:
        url = "static/stock.jpg"
    return url


def get_thought(dog):
    # populate thought bubble with personal message
    thoughts = [
        f"{dog['name']} is soooo cute!",
        f"I bet {dog['name']} likes to play ball!",
        f"Wow, {dog['name']} looks fun!",
        f"{dog['name']} needs a snuggle!"
        ]
    t = random.randint(0, len(thoughts) - 1)
    return thoughts[t]

def get_info(dog, photo):
    info = {
            "name": dog["name"],
            "location": dog['contact']['address']['city'],
            "url": dog["url"],
            "photo": photo,
            "breed": dog['breeds']['primary'],
            "age": dog["age"],
        }
    return info
