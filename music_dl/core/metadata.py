#!/usr/bin/env python
# coding: utf-8

import errno
import mimetypes
import os

from mutagen import mp4, id3, flac, File
from youtube_dl.utils import sanitize_filename

from music_dl.core.error import InvalidMimeTypeException, InvalidDataException
from music_dl.lib.log import logger
from music_dl.lib.util import contains_at_least


class MetadataEditor(object):
    """"""""""""""" Initialization """""""""""""""

    def __init__(self, audio_codec, no_artwork, no_album_title, no_album_artist, no_track_number, no_composer, no_compilation, verbose):
        """
        Initializer

        :param str audio_codec: Preferred audio codec
        :param bool no_artwork: Forbid adding artwork to audio metadata
        :param bool no_album_title: Forbid adding track number to audio metadata
        :param bool no_album_artist: Forbid adding album title to audio metadata
        :param bool no_track_number: Forbid adding album artist to audio metadata
        :param bool no_composer: Forbid adding composer to audio metadata
        :param bool no_compilation: Forbid adding part of compilation flag to audio metadata
        :param bool verbose: Print verbose message
        """

        self.audio_codec = audio_codec
        self.no_artwork = no_artwork
        self.no_album_title = no_album_title
        self.no_album_artist = no_album_artist
        self.no_track_number = no_track_number
        self.no_composer = no_composer
        self.no_compilation = no_compilation
        self.verbose = verbose

    """"""""""""""" Update metadata """""""""""""""

    def update(self, download_dir, pl_data, is_playlist):
        """
        The function that update audio metadata.

        :param str download_dir: Download directory
        :param dict pl_data: Playlist data which contains downloaded song information
        :param bool is_playlist: Flag that indicates playlist contains multiple songs
        """

        logger.info('Updating metadata...')

        if is_playlist:
            entries = pl_data.get('entries', [])
            album_title = pl_data.get('title', 'Unknown Album')
            album_artist = pl_data.get('uploader', None)
            album_composer = pl_data.get('extractor_key')

            process_index = 1
            process_total = len(entries)
            for entry in entries:
                try:
                    # Determine filename from entry id
                    song_id = entry['id']
                    # song_index = self.playlist_data_map.get(song_id, -1)

                    song_track_number = process_index
                    song_title = sanitize_filename(entry.get('title', song_id))
                    source_audio_file = os.path.join(download_dir, '{}.{}'.format(song_id, self.audio_codec))

                    # Artwork
                    image_file = None
                    try:
                        image_file = entry['thumbnails'][0]['filename']
                    except:
                        pass

                    # Update tag
                    self.__update_tag(
                        download_dir=download_dir,
                        song_title=song_title,
                        audio_file=source_audio_file,
                        image_file=image_file,
                        album_title=album_title,
                        album_artist=album_artist,
                        album_composer=album_composer,
                        track_number=song_track_number,
                        process_index=process_index,
                        process_total=process_total,
                    )

                except:
                    message = 'Could not update metadata because there is no data found on the playlist. The video may be private or deleted. Audio data is not saved.'
                    logger.error('[Process:{}/{}][Track:{}] {}'.format(process_index, process_total, 'N/A', message))

                process_index += 1

        else:
            base_filename = sanitize_filename(pl_data.get('title', 'Unknown'))
            audio_file = os.path.join(download_dir, '{}.{}'.format(base_filename, self.audio_codec))
            if os.path.exists(audio_file):
                image_file = None
                try:
                    image_file = pl_data['thumbnails'][0]['filename']
                except:
                    pass
                self.__update_tag(
                    download_dir=download_dir,
                    audio_file=audio_file,
                    image_file=image_file
                )

        logger.info('Done.')

    def __update_tag(self, download_dir, audio_file, image_file,
                     song_title=None, album_title=None, album_artist=None, album_composer=None,
                     track_number=-1, process_index=-1, process_total=-1):
        """
        The function that update audio metadata for each song.

        :param str download_dir: Download directory
        :param str audio_file: Path to audio file
        :param str image_file: Path to image file
        :param str song_title: Song title
        :param str album_title: Album title to be saved in metadata
        :param str album_artist: Album artist to be saved in metadata
        :param str album_composer: Album composer to be saved in metadata
        :param int track_number: track number to be saved in metadata
        :param int process_index: Current process index displayed in log message
        :param int process_total: Total number of process displayed in log message
        """

        if audio_file is None:
            logger.warning('[Process:{}/{}][Track:{}] Could not update metadata because there is no data found on the playlist. The video may be private or deleted.'.format(process_index, process_total, track_number))
            return

        if process_index > 0 and process_total > 0:

            if track_number > 0:
                log_prefix = '[Process:{}/{}][Track:{}]'.format(process_index, process_total, track_number)

            else:
                log_prefix = '[Process:{}/{}]'.format(process_index, process_total)

        else:
            log_prefix = ''

        audio_filename = os.path.basename(audio_file)

        try:
            # Validate audio data
            if not os.path.isfile(audio_file):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), audio_file)

            audio_mime_type = mimetypes.guess_type(audio_file)

            if contains_at_least(audio_mime_type, ['audio/x-mp4', 'audio/x-m4a', 'audio/mp4a-latm']):

                # For more info about mp4 tag is available at
                # https://github.com/quodlibet/mutagen/blob/cf399dc58940fb1356f672809d763be9e2af0033/mutagen/mp4/__init__.py
                # http://atomicparsley.sourceforge.net/mpeg-4files.html
                mp4_data = mp4.MP4(audio_file)
                # Track Number
                if not self.no_track_number and track_number > 0:
                    mp4_data['trkn'] = [(track_number, 0)]
                # Cover image
                if not self.no_artwork:
                    image_data = self.__get_tag_image(image_file, audio_mime_type)
                    if image_data:
                        mp4_data['covr'] = [image_data]
                # Album title
                if not self.no_album_title and album_title is not None:
                    mp4_data['\xa9alb'] = album_title
                # Album artist
                if not self.no_album_artist and album_artist is not None:
                    mp4_data['aART'] = album_artist
                # Composer
                if not self.no_composer and album_composer is not None:
                    mp4_data['\xa9wrt'] = album_composer
                # Part of compilation
                if not self.no_compilation:
                    mp4_data['cpil'] = True
                # Save
                mp4_data.save()

            elif contains_at_least(audio_mime_type, ['audio/x-mp3', 'audio/mpeg']):

                # For more info about ID3v2 tag is available at
                # https://github.com/quodlibet/mutagen/blob/4a5d7d17f1a611280cc52d229aa70b77ca3c55dd/mutagen/id3/_frames.py
                # https://help.mp3tag.de/main_tags.html
                mp3_data = id3.ID3(audio_file)
                # Cover image
                if not self.no_artwork:
                    image_data = self.__get_tag_image(image_file, audio_mime_type)
                    if image_data:
                        mp3_data['APIC'] = image_data
                # Track number
                if not self.no_track_number and track_number > 0:
                    mp3_data.add(id3.TRCK(encoding=3, text=['{}/{}'.format(track_number, 0)]))
                # Album title
                if not self.no_album_title and album_title is not None:
                    mp3_data["TALB"] = id3.TALB(encoding=0, text=album_title)
                # Album artist
                if not self.no_album_artist and album_artist is not None:
                    mp3_data["TPE2"] = id3.TPE2(encoding=0, text=album_artist)
                # Composer
                if not self.no_composer and album_composer is not None:
                    mp3_data["TCOM"] = id3.TCOM(encoding=0, text=album_composer)
                # Part of compilation
                if not self.no_compilation:
                    mp3_data['TCMP'] = id3.TCMP(encoding=0, text=['1'])
                # Save
                mp3_data.save()

            elif contains_at_least(audio_mime_type, ['audio/x-aac']):

                # TODO: Add AAC support
                pass
                # image_data = __get_tag_image(image_file, audio_mime_type)
                # aac_data = aac.AAC(audio_file)
                # if not self.no_track_number:
                #     if track_number > 0 and track_total > 0:
                #         aac_data.add_tags(id3.TRCK(encoding=3, text=['{}/{}'.format(track_number, track_total)]))
                #         # mp3_data['TRCK'] = id3.TRCK(encoding=3, text=[str(track_number)])
                # if image_data:
                #     mp3_data['APIC'] = image_data
                #     aac_data.save()

            elif contains_at_least(audio_mime_type, ['audio/x-flac']):

                # https://github.com/quodlibet/mutagen/blob/a1db79ece62c4e86259f15825e360d1ce0986a22/mutagen/flac.py
                # https://github.com/quodlibet/mutagen/blob/4a5d7d17f1a611280cc52d229aa70b77ca3c55dd/tests/test_flac.py

                flac_data = flac.FLAC(audio_file)
                # Artwork
                if not self.no_artwork:
                    image_data = self.__get_tag_image(image_file, audio_mime_type)
                    if image_data:
                        flac_data.add_picture(image_data)
                # Save
                flac_data.save()

                flac_data = File(audio_file)
                # Track number
                if not self.no_track_number and track_number > 0:
                    flac_data.tags['tracknumber'] = str(track_number)
                # Album title
                if not self.no_album_title and album_title is not None:
                    flac_data.tags['album'] = album_title
                # Album artist
                if not self.no_album_artist and album_artist is not None:
                    flac_data.tags['albumartist'] = album_artist
                # Composer
                if not self.no_composer and album_composer is not None:
                    flac_data.tags['composer'] = album_composer
                # Part of compilation
                if not self.no_compilation:
                    pass
                # Save
                flac_data.save()
                # audio = File(audio_file, easy=True)

            else:
                raise InvalidMimeTypeException("Invalid audio format.", audio_mime_type)

            # Remove artwork if succeeded
            if os.path.exists(image_file):
                os.remove(image_file)

            # Rename filename from id to title
            dest_audio_file = os.path.join(download_dir, '{}.{}'.format(song_title, self.audio_codec))
            os.rename(audio_file, dest_audio_file)

            dest_audio_filename = os.path.basename(dest_audio_file)
            logger.info('{}[File:{}] Updated.'.format(log_prefix, dest_audio_filename))

        except FileNotFoundError:
            message = 'File not found. Skipped.'
            logger.warning('{}[File:{}] {}'.format(log_prefix, audio_filename, message))

        except InvalidDataException as e:
            message = e.message + ' Skipped.'
            logger.warning('{}[File:{}] {}'.format(log_prefix, audio_filename, message))

        except InvalidMimeTypeException as e:
            message = e.message + ' Skipped.'
            logger.warning('{}[File:{}] {}'.format(log_prefix, audio_filename, message))

        except Exception as e:
            message = 'Error {}: {} Skipped.'.format(type(e), str(e))
            logger.error('{}[File:{}] {}'.format(log_prefix, audio_filename, message))

    def __get_tag_image(self, image_file, audio_mime_type):
        """
        The function that returns cover image.

        :param str image_file: Path to image file
        :param list audio_mime_type: Mime-Types of image file
        :return binary image_data: Binary data of image file
        """
        if not os.path.isfile(image_file):
            return

        # Create image
        with open(image_file, 'rb') as f:
            image_data = f.read()
        if image_data is None:
            raise InvalidDataException("Could not create image data.", image_file)

        image_mime_type = mimetypes.guess_type(image_file)[0]

        if contains_at_least(audio_mime_type, ['audio/x-mp4', 'audio/x-m4a', 'audio/mp4a-latm']):

            if image_mime_type == "image/jpeg":
                image_format = mp4.MP4Cover.FORMAT_JPEG
            elif image_mime_type == "image/png":
                image_format = mp4.MP4Cover.FORMAT_PNG
            else:
                raise InvalidMimeTypeException("Invalid image format.", image_mime_type)

            return mp4.MP4Cover(image_data, image_format)

        elif contains_at_least(audio_mime_type, ['audio/x-mp3', 'audio/mpeg']):

            if not image_mime_type == "image/jpeg" and not image_mime_type == "image/png":
                raise InvalidMimeTypeException("Invalid image format.", image_mime_type)

            return id3.APIC(encoding=3, mime=image_mime_type, type=3, desc='Cover', data=image_data)

        elif contains_at_least(audio_mime_type, ['audio/x-aac']):

            # TODO: Add aac support
            pass
            # if not image_mime_type == "image/jpeg" and not image_mime_type == "image/png":
            #     raise InvalidMimeTypeException("Invalid image format.", image_mime_type)
            #
            # picture = flac.Picture()
            # picture.type = 3
            # picture.desc = 'front cover'
            # picture.data = image_data
            #
            # return picture

        elif contains_at_least(audio_mime_type, ['audio/x-flac']):

            if not image_mime_type == "image/jpeg" and not image_mime_type == "image/png":
                raise InvalidMimeTypeException("Invalid image format.", image_mime_type)

            picture = flac.Picture()
            picture.type = 3
            picture.desc = 'front cover'
            picture.data = image_data

            return picture

        else:
            raise InvalidMimeTypeException("Invalid audio format.", audio_mime_type)
