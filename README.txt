Instructions for Running the Code:
1. Create an API key from https://superheroapi.com/, https://comicvine.gamespot.com/api/, and https://marvelrivalsapi.com/.
2. Insert each API key into the “replace text with key” on each corresponding line in the api_keys.txt file.
3. Run the superhero.py file 4 times first to create and populate the main database: superhero.db.
4. Run the marvel_rivals.py 4 times to create and populate its tables to the superhero.db database.
5. Run the comicvine.py file 6 times (or until "Finished searching for data!" prints) to create and populate its tables to the superhero.db database.
6. Run the calculations.py file to perform calculations using data from the superhero.db database to create the data calculations files: gender_by_comics.csv, most_played_characters.csv, num_superhero_by_origin.txt, and average_bmi_by_gender.txt.
5. Run the bl-visuals.py and sj-visuals.py files to create the visualizations from calculated data.