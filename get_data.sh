# ściągnięcie notowań
python download_charts.py

# skompaktowanie notowań i przygotowanie listy TrackIDs
python compact_data.py charts

# pobranie cech audio i danych o artystach z TrackIDs
python grab_audiofeatures.py

# skompaktowanie tracków i artystów
python compact_data.py tracks
