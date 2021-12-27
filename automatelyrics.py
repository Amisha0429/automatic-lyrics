'''

~  ENVIRONMENT VARIABLES  ~

export SPOTIPY_CLIENT_ID='6c35fb37a77e413a812ad4a84fc72666'
export SPOTIPY_CLIENT_SECRET='8e71fd864fc1440ba26a1a0e9afd0e71'
export SPOTIPY_REDIRECT_URI='https://google.com'
export GENIUS_ACCESS_TOKEN='cseuqCPpX-hkD_kkfCd4A3ndDiuvidptOdUEI_PcLxmR8CWVkpoVDS53NKjm_0sm' 
'''

# Import modules
import os
import sys
import json
import time
import signal
import spotipy
import threading
import webbrowser
import lyricsgenius as lg
import spotipy.util as util
from json.decoder import JSONDecodeError


def timed_input(prompt, timeout, timeout_message):
    def timeout_error(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM, timeout_error)
    signal.alarm(timeout)
    try:
        choice = input(prompt)
        signal.alarm(0)
        return choice
    except TimeoutError:
        if timeout_message:
            print(timeout_message)
        signal.signal(signal.SIGALRM, signal.SIG_IGN)
        return None

def sleeping(duration, result, index):
    time.sleep(duration)
    result[index] = True
    sys.exit()

# Scope required for currently playing
scope = "user-read-currently-playing"

# Create our spotifyOAuth object
spotifyOAuth = spotipy.SpotifyOAuth(client_id=os.environ['SPOTIPY_CLIENT_ID'],client_secret=os.environ['SPOTIPY_CLIENT_SECRET'],redirect_uri=os.environ['SPOTIPY_REDIRECT_URI'],scope=scope)
token = spotifyOAuth.get_access_token()

# Create our spotifyObject
spotifyObject = spotipy.Spotify(auth=token['access_token'])

# Create out geniusObject
access_token = os.environ['GENIUS_ACCESS_TOKEN']
genius = lg.Genius(access_token)

song_number = 1
result = [False]
index = 0

while True:
    print()
    print(">> Updating current track [" + str(song_number) + "]")
    print()
    song_number += 1

    current = spotifyObject.currently_playing()
    current_type = current['currently_playing_type']

    if current_type == "track":
        artist = current['item']['artists'][0]['name']
        title = current['item']['name']
        length_ms = current['item']['duration_ms']
        progress_ms = current['progress_ms']
        time_ms = length_ms - progress_ms
        time_sec = int((time_ms/1000))
        search_query = artist + " " + title

        song = genius.search_song(title=title, artist=artist)

        try:
            lyrics = song.lyrics
            url = song.url
            print(lyrics)
            print()
        except:
            print(">> The Lyrics were not found")
            print()

        # Thread to track end of song without clogging main thread
        thread = threading.Thread(target=sleeping, args=(time_sec, result, index))
        thread.start()

        print(">> Going to sleep for about " + str(time_sec) + " seconds")
        print()
        print(">> Enter 0 to open lyrics in browser")
        print(">> Enter 1 for the Artist info")
        print(">> Click Enter to continue")
        print(">> Cmd + C to exit")
        print()

        start = time.time()
        while result[index] == False:
            user_input = timed_input(">> ", time_sec, "Next track coming up")
            if user_input == "0":
                print(">> Showing Browser: ")

                try:
                    webbrowser.open(url, new=0, autoraise=False)
                except:
                    print(">> Could not find URL")

            end = time.time()
            time_sec = time_sec - int(abs(start - end))
            
        # reset
        result[index] = False

    elif current_type == "ad":
        print(">> AD playing now. On sleep for a while.")
        time.sleep(60)

    # Check if access token has expired or not
    if spotifyOAuth.is_token_expired(token) == True:
        print(">> Access token expired. Trying again.")

        token = spotifyOAuth.get_access_token()
        spotifyObject = spotipy.Spotify(auth=token['access_token'])