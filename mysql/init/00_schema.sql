CREATE TABLE artists (
  id         VARCHAR(25) PRIMARY KEY,
  followers  INT,
  genres     JSON ,          -- era JSON
  name       VARCHAR(255),
  popularity INT
);

CREATE TABLE tracks (
  id               VARCHAR(25) PRIMARY KEY,
  name             VARCHAR(255),
  popularity       INT,
  duration_ms      INT,
  explicit         TINYINT,
  artists          JSON,     -- era JSON
  id_artists       JSON,     -- era JSON
  release_date     DATE,
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
