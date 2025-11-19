import sqlite3
import json
import requests
import os

def get_api_key(filename):
    """
    Arguement: str filename

    Return: str key

    Taking a file of api_keys and getting back the Marvel Rivals API key 
    """
    with open(filename) as file:
        key = file.readlines()[2].split("=")[1].strip(" ")

    return key

API_key = get_api_key("api_keys.txt")

def get_data(num):
    """
    Arguement: int num

    Return: dict dic

    Returning hero name, play time, and matches for num number of heroes.
    """
    hero_list_url = f"https://marvelrivalsapi.com/api/v1/heroes"
    header = {"x-api-key": API_key}
    r = requests.get(hero_list_url, headers = header)
    try:
        data = json.loads(r.text)[:num]
    except:
        print("Num is out of range")
        data = json.loads(r.text)
    
    name_lst = []
    for hero in data:
        name_lst.append(hero["name"])

def set_up_database(name):
    """
    Arguement: str name

    Return: tup (cur, conn)

    Setting up a database using the name given.
    Also setting up the cursor and connection objects.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path + "/" + name)
    cur = conn.cursor()

    return (cur, conn)

get_data(5)
get_data(100)