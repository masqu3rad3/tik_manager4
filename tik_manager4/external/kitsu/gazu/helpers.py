import sys
import os
import re
import datetime
import shutil
import requests
import tempfile
import mimetypes

from gazu.exception import DownloadFileException

if sys.version_info[0] == 3:
    import urllib.parse as urlparse
else:
    import urlparse

_UUID_RE = re.compile(
    "([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}){1}"
)


def normalize_model_parameter(model_parameter):
    """
    Args:
        model_parameter (str / dict): The parameter to convert.

    Returns:
        dict: If `model_parameter` is an ID (a string), it turns it into a model
        dict. If it's already a dict, the `model_parameter` is returned as it
        is. It returns None if the paramater is None.
    """
    if model_parameter is None:
        return None
    elif isinstance(model_parameter, dict):
        return model_parameter
    else:
        try:
            id_str = str(model_parameter)
        except Exception:
            raise ValueError("Failed to cast argument to str")

        if _UUID_RE.match(id_str):
            return {"id": id_str}
        else:
            raise ValueError("Wrong format: expected ID string or Data dict")


def normalize_list_of_models_for_links(models=[]):
    """
    Args:
        models (list): The models to convert.

    Returns:
        list: A list of ids of the models.
    """
    if not isinstance(models, list):
        models = [models]

    return [normalize_model_parameter(model)["id"] for model in models]


def validate_date_format(date_text):
    try:
        datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            datetime.datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                "Incorrect date format for %s, should be YYYY-mm-dd or YYYY-mm-ddTHH:MM:SS"
                % date_text
            )
    return date_text


def sanitize_filename(filename):
    forbidden = "@|():%/,\\[]<>*?;`\n"
    return "".join(
        [c for c in filename.replace("..", "_") if c not in forbidden]
    ).strip()


def download_file(url, file_path=None, headers={}):
    """
    Download file located at *file_path* to given url *url*.

    Args:
        url (str): The url path to download file from.
        file_path (str): The location to store the file on the hard drive.
        headers (dict): The headers to pass to requests

    Returns:
        str: The location where the file is stored.

    """
    with requests.get(
        url,
        headers=headers,
        stream=True,
    ) as response:
        if response.ok:
            if file_path is None:
                file_path = tempfile.gettempdir()

            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, "")

            (dir, filename) = os.path.split(file_path)

            if not filename:
                url_parts = urlparse.urlparse(url)
                filename = url_parts.path.split("/")[-1]
            if not dir:
                dir = os.getcwd()

            name, ext = os.path.splitext(filename)

            if ext == "":
                if "Content-Type" in response.headers:
                    guessed_ext = mimetypes.guess_extension(
                        response.headers["Content-Type"]
                    )
                    if guessed_ext is not None:
                        ext = guessed_ext

            if name == "":
                name = "file"

            filename = sanitize_filename(name + ext)

            file_path = os.path.join(dir, filename)

            with open(file_path, "wb") as target_file:
                shutil.copyfileobj(response.raw, target_file)
            return file_path
        else:
            raise DownloadFileException(
                "File (%s) can't be downloaded (%i %s)."
                % (url, response.status_code, response.reason)
            )
