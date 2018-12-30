import os
import random
import sys

from functools import reduce
from itertools import takewhile

from gmusicapi import Mobileclient
from gmusicapi.exceptions import InvalidDeviceId
from gmusicapi.appdirs import my_appdirs

playlistName = 'Album shuffle'

# Initialise the Google Play Music API
mc = Mobileclient()
mc.__init__()

print('Logging in')
if os.path.isfile(mc.OAUTH_FILEPATH):
    # We have credentials - do a normal login.
    # Need to get a valid device ID from the exception text when using an invalid ID.
    deviceId = 'deviceId'
    while True:
        try:
            mc.oauth_login(deviceId)
            break
        except InvalidDeviceId as exc:
            deviceId = str(exc).split('\n')[1].replace('* ', '')
else:
    # First time login - do OAuth in browser
    mc.perform_oauth(open_browser=True)

# Find the playlist if it exists, or create it
print('Finding playlist "{0}"'.format(playlistName))
existingPlaylist = list(filter(lambda p: p['name'] == playlistName, mc.get_all_playlists()))
if len(existingPlaylist) > 0:
    playlistId = existingPlaylist[0]['id']
else:
    playlistId = mc.create_playlist(playlistName)

print('Fetching data from server')

# Get all songs in library
allTracks = mc.get_all_songs()

# Get contents of our playlist
playlist = list(filter(lambda p: p['id'] == playlistId, mc.get_all_user_playlist_contents()))[0]

# If a track's been modified since it was added, it's been played.
# Find all the played tracks at the start of the playlist.
playedTracks = list(takewhile(
    lambda pt: pt['creationTimestamp'] < list(filter(lambda t: t['id'] == pt['trackId'], allTracks))[0]['lastModifiedTimestamp'],
    playlist['tracks']))
playedTrackIds = list(map(lambda pt: pt['id'], playedTracks))

# Remove the played tracks from the playlist
mc.remove_entries_from_playlist(playedTrackIds)
print('Removed {0} played tracks'.format(len(playedTrackIds)))

trackCount = len(playlist['tracks']) - len(playedTrackIds)
print('{0} tracks on playlist'.format(trackCount))

# Pick out all the albums from the songs our library and shuffle them
albums = list(set(map(lambda t: t['albumArtist'] + '/' + t['album'], allTracks)))
random.shuffle(albums)

# Keep adding albums until we've got at least 900 tracks on the playlist
while trackCount < 900:
    album = albums.pop(0)

    # Get the tracks on the album sorted by track number
    albumTracks = list(sorted(
        filter(lambda t: t['albumArtist'] + '/' + t['album'] == album, allTracks),
        key = lambda t: t['discNumber'] * 1000 + t['trackNumber']))

    # Add the tracks to the playlist
    trackIds = list(map(lambda t: t['id'], albumTracks))
    mc.add_songs_to_playlist(playlistId, trackIds)
    trackCount = trackCount + len(trackIds)
    print('Added {0} tracks from {1}'.format(len(trackIds), album))
