class ApplicationError(Exception):
    """ Base level application error. """


class RefreshError(ApplicationError):
    """ Error IMDB content refresh"""


class FileRefreshError(RefreshError):
    """ Error refreshing IMDB content files"""


class DBRefreshErrror(RefreshError):
    """ Error refreshing application DB with IMDB content. """


class MissingConfigError(ApplicationError):
    """ Error raised when missing secret file"""
