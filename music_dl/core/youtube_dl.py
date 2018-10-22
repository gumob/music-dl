#!/usr/bin/env python
# coding: utf-8

import os
import re
from enum import Enum
from urllib.parse import urlparse

import colorama
from tldextract import tldextract


class YDLHelper(object):
    """"""""""""""" Initializer """""""""""""""

    def __init__(self):
        self.__preprocess_queue_index = 0
        self.__preprocess_queue_total = 0

        self.__download_callback = None
        self.__download_queue_index = 0
        self.__download_queue_total = 0
        self.__download_queue_indices = None

    """"""""""""""" Preprocess """""""""""""""

    def get_preprocess_option(self, download_url, audio_codec='m4a', audio_bitrate=198, playlist_start=1, playlist_end=0, verbose=True):
        """
        The function that creates youtube-dl options.
        More info is available at https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py

        :param str download_url: Directory to download songs
        :param str audio_codec: Preferred audio codec
        :param int audio_bitrate: Preferred audio bitrate
        :param int playlist_start: Playlist item to start at
        :param int playlist_end: Playlist item to end at
        :param bool verbose: Print verbose message

        :rtype dict
        :return ydl_opts: Options for youtube-dl
        """
        self.__preprocess_queue_index = playlist_start
        if 0 < playlist_end < playlist_start:
            playlist_end = playlist_start
            self.__preprocess_queue_total = 1
        elif playlist_end <= 0:
            self.__preprocess_queue_total = 0
        else:
            self.__preprocess_queue_index = playlist_end - playlist_start

        ydl_opts = {
            'format': 'bestaudio/best',  # Video format code. See https://github.com/rg3/youtube-dl/blob/master/youtube_dl/options.py for more information
            'writethumbnail': True,  # Write the thumbnail image to a file
            'ignoreerrors': True,  # Do not stop on download errors.
            'nooverwrites': True,  # Prevent overwriting files.
            'forceurl': True,  # Force printing final URL.
            'forcethumbnail': True,  # Force printing thumbnail URL.
            'forcefilename': True,  # Force printing final filename.
            'listformats': False,  # Print an overview of available video formats and exit.
            'postprocessors': [  # More info are available at https://github.com/rg3/youtube-dl/tree/master/youtube_dl/postprocessor
                {
                    'key': 'FFmpegMetadata',
                },
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_codec,
                    'preferredquality': str(audio_bitrate),
                }
            ],
            'logger': YDLLogger(verbose),
        }

        tld_parsed = tldextract.extract(download_url)
        if tld_parsed.domain == 'youtube':
            url_parsed = urlparse(download_url)
            if ('watch?' in url_parsed and 'v=' in url_parsed and 'list=' in url_parsed) or ('playlist?' in url_parsed and 'list=' in url_parsed):
                ydl_opts['playliststart'] = playlist_start
                ydl_opts['playlistend'] = playlist_end

        elif tld_parsed.domain == 'soundcloud':
            is_match = re.match(r"^(http(s)?://)([\w\.]+)?soundcloud\.com/(.*)/sets/(.*)", download_url)
            if is_match:
                ydl_opts['playliststart'] = playlist_start
                ydl_opts['playlistend'] = playlist_end

        return ydl_opts

    """"""""""""""" Download """""""""""""""

    def get_download_option(self, download_dir, hook, audio_codec='m4a', audio_bitrate=198, queue_indices=None, verbose=True):
        """
        The function that creates youtube-dl options.
        More info is available at https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py

        :param str download_dir: Directory to download songs
        :param function hook: Download hook that called when download is finished
        :param list queue_indices: Indices to download
        :param str audio_codec: Preferred audio codec
        :param int audio_bitrate: Preferred audio bitrate
        :param bool verbose: Print verbose message

        :rtype dict
        :return ydl_opts: Options for youtube-dl
        """
        self.__download_callback = hook

        if queue_indices is not None:
            self.__download_queue_indices = queue_indices
            self.__download_queue_index = 1
            self.__download_queue_total = len(queue_indices)

        ydl_opts = {
            # 'outtmpl': Template for output names. See https://github.com/rg3/youtube-dl/blob/master/README.md#output-template for more information
            # 'outtmpl': os.path.join(download_dir, '[%(playlist_index)s-{}] %(title)s.%(ext)s'.format(len(__download_queue_indices))),
            # 'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
            # 'outtmpl': os.path.join(download_dir, '%(id)s.%(ext)s'),
            'format': 'bestaudio/best',  # Video format code. See https://github.com/rg3/youtube-dl/blob/master/youtube_dl/options.py for more information
            'writethumbnail': True,  # Write the thumbnail image to a file
            'ignoreerrors': True,  # Do not stop on download errors.
            'nooverwrites': True,  # Prevent overwriting files.
            'forceurl': True,  # Force printing final URL.
            'forcethumbnail': True,  # Force printing thumbnail URL.
            'forcefilename': True,  # Force printing final filename.
            'listformats': False,  # Print an overview of available video formats and exit.
            # 'geo_bypass': True,  # Bypass geographic restriction via faking X-Forwarded-For HTTP header.
            'postprocessors': [  # More info are available at https://github.com/rg3/youtube-dl/tree/master/youtube_dl/postprocessor
                # {
                #     'key': 'EmbedThumbnail',  # Embedding thumbnail in m4a is not supported. Using mutagen instead.
                # },
                {
                    'key': 'FFmpegMetadata',
                },
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_codec,
                    'preferredquality': str(audio_bitrate),
                }
            ],
            'logger': YDLLogger(verbose),
            'progress_hooks': [self.__download_progress_hook],
        }

        # Specify indices of playlist to download
        if self.__download_queue_indices is not None and len(self.__download_queue_indices) > 0:
            ydl_opts['outtmpl'] = os.path.join(download_dir, '%(id)s.%(ext)s')  # Template for output names. See https://github.com/rg3/youtube-dl/blob/master/README.md#output-template for more information
            ydl_opts['playlist_items'] = ','.join([str(index) for index in self.__download_queue_indices])
        else:
            ydl_opts['outtmpl'] = os.path.join(download_dir, '%(title)s.%(ext)s')  # Template for output names. See https://github.com/rg3/youtube-dl/blob/master/README.md#output-template for more information
            pass

        return ydl_opts

    def __download_progress_hook(self, data):
        """
        The function that get called on download progress, with a dictionary with the entries.
        More info is available at https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py

        :param dict data: Progress information for each queue
        """
        if data['status'] == 'finished':

            # Playlist
            if self.__download_queue_index > 0:
                # Callback to MusicDL
                self.__download_callback(data, self.__download_queue_index, self.__download_queue_total)
                # Increment queue index
                self.__download_queue_index += 1

            # Single song
            else:
                # Callback to MusicDL
                self.__download_callback(data)


class YDLQueueStatus(Enum):
    ready = 'ready'
    failed = 'failed'
    finished = 'finished'


class YDLLogger(object):
    def __init__(self, verbose=True):
        colorama.init(autoreset=True)
        self.verbose = verbose

    def debug(self, msg):
        if self.verbose:
            print(colorama.Fore.BLUE + msg)

    def info(self, msg):
        print(msg)

    def warning(self, msg):
        print(colorama.Fore.YELLOW + msg)

    def error(self, msg):
        print(colorama.Fore.RED + msg)
