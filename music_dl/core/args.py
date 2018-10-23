#!/usr/bin/env python
# coding: utf-8

import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, RawTextHelpFormatter, OPTIONAL, SUPPRESS, ZERO_OR_MORE
from gettext import gettext as _

import clipboard
import colorama
import pkg_resources


def parse_args():
    """ Custom Argument Parser """

    class CustomArgumentParser(ArgumentParser):

        def format_help(self):
            return '\n' + super(CustomArgumentParser, self).format_help() + '\n'

        def format_usage(self):
            formatter = self._get_formatter()
            formatter.add_usage(self.usage, self._actions,
                                self._mutually_exclusive_groups)
            return '\n' + formatter.format_help()

        def error(self, message):
            self.print_usage(sys.stderr)
            args = {'prog': self.prog, 'message': message}
            # msg = colorama.Fore.RED + _('\n[%(prog)s] Error: %(message)s\n') % args + colorama.Style.RESET_ALL
            msg = colorama.Fore.RED + _('\nError: %(message)s\n\n') % args + colorama.Style.RESET_ALL
            msg += 'Type "music-dl --help" to show help. \n\n'
            self.exit(2, msg)

    class CustomFormatter(ArgumentDefaultsHelpFormatter, RawTextHelpFormatter):

        def __init__(self, prog, indent_increment=2, max_help_position=40, width=800):
            """
            Initializer that overrides help message indent and positioning
            """
            super().__init__(prog, indent_increment, max_help_position, width)

        def add_usage(self, usage, actions, groups, prefix=None):
            """
            The function that removes prefix from usage
            """
            if prefix is None:
                prefix = ''
                return super(CustomFormatter, self).add_usage(usage, actions, groups, prefix)

        def _format_action_invocation(self, action):
            """
            The function that suppresses duplicated metavars
            https://stackoverflow.com/questions/23936145/python-argparse-help-message-disable-metavar-for-short-options
            """
            if not action.option_strings:
                metavar, = self._metavar_formatter(action, action.dest)(1)
                return metavar
            else:
                parts = []
                # if the Optional doesn't take a value, format is:
                #    -s, --long
                if action.nargs == 0:
                    parts.extend(action.option_strings)

                # if the Optional takes a value, format is:
                #    -s ARGS, --long ARGS
                # change to
                #    -s, --long ARGS
                else:
                    default = action.dest.upper()
                    args_string = self._format_args(action, default)
                    for option_string in action.option_strings:
                        # parts.append('%s %s' % (option_string, args_string))
                        parts.append('%s' % option_string)
                    parts[-1] += ' %s' % args_string
                return ', '.join(parts)

        def _get_help_string(self, action):
            help_msg = action.help
            if '%(default)' not in action.help:
                if action.default is not SUPPRESS:
                    defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                    if action.option_strings or action.nargs in defaulting_nargs:
                        if not isinstance(action.default, bool) and action.default is not None:
                            help_msg += ' [Default: %(default)s]'

            return help_msg

    default_dir = os.path.expanduser('~/Music/Downloads')
    pkg_info = pkg_resources.require("music_dl")[0]
    description = "Music Downloader {}".format(pkg_info.version)
    usage = """
Usage: %(prog)s --url http://youtube.com/watch?v=<video_id>&list=<playlist_id>
                --dir ~/Music/Download
                --codec m4a
                --bitrate 128
                --no-track-number
                --no-compilation"""

    """ Parse arguments """

    parser = CustomArgumentParser(
        description=usage,
        usage=description,
        add_help=False,
        formatter_class=CustomFormatter,
    )

    parser._positionals.title = 'Positional Arguments'
    parser._optionals.title = 'Optional Arguments'

    parser.add_argument('-u', '--url', action='store', type=str, metavar='<str>',
                        help='URL to download. [Default: Clipboard Value]')
    parser.add_argument('-d', '--dir', action='store', type=str, metavar='<str>', default=default_dir,
                        help='Path to working directory.')
    parser.add_argument('-c', '--codec', action='store', type=str, metavar='<str> [m4a,mp3,flac]', default='m4a', choices=['m4a', 'mp3', 'flac'],
                        help='Preferred audio codec.')
    parser.add_argument('-b', '--bitrate', action='store', type=int, metavar='<int>', default=198,
                        help='Preferred audio bitrate.')
    parser.add_argument('-s', '--start', action='store', type=int, metavar='<int>', dest='playlist_start', default=1,
                        help='Index specifying playlist item to start at.\nDefault value is index of first song on playlist.')
    parser.add_argument('-e', '--end', action='store', type=int, metavar='<int>', dest='playlist_end', default=0,
                        help='Index specifying playlist item to end at.\nDefault value is index of last song on playlist.')
    parser.add_argument('--no-artwork', action='store_true',
                        help='Forbid adding artwork to audio metadata.')
    parser.add_argument('--no-track-number', action='store_true',
                        help='Forbid adding track number to audio metadata.')
    parser.add_argument('--no-album-title', action='store_true',
                        help='Forbid adding album title to audio metadata.')
    parser.add_argument('--no-album-artist', action='store_true',
                        help='Forbid adding album artist to audio metadata.')
    parser.add_argument('--no-composer', action='store_true',
                        help='Forbid adding composer to audio metadata.')
    parser.add_argument('--no-compilation', action='store_true',
                        help='Forbid adding part of compilation flag to audio metadata.')
    parser.add_argument('--open-dir', action='store_true',
                        help='Open download directory after all songs are downloaded.')
    # parser.add_argument('--clear-cache', action='store_true',
    #                     help='Clear cache directory.')
    parser.add_argument('--verbose', action='store_true',
                        help='Print verbose message.')
    parser.add_argument('--help', action='help', default=SUPPRESS,
                        help='Show this help message and exit.')

    parser_args = parser.parse_args()
    parser_args.url = parser_args.url if parser_args.url is not None else clipboard.paste()
    parser_args.dir = parser_args.dir if parser_args.dir is not None else default_dir

    return parser_args
