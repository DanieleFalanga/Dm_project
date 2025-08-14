import pandas as pd
import json
import ast


def fix_columns_to_JSON(val):
    try:
        # Converte la stringa in lista python (anche se usa singole virgolette)
        columns_list = ast.literal_eval(val)
        # Serializza in JSON (usa sempre doppie virgolette)
        return json.dumps(columns_list)
    except Exception:
        return json.dumps([])

def convert_to_JSON(df_tracks, df_artists):
    df_artists['genres'] = df_artists['genres'].apply(fix_columns_to_JSON)
    df_tracks['artists'] = df_tracks['artists'].apply(fix_columns_to_JSON)
    df_tracks['id_artists'] = df_tracks['id_artists'].apply(fix_columns_to_JSON)
    

def eliminate_month_day(df_tracks):
    df_tracks['release_date'] = pd.to_datetime(df_tracks['release_date'], yearfirst=True, format="mixed")
    df_tracks['release_date'] = df_tracks['release_date'].dt.strftime('%Y')

def save_csv(df_tracks, df_artists,dst_path_tracks, dst_path_artists):
    df_artists.to_csv(dst_path_artists, index=False)
    df_tracks.to_csv(dst_path_tracks, index=False)

def convert_followers_to_int(df_artists):
    df_artists['followers'] = pd.to_numeric(df_artists['followers'], errors='coerce').fillna(0).astype(int)

def main():
    # === Percorso file sorgente ===
    src_path_tracks = "/home/dans/Documents/Uni/DM_project/files/original_files/tracks.csv"
    src_path_artists = "/home/dans/Documents/Uni/DM_project/files/original_files/artists.csv"

    dst_path_tracks = "/home/dans/Documents/Uni/DM_project/files/modified/tracks.csv"
    dst_path_artists = "/home/dans/Documents/Uni/DM_project/files/modified/artists.csv"

    # Legge i CSV originali
    df_artists = pd.read_csv(src_path_artists)
    df_tracks = pd.read_csv(src_path_tracks)

    convert_to_JSON(df_tracks, df_artists)

    convert_followers_to_int(df_artists)

    eliminate_month_day(df_tracks)

    print(df_artists.dtypes)
    print(df_tracks.dtypes)

    save_csv(df_tracks, df_artists,dst_path_tracks, dst_path_artists)
main()
