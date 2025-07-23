#!/bin/bash
set -e

# attiva l'opzione LOCAL per LOAD DATA
mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "SET GLOBAL local_infile = 1;"

# importa artists.csv
mysql --local-infile=1 -u root -p"$MYSQL_ROOT_PASSWORD" spotify <<'SQL'
LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/artists.csv'
INTO TABLE artists
FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
SQL

# importa tracks.csv
# mysql --local-infile=1 -u root -p"$MYSQL_ROOT_PASSWORD" spotify <<'SQL'
# LOAD DATA LOCAL INFILE '/docker-entrypoint-initdb.d/tracks.csv'
# INTO TABLE tracks
# FIELDS TERMINATED BY ',' ENCLOSED BY '"' 
# LINES TERMINATED BY '\n'
# IGNORE 1 ROWS;
# SQL
