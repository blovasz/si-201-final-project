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

def get_top_ten_players():
    """
    Arguments: None

    Return: lst leaderboard[tup]

    Sorting through Marvel Rivals' API, specifically the player leaderboard
    to get the top 10 players' UID and icons.
    """
    leaderboard = []
    url = "https://marvelrivalsapi.com/api/v2/players/leaderboard"
    header = {"x-api-key": API_key}
    r = requests.get(url, headers = header)
    
    try:
        temp = json.loads(r.text)
    except:
        print("JSON failed to load")

    for i in range(10):
        leaderboard.append((temp["players"][i]["uid"], temp["players"][i]["icon"]["player_icon"]))

    return leaderboard

def get_player_match_history(num):
    """
    Arguement: int num

    Return dict characters_used

    For num number of matches, finding the most used character
    by the top 20 players in Marvel Rivals
    """
    characters_used = {}
    leaderboard = get_top_ten_players()
    header = {"x-api-key": API_key}

    for user in leaderboard:
        url = f"https://marvelrivalsapi.com/api/v1/player/{user[0]}/match-history"
        r = requests.get(url, headers=header)
        
        try:
            temp = json.loads(r.text)
        except:
            print("JSON failed to load")

        characters_used[user[0]] = {}
        for i in range(num):
            try:
                characters_used[user[0]][i+1] = temp["match_history"][i]["match_player"]["player_hero"]["hero_name"]
            except:
                characters_used[user[0]][i+1] = "None"
                
    return characters_used

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
    get_player_match_history(20)

if __name__ == "__main__":
    main()