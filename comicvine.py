import sqlite3
import json
import requests
import os

def get_api_key(filename):
    """
    Arguement: str filename

    Return: str key

    Taking a file of api_keys and getting back the Comic Vine API key 
    """
    with open(filename) as file:
        key = file.readlines()[0].split("=")[1].strip(" ")

    return key

API_KEY = str(get_api_key("api_keys.txt").strip())

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
    
    """
    #Creating origins
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS origins (id INTEGER PRIMARY KEY,
        origin TEXT UNIQUE)
        """
    )

    #Creating genders
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS genders (id INTEGER PRIMARY KEY, gender TEXT UNIQUE)
        """
    )

    #Creating characters
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY, name TEXT UNIQUE, 
        numcomics INT, origin_id INT, gender_id INT)
        """
    )

    conn.commit()

def get_data():
    """
    Arugements: None

    Returns: [(hero name, origin, number of comic appearances)]

    Iterating through the data from comic vine to find heros from Marvel
    trying to find the amount of times different heroes are shown in the comics
    as well as their origin.
    """
    results = []
    offset = 0

    while len(results) < 100:
        url = f"https://comicvine.gamespot.com/api/characters/?api_key={API_KEY}&format=json&field_list=count_of_issue_appearances,name,origin,publisher,gender&offset={offset}"
        r = requests.get(url, headers={"User-Agent": "MyApp"})
        try:
            data = json.loads(r.text)
        except:
            print("JSON failed to load")
            return None
        
        for hero in data["results"]:
            if hero["publisher"]["name"] == "Marvel":
                name = hero.get("name", "None")
                try:
                    origin = hero.get("origin", {}).get("name", "None")
                except:
                    origin = "None"
                numcomics = hero.get("count_of_issue_appearances", 0)
                gender = hero.get("gender", "Other")
                results.append((
                    name, origin, numcomics, gender
                ))
        
        offset += 100

    return results

def insert_data_for_origins(cur, conn, data):
    """
    Arugments: cur, conn, data

    Returns: None
    """
    x = 0
    y = 25

    while y < len(data):
        for i in range(x,y):
            cur.execute(
                """
                INSERT OR IGNORE INTO origins (id, origin)
                VALUES (?, ?)
                """,
                (i, data[i][1])
            )
            conn.commit()

        x += 25
        y += 25
    pass

def insert_data_for_gender(cur, conn, data):
    """
    Arugments: cur, conn, data

    Returns: None
    """
    x = 0
    y = 25
    

    while y < len(data):
        for i in range(x,y):
            cur.execute(
                """
                INSERT OR IGNORE INTO genders (id, gender)
                VALUES (?, ?)
                """,
                (1, "Male")
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO genders (id, gender)
                VALUES (?, ?)
                """,
                (2, "Female")
            )
            cur.execute(
                """
                INSERT OR IGNORE INTO genders (id, gender)
                VALUES (?, ?)
                """,
                (0, "Other")
            )
            conn.commit()

        x += 25
        y += 25
    pass

def insert_data_for_characters(cur, conn, data):
     x = 0
     y = 25

     while y < len(data):
        for i in range(x,y):
            cur.execute(
                f"""
                SELECT id FROM origins
                WHERE origin = '{data[i][1]}'
                """
            )

            o = cur.fetchone()[0]

            #characters
            cur.execute(
                """
                INSERT OR IGNORE INTO characters (id, name, numcomics, origin_id, gender_id) VALUES (?,?,?,?,?)
                """,
                (i, data[i][0], data[i][2], o, data[i][3])
            )

            conn.commit()

        x += 25
        y += 25

def main():
    cur, conn = set_up_database("comicvine.db")
    set_up_tables(cur, conn)
    data = get_data()
    insert_data_for_origins(cur, conn, data)
    insert_data_for_gender(cur,conn,data)
    insert_data_for_characters(cur,conn,data)
    conn.close()

if __name__ == "__main__":
    main()