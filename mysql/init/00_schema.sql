CREATE TABLE artists (
  id         VARCHAR(25) PRIMARY KEY,
  followers  INT,
  genres     JSON ,          
  name       VARCHAR(255),
  popularity INT
);


CREATE TABLE tracks (
  id               VARCHAR(25) PRIMARY KEY,
  name             VARCHAR(255),
  popularity       INT,
  duration_ms      INT,
  explicit         TINYINT,
  artists          JSON,     
  id_artists       JSON,     
  release_date     YEAR,
  danceability     FLOAT,
  energy           FLOAT,
  `key`            TINYINT,
  loudness         FLOAT,
  mode             TINYINT,
  speechiness      FLOAT,
  acousticness     FLOAT,
  instrumentalness FLOAT,
  liveness         FLOAT,
  valence          FLOAT,
  tempo            FLOAT,
  time_signature   TINYINT
);



-- TODO: Eseguire la query sottostante dopo aver runnato i container
-- CREATE TABLE tracks_artists AS
-- SELECT 
--   t.id         AS track_id,
--   t.name       AS track_name,
--   a.id         AS artist_id,
--   a.name       AS artist_name
-- FROM tracks t
-- JOIN JSON_TABLE(t.id_artists, '$[*]' COLUMNS(artist_id VARCHAR(25) PATH '$')) AS ta
--   ON TRUE
-- JOIN artists a 
--   ON a.id = ta.artist_id;