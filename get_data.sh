#!/bin/bash

# aktywacja venv
source venv/bin/activate

# ściągnięcie notowań
echo ""
echo "==== Pobieram dane o notowaniach"
python3 download_charts.py

# skompaktowanie notowań i przygotowanie listy TrackIDs
echo ""
echo "==== Kompaktuje dane o notowaniach"
python3 compact_data.py charts

# pobranie cech audio i danych o artystach z TrackIDs
echo ""
echo "==== Pobieram dane o utworach"
python3 grab_audiofeatures.py

# skompaktowanie tracków i artystów
echo ""
echo "==== Kompaktuje dane o utworach"
python3 compact_data.py tracks

# spakowanie surowych danych
echo ""
echo "==== Zipuje wszystko"
zip -r -9 data/charts.zip data/charts
zip -r -9 data/artists.zip data/artists
zip -r -9 data/tracks.zip data/tracks data/track_ids.csv


# deaktywacja venv
deactivate

