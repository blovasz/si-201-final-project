import sqlite3
import json
import requests
import os

def get_api_key(file_name, api_key_loc):
    """
    Arg: str file_name, int api_key_loc
    Out: str api key from file_name
    """
    with open(file_name) as file:
        return file.readlines()[api_key_loc].split("=")[1].strip()

def get_comics():
    """
    Arg: int id, str var1, str var2
    Out: tup of superhero id, var1, var2
    """
    comic_lst = []
    try:
        data = json.loads(requests.get(f"https://comicvine.gamespot.com/api/characters/?api_key={get_api_key('api_keys.txt', 2)}&format=json", headers={"User-Agent": "MyApp"}).text)
        for result in data["results"]:
            comic_lst.append((result["id"], result["name"], result["gender"], result["count_of_issue_appearances"]))
        return comic_lst
    except:
        return "JSON failed to load."

def get_movies():
    """
    Arg: int id, str var1, str var2
    Out: tup of superhero id, var1, var2
    """
    movie_lst = []
    try:
        data = json.loads(requests.get(f"https://comicvine.gamespot.com/api/movies/?api_key={get_api_key('api_keys.txt', 2)}&format=json", headers={"User-Agent": "MyApp"}).text)
        for result in data["results"]:
            movie_lst.append((result["id"], result["name"], result["box_office_revenue"], result["budget"]))
        return movie_lst
    except:
        return "JSON failed to load."
    
def setup_db(db_name):
    """
    Arg: str db_name
    Out: conn, cur
    """
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + "/" + db_name)
    return (conn, conn.cursor())

def setup_tables(conn, cur):
    """
    Arg: conn, cur
    Out: none
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS comics
        (id INTEGER PRIMARY KEY,
        name TEXT,
        gender TEXT,
        count_of_issue_appearances INT)
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS movies
        (id INTEGER PRIMARY KEY,
        name TEXT,
        box_office_revenue INT,
        budget INT)
        """
    )
    conn.commit()

def add_rows_to_db_tables(conn, cur, start_idx, end_idx):
    for idx in range(start_idx, end_idx + 1):
        gender = 0
        if get_comics()[idx][2] == 1:
            gender = "male"
        elif get_comics()[idx][2] == 0:
            gender = "unknown"
        elif get_comics()[idx][2] == 2:
            gender = "female"
        cur.execute(
            """
            INSERT OR IGNORE INTO comics
            (id, name, gender, count_of_issue_appearances)
            VALUES (?, ?, ?, ?)
            """,
            (get_comics()[idx][0], get_comics()[idx][1], gender, get_comics()[idx][3])
        )
    for idx in range(start_idx, end_idx + 1):
        cur.execute(
            """
            INSERT OR IGNORE INTO movies
            (id, name, box_office_revenue, budget)
            VALUES (?, ?, ?, ?)
            """,
            (get_movies()[idx][0], get_movies()[idx][1], get_movies()[idx][2], get_movies()[idx][3])
        )
    conn.commit()
    
def main():
    conn, cur = setup_db("comic_vine.db")
    setup_tables(conn, cur)
    add_rows_to_db_tables(conn, cur, 0, 24)
    add_rows_to_db_tables(conn, cur, 25, 49)
    add_rows_to_db_tables(conn, cur, 50, 74)
    add_rows_to_db_tables(conn, cur, 75, 99)
    conn.close()

if __name__ == "__main__":
    main()