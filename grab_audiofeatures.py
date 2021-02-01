# %%
import spotipy
from spotipy import util

import time
import json
from os.path import exists
import configparser

from tqdm import tqdm

import pandas as pd

# %%
# Spotify stuff
config = configparser.ConfigParser()
config.read('config.ini')

SpotifyClientID = config['SpotifyAPI']['SpotifyClientID']
SpotifyClientSecret = config['SpotifyAPI']['SpotifyClientSecret']
SpotifyUsername = config['SpotifyAPI']['SpotifyUsername']

SpotifyScope = 'user-read-currently-playing,user-read-playback-state'

# %%
# connect to Spotify


def revoke_token():
    token = util.prompt_for_user_token(SpotifyUsername,
                                       SpotifyScope,
                                       client_id=SpotifyClientID,
                                       client_secret=SpotifyClientSecret,
                                       redirect_uri='http://localhost/')

    spot = spotipy.Spotify(auth=token)
    return spot


# %%

def get_track_features(trackid):
    # pobieramy cechy dla tego track id
    try:
        audio_features = sp.audio_features(trackid)
    except Exception as e:
        print(e)
        return {'item_id': trackid}

    if audio_features:
        return {
            'item_id': trackid,
            'danceability': audio_features[0].get('danceability'),
            'energy': audio_features[0].get('energy'),
            'key': audio_features[0].get('key'),
            'loudness': audio_features[0].get('loudness'),
            'mode': audio_features[0].get('mode'),
            'speechiness': audio_features[0].get('speechiness'),
            'acousticness': audio_features[0].get('acousticness'),
            'instrumentalness': audio_features[0].get('instrumentalness'),
            'liveness': audio_features[0].get('liveness'),
            'valence': audio_features[0].get('valence'),
            'tempo': audio_features[0].get('tempo'),
            'time_signature': audio_features[0].get('time_signature'),
        }

    return {'item_id': trackid}


# %%


def get_track_info(trackid):
    track_info = sp.track(trackid)
    audio_features = get_track_features(trackid)

    audio_features['album_name'] = track_info['album']['name']
    audio_features['album_release_date'] = track_info['album']['release_date']
    audio_features['album_release_year'] = int(
        track_info['album']['release_date'][:4])
    audio_features['track_duration_ms'] = track_info['duration_ms']
    audio_features['track_explict'] = track_info['explicit']
    audio_features['track_popularity'] = track_info['popularity']
    audio_features['track_artist_id'] = track_info['artists'][0]['id']

    return audio_features


# %%
def get_artist_info(artist_id):
    artist_data = sp.artist(artist_id)

    artist_data_res = dict()
    artist_data_res['id'] = artist_data['id']
    artist_data_res['genre'] = artist_data['genres'][0] if artist_data['genres'] else []
    artist_data_res['genres'] = artist_data['genres']
    artist_data_res['popularity'] = int(artist_data['popularity'])
    artist_data_res['followers'] = int(artist_data['followers']['total'])

    return artist_data_res


# %%
sp = revoke_token()
trackids = pd.read_csv('track_ids.csv')

# %%
for trackid in tqdm(trackids['TrackID']):

    # ściągamy dane o tracku jeśli jeszcze ich nie mamy
    file_name_track = f'track_data/{trackid}.json'
    if not exists(file_name_track):
        try:
            track_data = get_track_info(trackid)
            with open(file_name_track, "w") as fp:
                json.dump(track_data, fp)

        except Exception as e:
            print(e)
            time.sleep(2)
            sp = revoke_token()

    # ściągamy dane o artyście - jeśli jeszcze ich nie mamy
    file_name_artist = f"artist_data/{track_data['track_artist_id']}.json"
    if not exists(file_name_artist):
        try:
            artist_data = get_artist_info(track_data['track_artist_id'])
            with open(file_name_artist, "w") as fp:
                json.dump(artist_data, fp)

        except Exception as e:
            print(e)
            time.sleep(2)
            sp = revoke_token()
