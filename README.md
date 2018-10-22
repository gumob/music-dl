
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

-u, --url               URL to download. Without this argument, URL is read
                        from clipboard.
-d, --dir               Path to working directory. [default="~/Music/Downloads"]
-ac, --codec            Preferred audio codec.
                        [available=m4a,mp3,flac default=m4a]
-ab, --bitrate'         Preferred audio bitrate. [default=198]
-ps, --playlist-start   Index specifying playlist item to start at.
                        [default=1 (index of first song on playlist)]
-pe, --playlist-end     Index specifying playlist item to end at.
                        [default=0 (index of last song on playlist)]
--no-artwork            Forbid adding artwork to audio metadata.
--no-track-number       Forbid adding track number to audio metadata.
--no-album-title        Forbid adding album title to audio metadata.
--no-album-artist       Forbid adding album artist to audio metadata.
--no-composer           Forbid adding composer to audio metadata.
--no-compilation        Forbid adding part of compilation flag to audio metadata.
--open-dir              Open download directory after all songs are downloaded.
--verbose               Print verbose message.
--help                  Print this help text and exit.
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

- If you requested an official YouTube playlist (aka YouTube Mix), downloaded songs are different from the playlist displayed on your browser, except for the first song. This is caused that YouTube generates random playlist for each requests.<br>
If you request to resume downloading the same playlist, the consistency of track numbers registered in the metadata will be lost.



# Copyright

Music Downloader is released into the public domain by the copyright holders.<br/>
This README file was written by [Gumob](https://github.com/gumob) and is likewise released into the public domain.
