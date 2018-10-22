# coding:utf-8


class YoutubeDownloadMusicException(Exception):
    """Raised when youtube-dl module throws an exception"""

    def __init__(self, message):
        self.msg = message


class DirectoryException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class PlaylistParameterException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class PlaylistPreprocessException(Exception):
    def __init__(self, message, data):
        super().__init__(message)
        self.message = message
        self.data = data


class PlaylistDownloadException(Exception):
    def __init__(self, message, data):
        super().__init__(message)
        self.message = message
        self.data = data


class InvalidDataException(Exception):
    def __init__(self, message, file):
        super().__init__(message)
        self.message = message
        self.file = file


class InvalidMimeTypeException(Exception):
    def __init__(self, message, mime_type):
        super().__init__(message)
        self.message = message + '({})'.format(mime_type)
        self.mime_type = mime_type
