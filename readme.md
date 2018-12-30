# AlbumShuffle

A Python script that uses the unofficial Google Play Music API https://github.com/simon-weber/gmusicapi to shuffle your library by album rather by individual songs, as the artists intended.

It creates a playlist called "Album shuffle" and then adds random albums from your library until the playlist has at least 900 tracks.

Running the script again will remove any tracks from the start of the playlist that you've played (so you can easily switch between devices) and then add more albums until you're back up to 900 tracks.

This is very much written for my own purposes, but if you want updates to match your own requirements then I'm open to issues and PRs :)