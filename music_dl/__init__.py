#!/usr/bin/env python
# coding: utf-8

import argparse
import os

import clipboard
import pkg_resources

from music_dl.MusicDL import MusicDL

__version__ = '0.1.27'
__license__ = 'MIT'
__author__ = 'Gumob'
__author_email__ = 'hello@gumob.com'
__url__ = 'http://github.com/gumob/music-dl'
__copyright__ = 'Copyright (C) 2018 Gumob'
__all__ = ['main', 'MusicDL']


def main():
    # Parse Argument
    pkg_info = pkg_resources.require("music_dl")[0]
    default_dir = os.path.expanduser('~/Music/Downloads')

    class CapitalisedHelpFormatter(argparse.HelpFormatter):
        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = 'Usage: '
                return super(CapitalisedHelpFormatter, self).add_usage(
                    usage, actions, groups, prefix)

    parser = argparse.ArgumentParser(
        prog='music-dl',
        description='Music Downloader - Command line tool to download music from YouTube and SoundCloud',
        # add_help=True,
        add_help=False,
        epilog=pkg_info,
        formatter_class=CapitalisedHelpFormatter,
    )

    parser._positionals.title = 'Positional arguments'
    parser._optionals.title = 'Optional arguments'
    argparse._HelpAction(option_strings=['-h', '--help'], dest='help', default='==SUPPRESS==', help='Show this help message and exit.')

    # parser.add_argument('-u', '--url', action='store', type=str,
    #                     help='URL to download. Without this argument, URL is read from clipboard.')
    # parser.add_argument('-d', '--dir', action='store', type=str,
    #                     help='Path to working directory. Default value is {}.'.format(default_dir))
    # parser.add_argument('-ac', '--codec', action='store', type=str, default='m4a', choices=['m4a', 'mp3', 'flac'],
    #                     help='Preferred audio codec. [available=m4a,mp3,flac default=m4a]')
    # parser.add_argument('-ab', '--bitrate', action='store', type=int, default=198,
    #                     help='Preferred audio bitrate. [default=198]')
    # parser.add_argument('-ps', '--playlist-start', action='store', type=int, default=1,
    #                     help='Index specifying playlist item to start at. [default=1 (index of first song on playlist)]')
    # parser.add_argument('-pe', '--playlist-end', action='store', type=int, default=0,
    #                     help='Index specifying playlist item to end at. [default=0 (index of last song on playlist)]')
    # parser.add_argument('--no-artwork', action='store_true',
    #                     help='Forbid adding artwork to audio metadata.')
    # parser.add_argument('--no-track-number', action='store_true',
    #                     help='Forbid adding track number to audio metadata.')
    # parser.add_argument('--no-album-title', action='store_true',
    #                     help='Forbid adding album title to audio metadata.')
    # parser.add_argument('--no-album-artist', action='store_true',
    #                     help='Forbid adding album artist to audio metadata.')
    # parser.add_argument('--no-composer', action='store_true',
    #                     help='Forbid adding composer to audio metadata.')
    # parser.add_argument('--no-compilation', action='store_true',
    #                     help='Forbid adding part of compilation flag to audio metadata.')
    # parser.add_argument('--open-dir', action='store_true',
    #                     help='Open download directory after all songs are downloaded.')
    # parser.add_argument('--clear-cache', action='store_true',
    #                     help='Clear cache directory.')
    # parser.add_argument('--verbose', action='store_true',
    #                     help='Print verbose message.')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit.')

    args = parser.parse_args()
    # args.url = args.url if args.url is not None else clipboard.paste()
    # args.dir = args.dir if args.dir is not None else default_dir

    # Execute download
    # mdl = MusicDL(
    #     download_url=args.url,
    #     working_dir=args.dir,
    #     audio_codec=args.codec,
    #     audio_bitrate=args.bitrate,
    #     playlist_start=int(args.playlist_start),
    #     playlist_end=int(args.playlist_end),
    #     no_artwork=args.no_artwork,
    #     no_album_title=args.no_album_title,
    #     no_album_artist=args.no_album_artist,
    #     no_track_number=args.no_track_number,
    #     no_composer=args.no_composer,
    #     no_compilation=args.no_compilation,
    #     open_dir=args.open_dir,
    #     # clear_cache=args.clear_cache,
    #     verbose=args.verbose
    # )
    # mdl.download()
