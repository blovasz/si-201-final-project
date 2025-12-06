import sqlite3
import json
import requests
import os
import re

# Add these columns to the superhero table in superhero.db
# mr_id INT
# num_comics INT
# first_issue INT


def get_api_key(file_name, api_key_loc):
    """ 
    Arg: str file_name, int api_key_loc
    Out: str api key from file_name
    Gets the API key from api_keys.txt
    """
    with open(file_name) as file:
        return file.readlines()[api_key_loc].split("=")[1].strip()

def get_superhero_row(id):
    """
    Arg: int id
    Out: tup of superhero id
    Gets the superhero data row of a specific superhero ID
    """
    try:
        data = json.loads(requests.get(f"https://www.superheroapi.com/api.php/{get_api_key("api_keys.txt", 1)}/{id}").text)
        return ((id, data["biography"]["publisher"], data["name"], data["appearance"]["gender"], data["biography"]["place-of-birth"], data["appearance"]["height"][1], data["appearance"]["weight"][1]))
    except:
        return (id, None, None, None, None, None, None)
    
def get_superhero_rows(start_id, end_id):
    """
    Arg: int start_id, int end_id
    Out: lst of tup of superhero id
    Gets all the superhero row data from a specified start and end ID range
    """
    out_lst = []
    counter = 0
    for id in range(start_id, end_id + 1):
        if counter != 100:
            unique_id, publisher, name, gender, origin, height, weight = get_superhero_row(id)
            if publisher != "Marvel Comics":
                continue 
            else:
                counter += 1
                if gender == "Male":
                    gender = 1
                elif gender == "Female":
                    gender = 2
                else:
                    gender = 3 # Not "Male" or "Female"
                if re.search(r"Yugoslavia|Germany|Ireland|England|United\sKingdom|Russia|USSR|Latveria", origin):
                    origin = 2 # "Europe"
                elif re.search(r"Egypt|Africa", origin):
                    origin = 3 # "Africa"
                elif re.search(r"Vietnam", origin):
                    origin = 4 # "Asia"
                elif re.search(r"Eternity|Xandar|Arthros|Galaxy|Beyond|Attilan|Criminal|Armechadon|Dimension|Asgard", origin):
                    origin = 6 # "Fictional Place"
                elif re.search(r"unknown|Earth", origin):
                    origin = 5 # "Somewhere in Earth"
                elif re.search(r"-", origin):
                    origin = 7 # "Unknown"
                else:
                    origin = 1 # "North America"
                if re.search(r"\smeters", height):
                    height = int(float(height.replace(" meters", ""))) * 100
                elif re.search(r"\scm", height):
                    height = int(height.replace(" cm", ""))
                out_lst.append((unique_id, name, gender, origin, height, weight.replace(" kg", "")))
        else:
            break
    return out_lst

def setup_db(db_name):
    """
    Arg: str db_name
    Out: conn, cur
    Sets up the database
    """
    conn = sqlite3.connect(os.path.dirname(os.path.abspath(__file__)) + "/" + db_name)
    return (conn, conn.cursor())

def setup_tables(conn, cur):
    """
    Arg: conn, cur
    Out: none
    Sets up the tables in the database
    """
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS superheros
        (id INTEGER,
        name_id INTEGER PRIMARY KEY,
        gender_id INTEGER,
        place_of_birth_id INTEGER,
        height INTEGER,
        weight INTEGER,
        mr_id INTEGER,
        num_comics INTEGER,
        first_issue INTEGER)
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS names
        (name_id INTEGER PRIMARY KEY,
        name TEXT)
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS genders (
            gender_id INTEGER PRIMARY KEY,
            gender TEXT
        )
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO genders (gender_id, gender)
        VALUES (1, 'Male')
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO genders (gender_id, gender)
        VALUES (2, 'Female')
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO genders (gender_id, gender)
        VALUES (3, 'Unknown')
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS places_of_birth
        (place_of_birth_id INTEGER PRIMARY KEY,
        place_of_birth TEXT)
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (1, "North America")
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (2, "Europe")
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (3, "Africa")
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (4, "Asia")
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (5, "Somewhere in Earth")
        """
    )
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (6, "Fictional Place")
        """
    )  
    cur.execute(
        """
        INSERT OR IGNORE INTO places_of_birth
        (place_of_birth_id, place_of_birth)
        VALUES (7, "Unknown") 
        """
    )
    conn.commit()

unique_names = {}

def add_rows_to_db_tables(conn, cur, batch):
    """
    Arg: conn, cur, int batch
    Out: none
    Adds the rows in batches of 25 to the database tables
    """
    for idx, row in enumerate(batch):
        unique_id, name, gender, origin, height, weight = row
        if name not in unique_names.values():
            name_id = len(unique_names) + 1
            unique_names[name_id] = name
            cur.execute(
                "INSERT OR IGNORE INTO names (name_id, name) VALUES (?, ?)",
                (name_id, name)
            )
            cur.execute(
                """INSERT OR IGNORE INTO superheros
                (id, name_id, gender_id, place_of_birth_id, height, weight)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (unique_id, name_id, gender, origin, height, weight)
            )
        else:
            name_id = [k for k, v in unique_names.items() if v == name][0]
            cur.execute(
                """INSERT OR IGNORE INTO superheros
                (id, name_id, gender_id, place_of_birth_id, height, weight)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (unique_id, name_id, gender, origin, height, weight)
            )
    conn.commit()

def chunked(iterable, size):
    """
    Arg: lst iterable, int size
    Out: none
    Returns a list of data chunks of size 25
    """
    chunks = []
    for i in range(0, len(iterable), size):
        chunks.append(iterable[i:i+size])
    return chunks

def main():
    """
    Arg: none
    Out: none
    """
    conn, cur = setup_db("superhero.db")
    setup_tables(conn, cur)
    for batch in chunked(get_superhero_rows(1, 231), 25):
        add_rows_to_db_tables(conn, cur, batch)
    conn.close()

if __name__ == "__main__":
    main()