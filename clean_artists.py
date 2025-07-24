import csv
import json

with open('/Users/matteodefilippis/Desktop/data-management-project/Dm_project/mysql/init/artists.csv', newline='', encoding='utf-8') as infile, open('/Users/matteodefilippis/Desktop/data-management-project/Dm_project/mysql/init/artists_clean.csv', 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        raw_genres = row['genres'].strip()
        try:
            # Caso ideale: è già JSON valido
            genres = json.loads(raw_genres)
        except:
            # Prova a trasformarlo in array (es. da "pop,rock" → ["pop", "rock"])
            if raw_genres.startswith('[') and raw_genres.endswith(']'):
                genres = [g.strip().strip('"').strip("'") for g in raw_genres[1:-1].split(',') if g.strip()]
            elif raw_genres:
                genres = [raw_genres.strip()]
            else:
                genres = []

        row['genres'] = json.dumps(genres)
        writer.writerow(row)