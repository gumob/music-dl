#!/usr/bin/env python
# coding: utf-8

import atexit
import logging
import os
import platform
import subprocess
from urllib.parse import urlparse

import colorama
import pkg_resources
from tldextract import tldextract
from youtube_dl import YoutubeDL

from music_dl.core.error import PlaylistParameterException, PlaylistPreprocessException, DirectoryException
from music_dl.core.metadata import MetadataEditor
from music_dl.core.playlist import Playlist
from music_dl.core.youtube_dl import YDLHelper
from music_dl.lib.dir import is_path_exists_or_creatable
from music_dl.lib.log import logger


class MusicDL(object):
    """"""""""""""" Initializer """""""""""""""

    def __init__(self,
                 download_url,
                 working_dir=os.path.expanduser('~/Music/Downloads'),
                 audio_codec='m4a',
                 audio_bitrate=198,
                 playlist_start=1,
                 playlist_end=0,
                 no_artwork=False,
                 no_album_title=False,
                 no_album_artist=False,
                 no_track_number=False,
                 no_composer=False,
                 no_compilation=False,
                 open_dir=False,
                 verbose=False,
                 clear_cache=False,
                 test_id=None):
        # Download URL
        self.download_url = download_url
        # Working directory
        self.working_dir = working_dir
        # Open directory configuration
        self.open_dir = open_dir
        # Verbose
        self.verbose = verbose
        # Music Downloader
        self.playlist = Playlist(
            download_url=download_url,
            working_dir=working_dir,
            audio_codec=audio_codec,
            audio_bitrate=audio_bitrate,
            playlist_start=playlist_start,
            playlist_end=playlist_end,
            clear_cache=clear_cache,
            verbose=verbose,
            test_id=test_id,
        )
        self.metadata_editor = MetadataEditor(
            audio_codec=audio_codec,
            no_artwork=no_artwork,
            no_album_title=no_album_title,
            no_album_artist=no_album_artist,
            no_track_number=no_track_number,
            no_composer=no_composer,
            no_compilation=no_compilation,
            verbose=verbose
        )
        # Youtube Downloader
        self.ydl = YoutubeDL()
        self.ydl_helper = YDLHelper()

    """"""""""""""" Download Music (Public) """""""""""""""

    def download(self):
        """
        The function that downloads songs from YouTube and SoundCloud

        :return bool result: Result of process, used by unit test
        """
        print()
        atexit.register(print)

        """ Set log level """

        if self.verbose:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        """ Print version """

        logger.info(pkg_resources.require("music_dl")[0])

        """ Validate parameters """

        logger.info('Validating parameters...')

        try:
            # Validate download url
            url_parsed = urlparse(self.download_url)
            if not url_parsed.scheme.startswith('http'):
                raise DirectoryException('Invalid URL. URL must start with http*. Input value is {}'.format(self.download_url))
            tld_parsed = tldextract.extract(self.download_url)
            if not (tld_parsed.domain in ['youtube', 'soundcloud']):
                raise DirectoryException('Invalid URL. Music Downloader supports only YouTube and SoundCloud. Input value is {}'.format(self.download_url))
            # Validate download directory
            if not is_path_exists_or_creatable(self.working_dir):
                raise DirectoryException('Invalid directory. Please specify valid download directory. Input value is {}'.format(self.working_dir))

        except DirectoryException as e:
            logger.error(e.message)
            logger.fatal('Aborted.')
            exit()

        # Validate playlist configuration
        try:
            self.playlist.validate()

        except PlaylistParameterException as e:
            logger.error(e.message)
            logger.fatal('Aborted.')
            exit()

        logger.info('Done.')

        """ Retrieve playlist """

        download_dir = None
        try:
            download_dir = self.playlist.preprocess(self.download_url, self.working_dir)

        except PlaylistPreprocessException as e:
            logger.error(e.message)
            logger.error(e.data)
            logger.fatal('Aborted.')
            exit()

        """ Download playlist """

        is_downloaded = False
        try:
            is_downloaded = self.playlist.download()

        except PlaylistPreprocessException as e:
            logger.error(e.message)
            logger.error(e.data)
            logger.fatal('Aborted.')
            exit()

        """ Update metadata """

        if is_downloaded:
            self.metadata_editor.update(
                download_dir=self.playlist.download_dir,
                pl_data=self.playlist.downloaded_playlist_data,
                is_playlist=self.playlist.is_playlist,
            )

        """ Cleanup download directory """

        self.playlist.cleanup()

        """ Print completion message """

        logger.info('All process has done.')
        logger.info('Now you can find downloaded songs at {}'.format(colorama.Fore.LIGHTCYAN_EX + download_dir))

        """ Open download directory """

        if self.open_dir and platform.system().lower() == 'darwin':
            subprocess.check_output(['open', download_dir], stderr=subprocess.STDOUT)

        return True
