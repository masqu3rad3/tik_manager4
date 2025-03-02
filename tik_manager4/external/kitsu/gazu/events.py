import sys

if sys.version_info[0] == 2:
    raise ImportError(
        "The events part of Gazu is not available for Python 2.7"
    )
from .exception import AuthFailedException
from .client import default_client, get_event_host
from gazu.client import make_auth_header
from engineio.base_client import signal_handler
import socketio
import os
import inspect
import signal
import socketio

if os.name == "nt":
    from win32api import SetConsoleCtrlHandler

    def WindowsSignalHandler(event):
        if event == 0:
            try:
                signal_handler(signal.SIGINT, inspect.currentframe())
            except:
                # SetConsoleCtrlHandler handle cannot raise exceptions
                pass

    SetConsoleCtrlHandler(WindowsSignalHandler, 1)


class EventsNamespace(socketio.ClientNamespace):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_error(self, data):
        return connect_error(data)


def init(
    client=default_client,
    ssl_verify=False,
    reconnection=True,
    logger=False,
    **kwargs
):
    """
    Init configuration for SocketIO client.

    Returns:
        Event client that will be able to set listeners.
    """
    params = {
        "ssl_verify": ssl_verify,
        "reconnection": reconnection,
        "logger": logger,
    }
    params.update(kwargs)
    event_client = socketio.Client(**params)
    event_client.on("connect_error", connect_error)
    event_client.register_namespace(EventsNamespace("/events"))
    event_client.connect(get_event_host(client), make_auth_header())
    return event_client


def connect_error(data):
    print("The connection failed!")
    print(data)
    return data


def add_listener(event_client, event_name, event_handler):
    """
    Set a listener that reacts to a given event.
    """
    event_client.on(event_name, event_handler, "/events")
    return event_client


def run_client(event_client):
    """
    Run event client (it blocks current thread). It listens to all events
    configured.
    """
    try:
        print("Listening to Kitsu events...")
        event_client.wait()
    except TypeError:
        raise AuthFailedException
    return event_client
