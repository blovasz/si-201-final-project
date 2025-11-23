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

def get_superhero_row(id, var1, var2):
    """
    Arg: int id, str var1, str var2
    Out: tup of superhero id, var1, var2
    """
    try:
        data = json.loads(requests.get(f"https://www.superheroapi.com/api.php/{get_api_key("api_keys.txt", 1)}/{id}").text)
        return ((id, data[var1], data[var2]))
    except:
        return ("JSON failed to load.")
    
def get_superhero_rows(start_id, end_id, var1, var2):
    """
    Arg: int start_id, int end_id, str var1, str var2
    Out: lst of tup of superhero id, var1, var2
    """
    out_lst = []
    for id in range(start_id, end_id + 1):
        out_lst.append(get_superhero_row(id, var1, var2))
    return out_lst

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
        CREATE TABLE IF NOT EXISTS superhero_appearance
        (id INTEGER PRIMARY KEY,
        name TEXT,
        gender TEXT,
        height INT,
        weight INT)
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS superhero_place_of_birth
        (id INTEGER PRIMARY KEY,
        name TEXT,
        place_of_birth TEXT)
        """
    )
    conn.commit()

def add_rows_to_db_tables(conn, cur, start_id, end_id):
    """
    Arg: conn, cur, int start_id, int end_id
    Out: none
    """
    for row in get_superhero_rows(start_id, end_id, "name", "appearance"):
        height = 0
        if " meters" in row[2]["height"][1]:
            height = int(float(row[2]["height"][1].replace(" meters", ""))) * 100
        elif " cm" in row[2]["height"][1]:
            height = int(row[2]["height"][1].replace(" cm", ""))
        cur.execute(
            """
            INSERT OR IGNORE INTO superhero_appearance
            (id, name, gender, height, weight)
            VALUES (?, ?, ?, ?, ?)
            """,
            (row[0], row[1], row[2]["gender"], height, int(row[2]["weight"][1].replace(" kg", "")))
        )
    for row in get_superhero_rows(start_id, end_id, "name", "biography"):
        cur.execute(
            """
            INSERT OR IGNORE INTO superhero_place_of_birth
            (id, name, place_of_birth)
            VALUES (?, ?, ?)
            """,
            (row[0], row[1], row[2]["place-of-birth"])
        )
    conn.commit()

def main():
    conn, cur = setup_db("superhero.db")
    setup_tables(conn, cur)
    add_rows_to_db_tables(conn, cur, 1, 25)
    add_rows_to_db_tables(conn, cur, 26, 50)
    add_rows_to_db_tables(conn, cur, 51, 75)
    add_rows_to_db_tables(conn, cur, 76, 100)
    conn.close()

if __name__ == "__main__":
    main()