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

def get_top_players(page_num):
    """
    Arguments: page_num

    Return: lst leaderboard[tup]

    Sorting through Marvel Rivals' API, specifically the player leaderboard
    to get 25 players from page number page_num.
    """
    leaderboard = []
    #25 items load per page, iterating through pages lets us get 25 players per page
    url = f"https://marvelrivalsapi.com/api/v2/players/leaderboard?page={page_num}"
    header = {"x-api-key": API_key}
    r = requests.get(url, headers = header)
    
    try:
        temp = json.loads(r.text)

        for i in range(25):
            leaderboard.append((temp["players"][i]["uid"], temp["players"][i]["icon"]["player_icon"]))
    except:
        print("JSON failed to load")

    return leaderboard

def get_player_match_history(num, page_num):
    """
    Arguement: int num, int page_num

    Return dict characters_used

    For num number of matches, finding the most used character
    by the top 20 players in Marvel Rivals
    """
    characters_used = {}
    leaderboard = get_top_players(page_num)
    header = {"x-api-key": API_key}

    for user in leaderboard:
        url = f"https://marvelrivalsapi.com/api/v1/player/{user[0]}/match-history"
        r = requests.get(url, headers=header)
        
        try:
            temp = json.loads(r.text)
        except:
            print("JSON failed to load")
            temp = {}

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
    get_player_match_history(5, 1)

if __name__ == "__main__":
    main()