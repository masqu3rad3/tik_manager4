import sys
import functools
import json
import shutil
import os

from .encoder import CustomJSONEncoder

from .__version__ import __version__

from .exception import (
    TooBigFileException,
    NotAuthenticatedException,
    NotAllowedException,
    MethodNotAllowedException,
    ParameterException,
    RouteNotFoundException,
    ServerErrorException,
    UploadFailedException,
)


if sys.version_info[0] == 3:
    from json import JSONDecodeError
    from urllib.parse import urlencode
else:
    JSONDecodeError = ValueError
    from urllib import urlencode

DEBUG = os.getenv("GAZU_DEBUG", "false").lower() == "true"


class KitsuClient(object):
    def __init__(
        self,
        host,
        ssl_verify=True,
        cert=None,
        use_refresh_token=True,
        callback_not_authenticated=None,
        tokens={"access_token": None, "refresh_token": None},
        access_token=None,
        refresh_token=None,
    ):
        self.tokens = tokens
        if access_token:
            self.access_token = access_token
        if refresh_token:
            self.refresh_token = refresh_token
        self.use_refresh_token = use_refresh_token
        self.callback_not_authenticated = callback_not_authenticated

        self.session = requests.Session()
        self.session.verify = ssl_verify
        self.session.cert = cert
        self.host = host
        self.event_host = host

    @property
    def access_token(self):
        return self.tokens.get("access_token", None)

    @access_token.setter
    def access_token(self, token):
        self.tokens["access_token"] = token

    @property
    def refresh_token(self):
        return self.tokens.get("refresh_token", None)

    @refresh_token.setter
    def refresh_token(self, token):
        self.tokens["refresh_token"] = token

    def refresh_access_token(self):
        """
        Refresh access tokens for this client.

        Returns:
            dict: The new access token.
        """
        response = self.session.get(
            get_full_url("auth/refresh-token", client=self),
            headers={
                "User-Agent": "CGWire Gazu " + __version__,
                "Authorization": "Bearer " + self.refresh_token,
            },
        )
        check_status(response, "auth/refresh-token")
        tokens = response.json()

        self.access_token = tokens["access_token"]
        self.refresh_token = None

        return tokens

    def make_auth_header(self):
        """
        Make headers required to authenticate.

        Returns:
            dict: Headers required to authenticate.
        """
        headers = {"User-Agent": "CGWire Gazu " + __version__}

        if self.access_token:
            headers["Authorization"] = "Bearer " + self.access_token

        return headers


def create_client(
    host,
    ssl_verify=True,
    cert=None,
    use_refresh_token=False,
    callback_not_authenticated=None,
    **kwargs
):
    """
    Create a client with given parameters.

    Args:
        host (str): The host to use for requests.
        ssl_verify (bool): Whether to verify SSL certificates.
        cert (str): Path to a client certificate.
        use_refresh_token (bool): Whether to automatically refresh tokens.
        callback_not_authenticated (function): Function to call when not authenticated.

    Returns:
        KitsuClient: The created client.
    """
    return KitsuClient(
        host,
        ssl_verify,
        cert=cert,
        use_refresh_token=use_refresh_token,
        callback_not_authenticated=callback_not_authenticated,
        **kwargs
    )


default_client = None
try:
    import requests

    # Little hack to allow json encoder to manage dates.
    requests.models.complexjson.dumps = functools.partial(
        json.dumps, cls=CustomJSONEncoder
    )
    host = "http://gazu.change.serverhost/api"
    default_client = create_client(host)
except Exception:
    print("Warning, running in setup mode!")


def host_is_up(client=default_client):
    """
    Check if the host is up.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        bool: True if the host is up.
    """
    try:
        response = client.session.head(client.host)
    except Exception:
        return False
    return response.status_code == 200


def host_is_valid(client=default_client):
    """
    Check if the host is valid by simulating a fake login.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        bool: True if the host is valid.
    """
    if not host_is_up(client):
        return False
    try:
        post("auth/login", {"email": ""})
    except Exception as exc:
        return isinstance(exc, (NotAuthenticatedException, ParameterException))


def get_host(client=default_client):
    """
    Get client.host.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The host of the client.
    """
    return client.host


def get_api_url_from_host(client=default_client):
    """
    Get the API url from the host.

    Args:
        client (KitsuClient): The client to use for the request.
    Returns:
        Zou url, retrieved from host.
    """
    return client.host[:-4]


def set_host(new_host, client=default_client):
    """
    Set the host for the client.

    Args:
        new_host (str): The new host to set.
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The new host.
    """
    client.host = new_host
    return client.host


def get_event_host(client=default_client):
    """
    Get the host on which listening for events.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The event host.
    """
    return client.event_host or client.host


def set_event_host(new_host, client=default_client):
    """
    Set the host on which listening for events.

    Args:
        new_host (str): The new host to set.
        client (KitsuClient): The client to use for the request.

    Returns:
        str: The new event host.
    """
    client.event_host = new_host
    return client.event_host


def set_tokens(new_tokens, client=default_client):
    """
    Store authentication token to reuse them for all requests.

    Args:
        new_tokens (dict): Tokens to use for authentication.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The stored tokens.
    """
    client.tokens = new_tokens
    return client.tokens


def make_auth_header(client=default_client):
    """
    Make headers required to authenticate.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: Headers required to authenticate.
    """
    return client.make_auth_header()


def url_path_join(*items):
    """
    Make it easier to build url path by joining every arguments with a '/'
    character.

    Args:
        items (list): Path elements

    Returns:
        str: The joined path.
    """
    return "/".join([item.lstrip("/").rstrip("/") for item in items])


def get_full_url(path, client=default_client):
    """
    Join host url with given path.

    Args:
        path (str): The path to integrate to host url.

    Returns:
        The result of joining configured host url with given path.
    """
    return url_path_join(get_host(client), path)


def build_path_with_params(path, params):
    """
    Add params to a path using urllib encoding.

    Args:
        path (str): The url base path
        params (dict): The parameters to add as a dict

    Returns:
        str: the builded path
    """
    if not params:
        return path

    query_string = urlencode(params)

    if query_string:
        # Support base paths that already contain query parameters.
        path += "&" if "?" in path else "?"
        path += query_string

    return path


def get(path, json_response=True, params=None, client=default_client):
    """
    Run a get request toward given path for configured host.

    Args:
        path (str): The path to query.
        json_response (bool): Whether to return a json response.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    if DEBUG:
        print("GET", get_full_url(path, client))
    path = build_path_with_params(path, params)
    retry = True
    while retry:
        response = client.session.get(
            get_full_url(path, client=client),
            headers=make_auth_header(client=client),
        )
        _, retry = check_status(response, path, client=client)

    if json_response:
        return response.json()
    else:
        return response.text


def post(path, data, client=default_client):
    """
    Run a post request toward given path for configured host.

    Args:
        path (str): The path to query.
        data (dict): The data to post.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    if DEBUG:
        print("POST", get_full_url(path, client))
        if not "password" in data:
            print("Body:", data)
    retry = True
    while retry:
        response = client.session.post(
            get_full_url(path, client),
            json=data,
            headers=make_auth_header(client=client),
        )
        _, retry = check_status(response, path, client=client)
    try:
        result = response.json()
    except JSONDecodeError:
        print(response.text)
        raise
    return result


def put(path, data, client=default_client):
    """
    Run a put request toward given path for configured host.

    Args:
        path (str): The path to query.
        data (dict): The data to put.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    if DEBUG:
        print("PUT", get_full_url(path, client))
        print("Body:", data)
    retry = True
    while retry:
        response = client.session.put(
            get_full_url(path, client),
            json=data,
            headers=make_auth_header(client=client),
        )
        _, retry = check_status(response, path, client=client)
    return response.json()


def delete(path, params=None, client=default_client):
    """
    Run a delete request toward given path for configured host.

    Args:
        path (str): The path to query.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        The request result.
    """
    if DEBUG:
        print("DELETE", get_full_url(path, client))
    path = build_path_with_params(path, params)

    retry = True
    while retry:
        response = client.session.delete(
            get_full_url(path, client), headers=make_auth_header(client=client)
        )
        _, retry = check_status(response, path, client=client)
    return response.text


def get_message_from_response(
    response, default_message="No additional information"
):
    """
    A utility function that handles Zou's inconsistent message keys.
    For a given request, checks if any error messages or regular messages were given and returns their value.
    If no messages are found, returns a default message.

    Args:
        response: requests.Request - A response to check.
        default_message: str - An optional default value to revert to if no message is detected.

    Returns:
        str: The message to display to the user.
    """
    message = default_message
    message_json = response.json()

    if hasattr(message_json, "get"):
        for key in ["error", "message"]:
            if message_json.get(key):
                message = message_json[key]
                break

    return message


def check_status(request, path, client=None):
    """
    Raise an exception related to status code, if the status code does not
    match a success code. Print error message when it's relevant.

    Args:
        request (Request): The request to validate.
        path (str): The path of the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        int: Status code

    Raises:
        ParameterException: when 400 response occurs
        NotAuthenticatedException: when 401 response occurs
        RouteNotFoundException: when 404 response occurs
        NotAllowedException: when 403 response occurs
        MethodNotAllowedException: when 405 response occurs
        TooBigFileException: when 413 response occurs
        ServerErrorException: when 500 response occurs
    """
    status_code = request.status_code
    if status_code == 404:
        raise RouteNotFoundException(path)
    elif status_code == 403:
        raise NotAllowedException(path)
    elif status_code == 400:
        raise ParameterException(path, get_message_from_response(request))
    elif status_code == 405:
        raise MethodNotAllowedException(path)
    elif status_code == 413:
        raise TooBigFileException(
            "%s: You send a too big file. "
            "Change your proxy configuration to allow bigger files." % path
        )
    elif status_code in [401, 422]:
        try:
            if (
                client
                and client.refresh_token
                and client.use_refresh_token
                and request.json()["message"] == "Signature has expired"
            ):
                client.refresh_access_token()
                return status_code, True
            else:
                raise NotAuthenticatedException(path)
        except NotAuthenticatedException:
            if client and client.callback_not_authenticated:
                retry = client.callback_not_authenticated(client, path)
                if retry:
                    return status_code, True
            raise
    elif status_code in [500, 502]:
        try:
            print("A server error occured!\n")
            stacktrace = request.json().get(
                "stacktrace", "No stacktrace sent by the server"
            )
            print("Server stacktrace:\n%s" % stacktrace)
            message = get_message_from_response(
                response=request,
                default_message="No message sent by the server",
            )
            print("Error message:\n%s\n" % message)
        except Exception:
            print(request.text)
        raise ServerErrorException(path)
    return status_code, False


def fetch_all(
    path, params=None, client=default_client, paginated=False, limit=None
):
    """
    Args:
        path (str): The path for which we want to retrieve all entries.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.
        paginated (bool): Will query entries page by page.
        limit (int): Limit the number of entries per page.

    Returns:
        list: All entries stored in database for a given model. You can add a
        filter to the model name like this: "tasks?project_id=project-id"
    """

    if paginated:
        if not params:
            params = {}
        params["page"] = 1
        if limit is not None:
            params["limit"] = limit

    url = url_path_join("data", path)

    response = get(url, params=params, client=client)

    if not paginated:
        return response

    nb_pages = response.get("nb_pages", 1)
    current_page = response.get("page", 1)
    results = response.get("data", [])

    if current_page != nb_pages:
        for page in range(2, nb_pages + 1):
            params["page"] = page
            response = get(
                url,
                params=params,
                client=client,
            )
            results += response.get("data", [])

    return results


def fetch_first(path, params=None, client=default_client):
    """
    Args:
        path (str): The path for which we want to retrieve the first entry.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The first entry for which a model is required.
    """
    entries = get(url_path_join("data", path), params=params, client=client)
    if len(entries) > 0:
        return entries[0]
    else:
        return None


def fetch_one(model_name, id, params=None, client=default_client):
    """
    Function dedicated at targeting routes that returns a single model
    instance.

    Args:
        model_name (str): Model type name.
        id (str): Model instance ID.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The model instance matching id and model name.
    """
    return get(
        url_path_join("data", model_name, id), params=params, client=client
    )


def create(model_name, data, client=default_client):
    """
    Create an entry for given model and data.

    Args:
        model_name (str): The model type involved.
        data (str): The data to use for creation.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: Created entry
    """
    return post(url_path_join("data", model_name), data, client=client)


def update(model_name, model_id, data, client=default_client):
    """
    Update an entry for given model, id and data.

    Args:
        model_name (str): The model type involved.
        model_id (str): The target model id.
        data (dict): The data to update.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: Updated entry
    """
    return put(
        url_path_join("data", model_name, model_id), data, client=client
    )


def upload(
    path,
    file_path=None,
    data={},
    extra_files=[],
    files=None,
    client=default_client,
):
    """
    Upload file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to upload file.
        file_path (str): The file location on the hard drive.
        data (dict): The data to send with the file.
        extra_files (list): List of extra files to upload.
        files (dict): The dictionary of files to upload.
        client (KitsuClient): The client to use for the request.

    Returns:
        Response: Request response object.
    """
    url = get_full_url(path, client)
    if not files:
        files = _build_file_dict(file_path, extra_files)
    retry = True
    while retry:
        response = client.session.post(
            url,
            data=data,
            headers=make_auth_header(client=client),
            files=files,
        )
        _, retry = check_status(response, path, client=client)
    try:
        result = response.json()
    except JSONDecodeError:
        print(response.text)
        raise

    result_message = get_message_from_response(response, default_message="")
    if result_message:
        raise UploadFailedException(result_message)

    return result


def _build_file_dict(file_path, extra_files):
    """
    Build a dictionary of files to upload.

    Args:
        file_path (str): The file location on the hard drive.
        extra_files (list): List of extra files to upload.

    Returns:
        dict: The dictionary of files to upload.
    """

    files = {"file": open(file_path, "rb")}
    i = 0
    for file_path in extra_files:
        i += 1
        files["file-%s" % i] = open(file_path, "rb")

    return files


def download(path, file_path, params=None, client=default_client):
    """
    Download file located at *file_path* to given url *path*.

    Args:
        path (str): The url path to download file from.
        file_path (str): The location to store the file on the hard drive.
        params (dict): The parameters to pass to the request.
        client (KitsuClient): The client to use for the request.

    Returns:
        Response: Request response object.

    """
    path = build_path_with_params(path, params)
    with client.session.get(
        get_full_url(path, client),
        headers=make_auth_header(client=client),
        stream=True,
    ) as response:
        with open(file_path, "wb") as target_file:
            shutil.copyfileobj(response.raw, target_file)
        return response


def get_file_data_from_url(url, full=False, client=default_client):
    """
    Return data found at given url.

    Args:
        url (str): The url to fetch data from.
        full (bool): Whether to use full url.
        client (KitsuClient): The client to use for the request.

    Returns:
        bytes: The data found at the given url.
    """
    if not full:
        url = get_full_url(url)
    retry = True
    while retry:
        response = requests.get(
            url,
            stream=True,
            headers=make_auth_header(client=client),
        )
        _, retry = check_status(response, url, client=client)
    return response.content


def import_data(model_name, data, client=default_client):
    """
    Import data for given model.

    Args:
        model_name (str): The data model to import.
        data (dict): The data to import.
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: The imported data.
    """
    return post("/import/kitsu/%s" % model_name, data, client=client)


def get_api_version(client=default_client):
    """
    Get the current version of the API.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        str: Current version of the API.
    """
    return get("", client=client)["version"]


def get_current_user(client=default_client):
    """
    Get the current user.

    Args:
        client (KitsuClient): The client to use for the request.

    Returns:
        dict: User database information for user linked to auth tokens.
    """
    return get("auth/authenticated", client=client)["user"]
