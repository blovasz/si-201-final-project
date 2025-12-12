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
    #Creating 
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS numcomics (id INTEGER PRIMARY KEY, comics TEXT UNIQUE)
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

    while len(results) < 150:
        url = f"https://comicvine.gamespot.com/api/characters/?api_key={API_KEY}&format=json&field_list=count_of_issue_appearances,name,first_appeared_in_issue,publisher,gender&offset={offset}"
        r = requests.get(url, headers={"User-Agent": "MyApp"})
        try:
            data = json.loads(r.text)
        except:
            print("JSON failed to load")
            return None
        
        for hero in data["results"]:
            if hero["publisher"]["name"] == "Marvel":
                name = hero.get("name", "None")
                numcomics = hero.get("count_of_issue_appearances", 0)
                gender = hero.get("gender", "Other")
                results.append((
                    name, numcomics, gender
                ))
        
        offset += 100

    return results

def insert_data_for_characters(cur, conn, data):
     """
     Arguments: cur, conn, data

     Returns: NONE
     """
     cur.execute(
        """
        SELECT name FROM names
        """
     )
     lst = cur.fetchall()
     id = len(lst) + 1
     cur.execute(
         """
        SELECT comics FROM numcomics
        """
     )
     x = len(cur.fetchall())
     y = x + 25

     for i in range(x, y):
        temp = (data[i][0],)
        if temp in lst:
            continue

        cur.execute(
            """
            INSERT OR IGNORE INTO names (name_id, name) VALUES (?,?)
            """,
            (id, data[i][0])
        )

        gender = data[i][2]
        if gender == 0:
            gender = 3

        cur.execute(
            """
            INSERT OR IGNORE INTO superheros (name_id, gender_id)
            VALUES (?,?)
            """,
            (id, gender)
        )
        conn.commit()
        id += 1

     pass

def insert_data_for_numissues(cur, conn):
    """
    Arguments: cur, conn, data

    Returns: NONE
    """
    cur.execute(
        """
        SELECT name_id, name FROM names
        """
    )
    data = cur.fetchall()
    
    cur.execute(
        """
        SELECT name_id, num_comics FROM superheros
        """
    )
    temp = cur.fetchall()
    for t in temp:
        if t[1] == None:
            x = t[0] - 1
            y = x + 20 #adding 20 at a time in case there are double named superheros so we're not adding 25+
            break
        else:
            print("Finished searching for data!")
            pass

    for i in range(x,y):
        try:
            url = f"https://comicvine.gamespot.com/api/characters/?api_key={API_KEY}&format=json&field_list=count_of_issue_appearances,name&filter=name:{data[i][1]}"
        except:
            print("Finished searching for data!")
            break
        r = requests.get(url, headers={"User-Agent": "MyApp"})
        try:
            temp = json.loads(r.text)
        except:
            print("JSON failed to load")
            return None

        issues = "NULL"
        for hero in temp["results"]:
            if hero["name"].lower() == data[i][1].lower():
                issues = str(hero["count_of_issue_appearances"])
                break
            
        cur.execute(
            """
            INSERT OR IGNORE INTO numcomics (id, comics)
            VALUES (?,?)
            """,
            (i, issues)
        )
        conn.commit()

        cur.execute(
            f"""
            SELECT id, comics FROM numcomics
            WHERE comics = "{issues}"
            """
        )

        id = cur.fetchone()[0]
        cur.execute(
            f"""
            UPDATE superheros
            SET num_comics = {id}
            WHERE name_id = {data[i][0]}
            """
        )
        conn.commit()
pass


def main():
    cur, conn = set_up_database("superhero.db")
    set_up_tables(cur, conn)
    cur.execute(
        """
        SELECT id FROM superheros
        """
    )
    length = len(cur.fetchall())
    if length < 150:
        data = get_data()
        insert_data_for_characters(cur,conn,data)
    insert_data_for_numissues(cur,conn)
    conn.close()

if __name__ == "__main__":
    main()