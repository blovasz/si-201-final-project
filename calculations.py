import marvel_rivals
import superhero

def most_played_characters(file, filename):
    """
    Arguements: str file, str filename

    Return: None

    Iterating through the characters used and ordering them
    through most played in a text file for later use
    """
    results = []
    cur, conn = marvel_rivals.set_up_database(file)

    cur.execute(
        """
        SELECT name, id FROM characters
        """
    )

    hero_lst = cur.fetchall()

    for hero in hero_lst:
        count = 0
        name = hero[0]
        id = hero[1]

        for i in range(1,6):
            #iterating over a single match at a time so I'm not getting the whole row
            cur.execute(
                f"""
                SELECT character_by_match.match{i} FROM character_by_match
                WHERE character_by_match.match{i} = {id}
                """
            )
            
            #the length of fetchall should contain number of times character is used
            num = len(cur.fetchall())
            count += num

        results.append((name, count))
        results = sorted(results, key = lambda x: x[1], reverse=True)
    
    try:
        open(filename)
    except:
        #Only writing if the file doesn't already exist
        with open(filename, "w") as f:
            f.write(f"{results[0][0]} is used {results[0][1]} times")
            for i in range(1, len(results)):
                f.write(f"\n{results[i][0]} is used {results[i][1]} times")
    pass

def superhero_api_calculations(db_file, filename, filename2):
    """
    Args: str db_file, str filename
    Out: none 
    """
    conn, cur = superhero.setup_db(db_file)
    cur.execute("""
        SELECT places_of_birth.place_of_birth
        FROM superheros
        JOIN places_of_birth
        ON superheros.place_of_birth_id = places_of_birth.place_of_birth_id
    """)
    places_of_birth = cur.fetchall()
    places_count = {
        "North America": 0,
        "Europe": 0,
        "Africa": 0,
        "Asia": 0,
        "Somewhere in Earth": 0,
        "Fictional Place": 0,
        "Unknown": 0
    }
    for place in places_of_birth:
        if place[0] in places_count:
            places_count[place[0]] += 1
    with open(filename, "w") as f:
        for origin, count in places_count.items():
            f.write(f"There are {count} superheros from {origin}\n")

    cur.execute("""
        SELECT genders.gender, superheros.height, superheros.weight
        FROM superheros
        JOIN genders
        ON superheros.gender_id = genders.gender_id
    """)
    gender_height_weight = cur.fetchall()

    gender_counts = {"Male": 0, "Female": 0, "Unknown": 0}
    gender_bmi = {"Male": 0, "Female": 0, "Unknown": 0}

    for g, height, weight in gender_height_weight:
        if g in gender_counts and height and weight:
            try:
                bmi = weight / ((height / 100) ** 2)
                gender_counts[g] += 1
                gender_bmi[g] += bmi
            except Exception:
                continue

    with open(filename2, "a") as f:   # append so both results are in same file
        for gender, total_bmi in gender_bmi.items():
            if gender_counts[gender] > 0:
                avg_bmi = total_bmi / gender_counts[gender]
                f.write(f"The average BMI for {gender} superheros is {avg_bmi:.2f}\n")
            else:
                f.write(f"No data for {gender} superheros\n")

def main():
    most_played_characters("marvel_rivals.db", "most_played_characters.txt")
    superhero_api_calculations("superhero.db", "num_superhero_by_origin.txt", "average_bmi_by_gender.txt")

if __name__ == "__main__":
    main()