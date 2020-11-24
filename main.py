import requests
from pprint import pprint
import credentials
from authlib.integrations.requests_client import OAuth2Session
import flask_server
import webbrowser
import json
from bs4 import BeautifulSoup
import re
from difflib import ndiff

def compare(str1, str2):
    counter = {"+": 0, "-": 0}
    distance = 0
    for edit_code, *_ in ndiff(str1, str2):
        if edit_code == " ":
            distance += max(counter.values())
            counter = {"+": 0, "-": 0}
        else:
            counter[edit_code] += 1
    distance += max(counter.values())
    return distance

words = lambda track_name: re.sub('[\(\)\[\]\-]', '', track_name.lower())

def get_token():
    redirect_uri = 'http://localhost:5000/'
    scope = ['playlist-read-private']
    oauth = OAuth2Session("3325d6c78df64d53884a942d3f8ccf88", redirect_uri=redirect_uri, scope=scope)
    auth_url = "https://accounts.spotify.com/authorize"
    authorization_url, state = oauth.create_authorization_url(auth_url, response_type="token")
    webbrowser.open(authorization_url)
    print(f"Please go to {authorization_url} to authorize access.")
    callback_url = input("Waiting for credentials. Please paste callback URL: ")
    auth = dict(kv.split('=') for kv in callback_url.split("#")[1].split('&'))
    #auth = flask_server.get_cred()
    print("Got credentials.")
    return auth

def get_playlists(auth, url="", playlists=[]):
    if not url:
        url = f"https://api.spotify.com/v1/me/playlists?offset=0&limit=50"
    headers = {'Authorization': f"Bearer {auth['access_token']}"}
    r = requests.get(url, headers=headers).json()
    playlists += r['items']
    if len(r['items']) < 50 or not r['next']:
        return playlists
    return get_playlists(auth, r['next'], playlists)

def get_user(auth):
    headers = {'Authorization': f"Bearer {auth['access_token']}"}
    r = requests.get('https://api.spotify.com/v1/me', headers=headers)
    return r.json()

def get_tracks(auth, url="", tracks=[]):
    headers = {'Authorization': f"Bearer {auth['access_token']}"}
    r = requests.get(url, headers=headers).json()
    tracks += r['items']
    if len(r['items']) < 50 or not r['next']:
        return tracks
    return get_tracks(auth, r['next'], tracks)

def search(track):
    artist_names = [artist['name'] for artist in track['track']['artists']]
    query = f"{'+'.join(track['track']['name'].split(' (')[0].split())}+{'+'.join(artist_names[0].split())}".lower()
    r = requests.get(f"https://bsaber.com/?s={query}&orderby=relevance&order=DESC")
    s = BeautifulSoup(r.content, 'html.parser')
    results = [result.find('a').text.strip().split(' - ')[0] for result in s.find_all('h4')[1:-1]]
    if results:
        results.sort(key=lambda x: compare(words(track['track']['name']), x))
        print(f"   [>] Matched Track: {results[0]}")
    else:
        print("   [x] No match found")

auth = get_token()
playlists = get_playlists(auth)
print("Please pick a playlist to convert to a BeatSaver playlist: ")
for n, playlist in enumerate(playlists):
    print(f"{n+1}. {playlist['name']} – {playlist['tracks']['total']}")
playlist_number = int(input('Playlist number: '))
pl = playlists[playlist_number-1]
tracks = get_tracks(auth, url=pl['tracks']['href'])
for track in tracks:
    artist_names = [artist['name'] for artist in track['track']['artists']]
    print(f"[~] Searching for track: {track['track']['name']} - {', '.join(artist_names)}")
    search(track)
