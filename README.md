
![Python](https://img.shields.io/badge/Python-3.4%20%7C%203.5%20%7C%203.6-blue.svg)
![System](https://img.shields.io/badge/System-Mac%20OS%20X-brightgreen.svg)
![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)

# Overview

**Music Downloader** is the command line tool to download music from YouTube and SoundCloud.<br/>
This package requires the Python interpreter 3.4+ and tested only on Mac OS X Mojave.<br/>
It is released to the public domain, which means you can modify it, redistribute it or use it however you like.



# Installation

You need to install following dependencies before using Music Downloader.

```
$ brew install ffmpeg atomicparsley libmagic
```

Music Downloader can be installed using pip.

```
$ pip install --upgrade music-dl
```




# Usage

## Options

Music Downloader offers following options.

```
$ music-dl --help

Music Downloader 0.2.1

Usage: music-dl --url http://youtube.com/watch?v=<video_id>&list=<playlist_id>
                --dir ~/Music/Download
                --codec m4a
                --bitrate 128
                --no-track-number
                --no-compilation

Optional Arguments:
  -u, --url <str>                   URL to download. [Default: Clipboard Value]
  -d, --dir <str>                   Path to working directory. [Default: /Users/kojirof/Music/Downloads]
  -c, --codec <str> [m4a,mp3,flac]  Preferred audio codec. [Default: m4a]
  -b, --bitrate <int>               Preferred audio bitrate. [Default: 198]
  -s, --start <int>                 Index specifying playlist item to start at.
                                    Default value is index of first song on playlist. [Default: 1]
  -e, --end <int>                   Index specifying playlist item to end at.
                                    Default value is index of last song on playlist. [Default: 0]
  --no-artwork                      Forbid adding artwork to audio metadata.
  --no-track-number                 Forbid adding track number to audio metadata.
  --no-album-title                  Forbid adding album title to audio metadata.
  --no-album-artist                 Forbid adding album artist to audio metadata.
  --no-composer                     Forbid adding composer to audio metadata.
  --no-compilation                  Forbid adding part of compilation flag to audio metadata.
  --open-dir                        Open download directory after all songs are downloaded.
  --verbose                         Print verbose message.
  --help                            Show this help message and exit.

```


## Example

Music Downloader can download music by combining various options. Here are some examples.

### Download music of the URL copied to the clipboard. (No option requried)

```
$ music-dl
```

### Download single song

```
$ music-dl --url https://www.youtube.com/watch?v=video_id

$ music-dl --url https://soundcloud.com/artist_id/song_id
```

### Set audio quality and download all songs from playlist to specific directory

```
$ music-dl --url https://www.youtube.com/watch?v=video_id&list=playlist_id \
           --dir ~/Downloads/Music \
           --codec m4a \
           --bitrate 128

$ music-dl --url https://soundcloud.com/artist_id/sets/playlist_id \
           --dir ~/Downloads/Music \
           --codec mp3 \
           --bitrate 320
```

### Download songs from the 7th to 10th of playlist

```
$ music-dl --url https://www.youtube.com/watch?v=video_id&list=playlist_id \
           --playlist-start 7 \
           --playlist-end 10

$ music-dl --url https://soundcloud.com/artist_id/sets/playlist_id \
           --playlist-start 7 \
           --playlist-end 10
```

### Download songs from the 7th to the end of playlist

```
$ music-dl --url https://www.youtube.com/watch?v=video_id&list=playlist_id \
           --playlist-start 7

$ music-dl --url https://soundcloud.com/artist_id/sets/playlist_id \
           --playlist-start 7
```

### Download songs without adding track number to metadata

```
$ music-dl --url https://www.youtube.com/watch?v=video_id&list=playlist_id \
           --no-track-number

$ music-dl --url https://soundcloud.com/artist_id/sets/playlist_id \
           --no-track-number
```





# Known Issues

- If you requested an official YouTube playlist (aka YouTube Mix), downloaded songs are different from the playlist displayed on your browser, except for the first song. This is caused that YouTube generates a random playlist for each request.<br>
If you request to resume downloading the same playlist, the consistency of track numbers registered in the metadata will be lost.



# Copyright

Music Downloader is released into the public domain by the copyright holders.<br/>
This README file was written by [Gumob](https://github.com/gumob) and is likewise released into the public domain.
