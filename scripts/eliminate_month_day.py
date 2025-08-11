import pandas as pd

# === Percorso file sorgente ===
src_path = "/home/dans/Documents/Uni/DM_project/files/modified/tracks.csv"

# Legge il CSV originale
df = pd.read_csv(src_path)

print(df['release_date'])

df['release_date'] = pd.to_datetime(df['release_date'], yearfirst=True, format="mixed")

df['release_date'] = df['release_date'].dt.strftime('%Y')

print(df['release_date'])
# Salva il nuovo CSV con solo gli anni
out_csv = "tracks_years.csv"
df.to_csv(out_csv, index=False)

print("File salvato come:", out_csv)
