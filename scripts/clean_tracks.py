import csv
import json

input_path = '/Users/matteodefilippis/Desktop/data-management-project/Dm_project/mysql/init/tracks.csv'
output_path = '/Users/matteodefilippis/Desktop/data-management-project/Dm_project/mysql/init/tracks_clean.csv'

with open(input_path, newline='', encoding='utf-8') as infile, open(output_path, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        for field in ['artists', 'id_artists']:
            raw = row[field].strip()
            try:
                parsed = json.loads(raw)
            except:
                # Se sembra una lista (es. [a, b]), prova a ripulirla
                if raw.startswith('[') and raw.endswith(']'):
                    parsed = [g.strip().strip('"').strip("'") for g in raw[1:-1].split(',') if g.strip()]
                elif raw:
                    parsed = [raw.strip()]
                else:
                    parsed = []
            row[field] = json.dumps(parsed)

        writer.writerow(row)