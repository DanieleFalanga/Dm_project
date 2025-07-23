#!/bin/bash
set -e
mongoimport \
  --username "$MONGO_INITDB_ROOT_USERNAME" \
  --password "$MONGO_INITDB_ROOT_PASSWORD" \
  --authenticationDatabase admin \
  --db spotify \
  --collection tracks \
  --type csv \
  --file /docker-entrypoint-initdb.d/tracks.csv \
  --headerline
