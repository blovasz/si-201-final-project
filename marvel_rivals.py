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

def get_hero_key(filename):
    """
    Arguement: str filename

    Return: str key

    Taking a file of api_keys and getting back the Superhero API key 
    """
    with open(filename) as file:
        key = file.readlines()[1].split("=")[1].strip(" ")

    return key

API_key = get_api_key("api_keys.txt")
API_KEY = get_hero_key("api_keys.txt").strip()

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
    except:
        print("JSON failed to load at top_players")
        return r.status_code

    for i in range(25):
        leaderboard.append((temp["players"][i]["uid"], temp["players"][i]["name"]))
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
        url = f"https://marvelrivalsapi.com/api/v2/player/{user[0]}/match-history"
        r = requests.get(url, headers=header)
        
        try:
            temp = json.loads(r.text)
        except:
            print("JSON failed to load at player_match_history")
            print(r.status_code)
            temp = {}

        characters_used[user[0]] = {"name": user[1]}
        for i in range(num):
            try:
                characters_used[user[0]][i+1] = temp["match_history"][i]["match_player"]["player_hero"]["hero_id"]
            except:
                characters_used[user[0]][i+1] = "None"

    return characters_used

def hero_list():
    """
    Arguement: None

    Return: lst[tup(hero_id, hero_name)]

    Getting a list of every hero in game with their hero name and id
    """
    hero_lst = []
    url = "https://marvelrivalsapi.com/api/v1/heroes"
    header = {"x-api-key": API_key}
    r = requests.get(url, headers=header)
    base = f"https://superheroapi.com/api/{API_KEY}/search/"

    try:
        temp = json.loads(r.text)
    except:
        print(r.status_code)
        print("JSON failed to load at hero_list 1")

    for hero in temp:
        ourl = base + hero["name"]
        try:
            req = requests.get(ourl)
            gdata = json.loads(req.text)
        except:
            print("JSON faild to load at hero_list 2")
        
        try:
            gender = gdata["results"][0]["appearance"]["gender"]
        except:
            gender = "Other"
            
        tup = (hero["id"], hero["name"], gender)
        hero_lst.append(tup)

    return hero_lst

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

def set_up_tables(cur, conn):
    """
    Arguement: cur, conn

    Return: None

    Create two tables:
    character_by_match - uid, player, match1, match2, match3, match4, match5
    characters - id, name
    """
    #Creating character_by_match
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS character_by_match (uid INTEGER PRIMARY KEY,
        player TEXT UNIQUE, match1 INT, match2 INT, match3 INT, match4 INT, match5 INT)
        """
    )

    conn.commit()

def add_to_character_by_match(num, page_num, cur, conn):
    """
    Arguements: int num, int page_num, cur, conn

    Return: None

    Calling get_player_match_history() and adding that data to character_by_match
    if its not a duplicate.
    """
    data = get_player_match_history(num, page_num)

    if type(data) != dict:
        return data

    for player in list(data.keys()):
        
        cur.execute(
            """
            INSERT OR IGNORE INTO character_by_match (uid, player, match1, match2, match3, match4, match5)
            VALUES (?,?,?,?,?,?,?)
            """,
            (player, data[player]["name"], data[player][1], data[player][2], data[player][3],
            data[player][4], data[player][5])
        )
        #I'm only adding the player if their match data is available. 
        #if data[player][1] != "None" and data[player][2] != "None" and data[player][3] != "None" and data[player][4] != "None" and data[player][5] != "None":
         #   cur.execute(
                #"""
                #INSERT OR IGNORE INTO character_by_match (uid, player, match1, match2, match3, match4, match5)
                #VALUES (?,?,?,?,?,?,?)
                #""",
           #     (player, data[player]["name"], data[player][1], data[player][2], data[player][3],
            #    data[player][4], data[player][5])
            #)

    conn.commit()
    pass

def add_to_characters(x, y, cur, conn):
    """
    Arguements: int x, int y, cur, conn

    Return: None

    Using x and y to limit how many characters we add at a time,
    we are adding data from hero_list() to the characters table
    """
    lst = hero_list()
    if y > len(lst):
        data = lst[x:len(lst)+1]
    else:
        data = lst[x:y]

    cur.execute(
        """
        SELECT name FROM names
        """
    )

    lst = cur.fetchall()
    id = len(lst)+1

    for hero in data:
        tup = (hero[1],)
        if tup not in lst:
            cur.execute(
                """
                INSERT OR IGNORE INTO names (name_id, name)
                VALUES (?,?)
                """,
                (id, hero[1])
            )
            conn.commit()

        cur.execute(
            f"""
            SELECT name_id FROM names
            WHERE name = '{hero[1]}'
            """
        )
        name_id = cur.fetchone()[0]
        
        if hero[2] == "Male":
            cur.execute(
                """
                INSERT OR IGNORE INTO superheros (name_id, gender_id, mr_id) VALUES (?, ?, ?)
                """,
                (name_id, 1, hero[0])
            )
        elif hero[2] == "Female":
            cur.execute(
                """
                INSERT OR IGNORE INTO superheros (name_id, gender_id, mr_id) VALUES (?, ?, ?)
                """,
                (name_id, 2, hero[0])
            )
        else:
            cur.execute(
                """
                INSERT OR IGNORE INTO superheros (name_id, gender_id, mr_id) VALUES (?, ?, ?)
                """,
                (name_id, 3, hero[0])
            )
        id += 1

    conn.commit()
    pass

def run_add_character_by_match(x, cur, conn):
    """
    Arguement: int x, cur, conn

    Return: None
    
    Run character_by_match until num of rows is equal to x
    """

    cur.execute(
        """
        SELECT uid FROM character_by_match
        """
    )

    count = len(cur.fetchall())
    x += count
    if count > 0:
        pagenum = 100/count
    else:
        pagenum = 5
    c = add_to_character_by_match(5, pagenum, cur, conn)
    pass

def main():
    cur, conn = set_up_database("superhero.db")
    set_up_tables(cur, conn)
    run_add_character_by_match(25, cur, conn) 
    conn.close()

if __name__ == "__main__":
    main()