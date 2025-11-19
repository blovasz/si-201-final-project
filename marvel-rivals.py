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

def get_top_five_players():
    """
    Arguments: None

    Return: List of top 5 Marvel Rivals Players' UID

    Sorting through Marvel Rivals' API, specifically the player leaderboard
    to get the top 5 players' UID.
    """
    leaderboard = []
    url = "https://marvelrivalsapi.com/api/v2/players/leaderboard"
    header = {"x-api-key": API_key}
    r = requests.get(url, headers = header)
    
    try:
        temp = json.loads(r.text)
    except:
        print("JSON failed to load")

    for i in range(5):
        leaderboard.append(temp["players"][i]["uid"])

    return leaderboard

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

def main():
    get_top_five_players()

if __name__ == "__main__":
    main()