#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import os
import shutil
import sys
import unittest

from music_dl.MusicDL import MusicDL


class TestMusicDL(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMusicDL, self).__init__(*args, **kwargs)
        self.verbose = False
        self.open_dir = False
        self.download_dir = os.path.join(os.getcwd(), 'Downloads')

    def setUp(self):
        # if os.path.exists(self.download_dir):
        #     shutil.rmtree(self.download_dir)
        pass

    def tearDown(self):
        pass

    def test_youtube_playlist_random_generated(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        """ YouTube Mix always returns playlists generated randomly. """
        mdl = MusicDL(
            download_url='https://www.youtube.com/watch?v=L2aUMxR2tUo&list=RDL2aUMxR2tUo',
            working_dir=self.download_dir,
            playlist_start=10,
            playlist_end=20,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_youtube_playlist_contains_private(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://www.youtube.com/watch?v=JNzxRt-7opc&list=PLpzbRhaAcBDUXr4f443rbWt0SX5B7NPzh',
            working_dir=self.download_dir,
            playlist_start=10,
            playlist_end=12,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_youtube_playlist_contains_deleted(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://www.youtube.com/watch?v=qeMFqkcPYcg&list=PLvEomy2ZUOYhd4Uk0lgSfMz6LTK4fKAzX',
            working_dir=self.download_dir,
            audio_codec='m4a',
            playlist_start=8,
            playlist_end=12,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_youtube_single(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://www.youtube.com/watch?v=JNzxRt-7opc',
            working_dir=self.download_dir,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_soundcloud_playlist(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://soundcloud.com/futureclassic/sets/teen-idols-a-future-classic-1',
            working_dir=self.download_dir,
            playlist_start=1,
            playlist_end=4,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_soundcloud_single(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://soundcloud.com/futureclassic/touch-sensitive-teen-idols-1',
            working_dir=self.download_dir,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_youtube_playlist_mp3(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://www.youtube.com/watch?v=p9j8RGTqju0&list=PLEFicgYw8GpTBfs-r72joXydKhohoHhMM',
            working_dir=self.download_dir,
            audio_codec='mp3',
            playlist_start=1,
            playlist_end=2,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_youtube_playlist_flac(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://www.youtube.com/watch?v=DpMfP6qUSBo&list=PLSuv_rN0oCUl70G7XgeA2wLvKqTPflggN',
            working_dir=self.download_dir,
            audio_codec='flac',
            playlist_start=1,
            playlist_end=2,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_soundcloud_playlist_mp3(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://soundcloud.com/aeroeau/sets/gilles-p',
            working_dir=self.download_dir,
            audio_codec='mp3',
            playlist_start=3,
            playlist_end=4,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())

    def test_soundcloud_playlist_flac(self):
        print('\n')
        print('======================================================================')
        print(self.id())
        print('======================================================================')
        mdl = MusicDL(
            download_url='https://soundcloud.com/joris-besnart-716425874/sets/11-12-17',
            working_dir=self.download_dir,
            audio_codec='mp3',
            playlist_start=1,
            playlist_end=2,
            verbose=self.verbose,
            # open_dir=self.open_dir,
            test_id=sys._getframe().f_code.co_name,
        )
        self.assertTrue(True, mdl.download())


if __name__ == '__main__':
    unittest.main()
