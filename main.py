import requests
from pprint import pprint
import credentials
from authlib.integrations.requests_client import OAuth2Session
import flask_server
import webbrowser
import json

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
    if len(r['items']) < 50:
        return playlists
    return get_playlists(auth, r['next'], playlists)

def get_user(auth):
    headers = {'Authorization': f"Bearer {auth['access_token']}"}
    r = requests.get('https://api.spotify.com/v1/me', headers=headers)
    return r.json()

def get_tacks(playlist):
    url = ""

auth = get_token()
playlists = get_playlists(auth)
print("Please pick a playlist to convert to a BeatSaver playlist: ")
for n, playlist in enumerate(playlists):
    print(f"{n+1}. {playlist['name']} – {playlist['tracks']['total']}")
playlist_number = int(input('Playlist number: '))
pl = playlists[playlist_number-1]
print(pl['tracks'])
