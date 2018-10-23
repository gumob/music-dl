#!/usr/bin/env python
# coding: utf-8

from music_dl.MusicDL import MusicDL
from music_dl.core.args import parse_args

__version__ = '0.2.0'
__license__ = 'MIT'
__author__ = 'Gumob'
__author_email__ = 'hello@gumob.com'
__url__ = 'http://github.com/gumob/music-dl'
__copyright__ = 'Copyright (C) 2018 Gumob'
__all__ = ['main', 'MusicDL']


def main():
    args = parse_args()

    """ Execute download """

    mdl = MusicDL(
        download_url=args.url,
        working_dir=args.dir,
        audio_codec=args.codec,
        audio_bitrate=args.bitrate,
        playlist_start=int(args.playlist_start),
        playlist_end=int(args.playlist_end),
        no_artwork=args.no_artwork,
        no_album_title=args.no_album_title,
        no_album_artist=args.no_album_artist,
        no_track_number=args.no_track_number,
        no_composer=args.no_composer,
        no_compilation=args.no_compilation,
        open_dir=args.open_dir,
        # clear_cache=args.clear_cache,
        verbose=args.verbose
    )
    mdl.download()
