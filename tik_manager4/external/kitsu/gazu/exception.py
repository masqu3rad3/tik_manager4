class HostException(Exception):
    """
    Error raised when host is not valid.
    """


class AuthFailedException(Exception):
    """
    Error raised when user credentials are wrong.
    """


class NotAuthenticatedException(Exception):
    """
    Error raised when a 401 error (not authenticated) is sent by the API.
    """


class NotAllowedException(Exception):
    """
    Error raised when a 403 error (not authorized) is sent by the API.
    """


class MethodNotAllowedException(Exception):
    """
    Error raised when a 405 error (method not handled) is sent by the API.
    """


class RouteNotFoundException(Exception):
    """
    Error raised when a 404 error (not found) is sent by the API.
    """


class ServerErrorException(Exception):
    """
    Error raised when a 500 error (server error) is sent by the API.
    """


class ParameterException(Exception):
    """
    Error raised when a 400 error (argument error) is sent by the API.
    """


class UploadFailedException(Exception):
    """
    Error raised when an error while uploading a file, mainly to handle cases
    where processing that occurs on the remote server fails.
    """


class TooBigFileException(Exception):
    """
    Error raised when a 413 error (payload too big error) is sent by the API.
    """


class TaskStatusNotFoundException(Exception):
    """
    Error raised when a task status is not found.
    """


class DownloadFileException(Exception):
    """
    Error raised when a file can't be downloaded.
    """


class TaskMustBeADictException(Exception):
    """
    Error raised when a task should be a dict.
    """


class FileDoesntExistException(Exception):
    """
    Error raised when a file should be existed when we submit a preview.
    """


class ProjectDoesntExistException(Exception):
    """
    Error raised when a project isn't available.
    """
