#!/usr/bin/env python
# coding: utf-8

import glob
import json
import os
from pprint import pformat

from youtube_dl import YoutubeDL
from youtube_dl.utils import sanitize_filename

from music_dl.core.error import PlaylistParameterException, PlaylistPreprocessException, PlaylistDownloadException
from music_dl.core.youtube_dl import YDLQueueStatus, YDLHelper
from music_dl.lib.log import logger


class Playlist(object):
    """"""""""""""" Initialization """""""""""""""

    def __init__(self, download_url, working_dir, audio_codec='m4a', audio_bitrate=198, playlist_start=1, playlist_end=0, clear_cache=False, verbose=False, test_id=None):
        """
        Initializer

        :param str audio_codec: Preferred audio codec
        :param int audio_bitrate: Preferred audio bitrate
        :param int playlist_start: Index specifying playlist item to start at
        :param int playlist_end: Index specifying playlist item to end at
        :param bool clear_cache: Flag that indicates to delete json file before downloading
        :param bool verbose: Print verbose message
        :param str test_id: Test case identifier
        """

        # Playlist configuration
        self.download_url = download_url
        self.working_dir = working_dir
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate
        self.playlist_start = playlist_start
        self.playlist_end = playlist_end
        self.clear_cache = clear_cache
        self.verbose = verbose
        self.test_id = test_id

        # Path
        self.download_dir = None
        self.playlist_file = None  # Path to playlist file
        self.downloaded_playlist_file = None  # Path to playlist file contains downloaded songs

        # Playlist data
        self.playlist_data = None  # Playlist data
        self.downloaded_playlist_data = None  # Playlist data
        self.playlist_entry_total = 0  # Total count of entries on playlist
        self.playlist_data_map = {}  # OrderedDict that maps index and entry_id
        self.scheduled_queue_indices = []  # Queue indices to be downloaded
        self.is_playlist = False  # Flag specifies data is playlist

        # Youtube Downloader
        self.ydl = YoutubeDL()
        self.ydl_helper = YDLHelper()

    """"""""""""""" Property """""""""""""""

    @property
    def downloaded_songs_total(self):
        """
        :rtype int
        :return Number of songs downloaded
        """
        if self.downloaded_playlist_data is None:
            return 0
        else:
            return len(self.download_dir.get('entries', []))

    """"""""""""""" Validation """""""""""""""

    def validate(self):
        # Validate playlist start and end
        if self.playlist_start <= 0:
            raise PlaylistParameterException('Invalid start index. Value must be greater than or equal to 1.')

        if 0 < self.playlist_end < self.playlist_start:
            raise PlaylistParameterException('Invalid start and end index. End index must be greater than or equal to start index.')

        # Validate audio codec
        if not (self.audio_codec in ['m4a', 'mp3', 'flac']):
            raise PlaylistParameterException('Supported audio format is m4a, mp3, and flac for now.')

        # Validate audio bit rate
        if self.audio_bitrate < 0:
            raise PlaylistParameterException('Audio bitrate must be positive integer.')

    """"""""""""""" Preprocess """""""""""""""

    def preprocess(self, download_url, working_dir):
        """
        :param str download_url: URL to download
        :param str working_dir: Path to root directory
        """

        self.download_url = download_url

        """ Retrieve playlist """

        logger.info('Retrieving playlist...')
        logger.info('Download URL: {}'.format(self.download_url))

        try:
            ydl_opts = self.ydl_helper.get_preprocess_option(
                download_url=self.download_url,
                audio_codec=self.audio_codec,
                audio_bitrate=self.audio_bitrate,
                playlist_start=self.playlist_start,
                playlist_end=self.playlist_end,
                verbose=self.verbose,
            )
            logger.debug(pformat(ydl_opts))
            self.ydl.__init__(params=ydl_opts)
            # TODO: What is extra_info? Need investigation.
            # self.playlist_data = self.ydl.extract_info(download_url, download=False, process=False, extra_info={})
            self.playlist_data = self.ydl.extract_info(self.download_url, download=False, process=False)

        except:
            raise PlaylistPreprocessException('Could not retrieve playlist.', None)

        if self.playlist_data is None or self.ydl is None:
            raise PlaylistPreprocessException('Could not retrieve playlist.', None)

        logger.info('Done.')

        """ Validate playlist """

        logger.info('Validating playlist...')

        # Determines playlist type
        playlist_extractor = self.playlist_data['extractor'].lower()
        if playlist_extractor == 'youtube:playlist' or playlist_extractor == 'soundcloud:set':
            self.is_playlist = True
            # Define download folder name
            if self.test_id is not None:
                download_folder = self.test_id
            else:
                playlist_title = sanitize_filename(self.playlist_data['title'])
                download_folder = '[{}] {}'.format(self.playlist_data['id'], playlist_title)
            self.download_dir = os.path.join(working_dir, download_folder)

        elif playlist_extractor == 'youtube' or playlist_extractor == 'soundcloud':
            self.is_playlist = False
            # Define download folder name
            if self.test_id is not None:
                download_folder = self.test_id
            else:
                download_folder = 'Single'
            self.download_dir = os.path.join(working_dir, download_folder)

        else:
            raise PlaylistPreprocessException('This playlist is not supported.', self.playlist_data)

        self.playlist_file = os.path.join(self.download_dir, '.queued.json')
        self.downloaded_playlist_file = os.path.join(self.download_dir, '.downloaded.json')

        logger.debug(pformat(self.playlist_data))
        logger.info('Done.')

        """ Create directories """

        logger.info('Creating download directory...')

        # Download directory
        os.makedirs(self.download_dir, exist_ok=True)

        # Playlist
        if self.clear_cache and os.path.exists(self.playlist_file):
            os.remove(self.playlist_file)
        if os.path.exists(self.downloaded_playlist_file):
            os.remove(self.downloaded_playlist_file)

        logger.info('Done.')

        """ Process playlist """

        logger.info('Processing playlist...')

        if self.is_playlist:
            # Convert generator object to list
            self.playlist_data['entries'] = list(self.playlist_data['entries'])
            self.playlist_entry_total = len(self.playlist_data['entries'])

            # Merge playlist
            merged_playlist_data, queue_indices = self.__merge_playlist(self.playlist_data)
            with open(self.playlist_file, 'w') as f:
                json.dump(merged_playlist_data, f, indent=4, ensure_ascii=False)
            self.playlist_data = merged_playlist_data
            self.scheduled_queue_indices = queue_indices

        logger.debug(pformat(self.playlist_data))
        logger.info('Done.')

        return self.download_dir

    """"""""""""""" Download """""""""""""""

    def download(self):
        """
        The function to download songs on the playlist

        :return str is_downloaded: Flag that indicates songs are downloaded
        """

        """ Generate youtube-dl option """

        logger.info('Generating youtube-dl option...')

        ydl_opts = None
        if self.is_playlist and len(self.scheduled_queue_indices) > 0:
            ydl_opts = self.ydl_helper.get_download_option(
                download_dir=self.download_dir,
                hook=self.__download_hook,
                audio_codec=self.audio_codec,
                audio_bitrate=self.audio_bitrate,
                queue_indices=self.scheduled_queue_indices,
                verbose=self.verbose
            )
            logger.debug(pformat(ydl_opts))

        elif not self.is_playlist:
            ydl_opts = self.ydl_helper.get_download_option(
                download_dir=self.download_dir,
                hook=self.__download_hook,
                audio_codec=self.audio_codec,
                audio_bitrate=self.audio_bitrate,
                verbose=self.verbose
            )
            logger.debug(pformat(ydl_opts))

        logger.info('Done.')

        """ Download songs """

        if ydl_opts:
            logger.info('Downloading songs...')

            try:
                # Download playlist
                self.ydl.__init__(params=ydl_opts)
                self.downloaded_playlist_data = self.ydl.extract_info(self.download_url, download=True)
                # Save playlist data
                with open(self.downloaded_playlist_file, 'w') as f:
                    json.dump(self.downloaded_playlist_data, f, indent=4, ensure_ascii=False)

            except Exception:
                raise PlaylistDownloadException('Failed to download playlist.', None)

            if self.downloaded_playlist_data is None:
                raise PlaylistDownloadException('Failed to download playlist.', None)

            logger.info('Done.')
            return True

        else:
            logger.warning('All songs on the playlist are already downloaded. There is nothing to process.')
            return False

    def __download_hook(self, data, queue_index=0, queue_total=0):
        """
        The function that get called on download progress, with a dictionary with the entries.
        More info is available at https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py

        :param dict data: Progress information for each queue
        :param int queue_index: Current queue index displayed in log message
        :param int queue_total: Total number of queue displayed in log message
        :return:

        :param dict data: Progress information for each queue
        """

        try:
            # Filename
            song_filename = os.path.basename(data['filename'])
            elapsed = "{0:.2f}".format(data.get('elapsed', -1))

            if queue_index > 0 and queue_total > 0:

                try:
                    # Get index from id-index map
                    song_id, song_ext = os.path.splitext(song_filename)
                    song_index = self.playlist_data_map.get(song_id, -1)
                    entry_found = None
                    if song_index >= 0:
                        # YouTube user playlist or SoundCloud playlist
                        entry_found = self.playlist_data['entries'][song_index]

                    else:
                        # YouTube auto-generated playlist
                        for entry in self.playlist_data['entries']:
                            if entry['id'] == song_id:
                                entry_found = entry
                                break

                    if entry_found:
                        # Finish queue
                        entry_found['status'] = YDLQueueStatus.finished.value
                        with open(self.playlist_file, 'w') as f:
                            json.dump(self.playlist_data, f, indent=4, ensure_ascii=False)

                        # Print song info
                        song_title = self.playlist_data['entries'][song_index].get('title', None)
                        song_title = '[title:{}]'.format(song_title) if song_title else ''
                        elapsed = '[Elapsed:{}]'.format(elapsed) if float(elapsed) >= 0 else ''
                        logger.info('[Process:{}/{}][ID:{}]{}[Size:{}]{} {}'.format(
                            queue_index, queue_total,
                            song_id, song_title, data['_total_bytes_str'], elapsed,
                            'Finished.'
                        ))

                    else:
                        # Print warning
                        song_title = self.playlist_data['entries'][song_index].get('title', None)
                        song_title = '[title:{}]'.format(song_title) if song_title else ''
                        elapsed = '[Elapsed:{}]'.format(elapsed) if float(elapsed) >= 0 else ''
                        logger.warning(
                            '[Process:{}/{}][ID:{}]{}[Size:{}]{} {}'.format(
                                queue_index, queue_total,
                                song_id, song_title, data['_total_bytes_str'], elapsed,
                                'The downloaded song is different from the song on the playlist initially requested. This is caused by YouTube auto-generated playlist.'
                            ))

                except Exception as e:
                    logger.error('[Process:{}/{}] {}:{}'.format(
                        queue_index, queue_total,
                        type(e), str(e),
                    ))

            else:
                song_title, song_ext = os.path.splitext(song_filename)
                elapsed = '[Elapsed:{}]'.format(elapsed) if float(elapsed) >= 0 else ''
                logger.info('[Title:{}][Size:{}]{} {}'.format(
                    song_title, data['_total_bytes_str'], elapsed,
                    'Finished.'
                ))

        except Exception as e:
            logger.error('[Process:{}/{}] {}:{}'.format(queue_index, queue_total, type(e), str(e)))

    def __merge_playlist(self, pl_data):
        """
        The function that merges remote (head_playlist) and local playlist (base_playlist) and generate scheduled queue indices

        :param dict pl_data: Playlist data contains downloaded songs

        :rtype: (dict, list)
        :return: (playlist, indices):  (Merged playlist, Queue indices to download)
        """

        head_playlist_data = pl_data  # Playlist data downloaded from url
        base_playlist_data = None  # Playlist data previously saved on download directory

        """ Load playlist previously saved """

        if os.path.exists(self.playlist_file):
            with open(self.playlist_file) as f:
                # base_playlist_data = json.load(f, object_pairs_hook=OrderedDict)
                base_playlist_data = json.load(f)

        """ Merge Playlist """

        candidate_queue_indices = []
        candidate_queue_index = 1

        # Playlist
        if base_playlist_data:
            # Copy list to avoid index shifting when elements are removed while iterating.
            # https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
            head_index = 0
            head_entries = head_playlist_data['entries'][:]
            for head_entry in head_entries:
                # Delete entry if invalid.
                if head_entry is None or head_entry.get('title', 'N/A').lower() in ['[private video]', '[deleted video]']:
                    song_title = head_entry.get('title', None)
                    song_title = '[title:{}]'.format(song_title) if song_title else ''
                    logger.error('[Playlist:{}/{}][ID:{}]{} {}'.format(
                        head_index + 1, len(head_playlist_data['entries']),
                        head_entry.get('id', 'N/A'), song_title,
                        'The video is private or deleted. Removed from the playlist.'
                    ))
                    del head_playlist_data['entries'][head_index]
                    candidate_queue_index += 1

                else:
                    # Copy list to avoid index shifting when elements are removed while iterating.
                    # https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
                    base_index = 0
                    base_entries = base_playlist_data['entries'][:]
                    for base_entry in base_entries:

                        # Delete entry if invalid.
                        if base_entry is None or base_entry.get('title', 'N/A').lower() in ['[private video]', '[deleted video]']:
                            song_title = base_entry.get('title', None)
                            song_title = '[title:{}]'.format(song_title) if song_title else ''
                            logger.error('[Playlist:{}/{}][ID:{}]{} {}'.format(
                                head_index + 1, len(head_playlist_data['entries']),
                                base_entry.get('id', 'N/A'), song_title,
                                'The video is private or deleted. Removed from the playlist.',
                            ))
                            del base_playlist_data['entries'][base_index]

                        else:
                            # If same entry is found, update status
                            if head_entry['id'] == base_entry['id']:

                                # Merge base status into head status
                                base_entry_status = base_entry.get('status', YDLQueueStatus.ready.value)
                                head_playlist_data['entries'][head_index]['status'] = base_entry_status

                                # Queue index is out of range requested
                                if not self.__is_queue_in_range(head_index):
                                    song_title = base_entry.get('title', None)
                                    song_title = '[title:{}]'.format(song_title) if song_title else ''
                                    logger.debug('[Playlist:{}/{}][ID:{}]{} {}'.format(
                                        head_index + 1, len(head_playlist_data['entries']),
                                        base_entry.get('id', 'N/A'), song_title,
                                        'This queue is out of range requested. Skipped.',
                                    ))

                                # Song is already downloaded
                                elif base_entry_status == YDLQueueStatus.finished.value:
                                    song_title = base_entry.get('title', None)
                                    song_title = '[title:{}]'.format(song_title) if song_title else ''
                                    logger.warning('[Playlist:{}/{}][ID:{}]{} {}'.format(
                                        head_index + 1, len(head_playlist_data['entries']),
                                        base_entry.get('id', 'N/A'), song_title,
                                        'This queue is already finished. Skipped.',
                                    ))

                                # Song is not downloaded yet
                                else:
                                    song_title = base_entry.get('title', None)
                                    song_title = '[title:{}]'.format(song_title) if song_title else ''
                                    logger.info('[Playlist:{}/{}][ID:{}]{} {}'.format(
                                        head_index + 1, len(head_playlist_data['entries']),
                                        base_entry.get('id', 'N/A'), song_title,
                                        'This queue is not finished yet. Added to scheduled queues.',
                                    ))

                                # Delete entry to make iteration faster
                                del base_playlist_data['entries'][base_index]
                                break

                            base_index += 1

                    # Update track number
                    head_entry['track_number'] = head_index + 1

                    # Add queue
                    is_not_finished = head_entry.get('status', YDLQueueStatus.ready.value) != YDLQueueStatus.finished.value
                    if self.__is_queue_in_range(head_index) and is_not_finished:
                        candidate_queue_indices.append(candidate_queue_index)

                    # Add element to dictionary that maps index and entry_id
                    self.playlist_data_map[head_entry['id']] = head_index

                    candidate_queue_index += 1
                    head_index += 1

        # Single song
        else:
            # Copy list to avoid index shifting when elements are removed while iterating.
            # https://stackoverflow.com/questions/1207406/how-to-remove-items-from-a-list-while-iterating
            head_index = 0
            head_entries = head_playlist_data['entries'][:]
            for head_entry in head_entries:
                # Delete entry if invalid.
                if head_entry is None or head_entry.get('title', 'N/A').lower() in ['[private video]', '[deleted video]']:
                    song_title = head_entry.get('title', None)
                    song_title = '[title:{}]'.format(song_title) if song_title else ''
                    logger.error('[Playlist:{}/{}][ID:{}]{} {}'.format(
                        head_index + 1, len(head_playlist_data['entries']),
                        head_entry.get('id', 'N/A'), song_title,
                        'The video is private or deleted. Removed from the playlist.'
                    ))
                    del head_playlist_data['entries'][head_index]
                    candidate_queue_index += 1

                else:
                    song_title = head_entry.get('title', None)
                    song_title = '[title:{}]'.format(song_title) if song_title else ''

                    # Add queue
                    if self.__is_queue_in_range(head_index):
                        candidate_queue_indices.append(candidate_queue_index)
                        logger.info('[Playlist:{}/{}][ID:{}]{} {}'.format(
                            head_index + 1, len(head_playlist_data['entries']),
                            head_entry.get('id', 'N/A'), song_title,
                            'This queue is not finished yet. Added to scheduled queues.'
                        ))
                    else:
                        logger.debug('[Playlist:{}/{}][ID:{}]{} {}'.format(
                            head_index + 1, len(head_playlist_data['entries']),
                            head_entry.get('id', 'N/A'), song_title,
                            'This queue is out of range requested. Skipped.'
                        ))

                    # Update value
                    head_entry['status'] = YDLQueueStatus.ready.value

                    # Update track number
                    head_entry['track_number'] = head_index + 1

                    # Add element to dictionary that maps index and entry_id
                    self.playlist_data_map[head_entry['id']] = head_index

                    candidate_queue_index += 1
                    head_index += 1

        # Save playlist
        with open(self.playlist_file, 'w') as file:
            json.dump(head_playlist_data, file, indent=4, ensure_ascii=False)

        self.playlist_data = head_playlist_data

        return head_playlist_data, candidate_queue_indices

    def __is_queue_in_range(self, index):
        is_greater_than_start = self.playlist_end <= 0 and self.playlist_start <= index + 1
        is_between_start_and_end = self.playlist_start <= index + 1 <= self.playlist_end
        return is_greater_than_start or is_between_start_and_end

    """"""""""""""" Cleanup """""""""""""""

    def cleanup(self):
        """
        The function that deletes all zero byte files from download directory.
        """

        """ Remove zero bytes files created by youtube-dl """

        logger.info('Deleting zero byte files...')
        if not os.path.isdir(self.download_dir):
            raise ValueError('Parameter path is not a directory.')
        files = glob.glob(self.download_dir + '/*')

        # Create generator to find and remove zero byte files
        generator = (os.remove(f) for f in files if os.path.isfile(f) and os.path.getsize(f) == 0)

        try:
            while True:
                next(generator)
        except StopIteration:
            logger.info('Done.')
            return
        except Exception as e:
            logger.error('{}: {}'.format(type(e), e))
