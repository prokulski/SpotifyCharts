#!/bin/bash

# ściągnięcie notowań
python3 download_charts.py

# skompaktowanie notowań i przygotowanie listy TrackIDs
python3 compact_data.py charts

# pobranie cech audio i danych o artystach z TrackIDs
python3 grab_audiofeatures.py

# skompaktowanie tracków i artystów
python3 compact_data.py tracks

# spakowanie surowych danych
zip -r -9 data/charts.zip data/charts
zip -r -9 data/artists.zip data/artists
zip -r -9 data/tracks.zip data/tracks data/track_ids.csv
