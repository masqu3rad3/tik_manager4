from . import client as raw

from .helpers import normalize_model_parameter
from .sorting import sort_by_name

from .cache import cache

default = raw.default_client


@cache
def all_playlists(client=default):
    """
    Returns:
        list: All playlists for all projects.
    """
    return sort_by_name(raw.fetch_all("playlists", client=client))


@cache
def all_shots_for_playlist(playlist, client=default):
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        list: All shots linked to the given playlist
    """
    playlist = normalize_model_parameter(playlist)
    playlist = raw.fetch_one("playlists", playlist["id"], client=client)
    return sort_by_name(playlist["shots"])


@cache
def all_playlists_for_project(project, client=default, page=1):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: All playlists for the given project
    """
    project = normalize_model_parameter(project)
    return sort_by_name(
        raw.fetch_all(
            "projects/%s/playlists" % project["id"],
            params={"page": page},
            client=client,
        )
    )


@cache
def all_playlists_for_episode(episode, client=default):
    """

    Args:
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        list: All playlists for the given episode.
    """

    project = normalize_model_parameter(episode["project_id"])
    return sort_by_name(
        raw.fetch_all(
            "projects/%s/episodes/%s/playlists"
            % (
                project["id"],
                episode["id"],
            ),
            client=client,
        )
    )


@cache
def get_playlist(playlist, client=default):
    """
    Args:
        playlist (str / dict): The playlist dict or the playlist ID.

    Returns:
        dict: playlist object for given id.
    """

    playlist = normalize_model_parameter(playlist)
    return raw.fetch_one("playlists", playlist["id"], client=client)


@cache
def get_playlist_by_name(project, name, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The playlist name

    Returns:
        dict: Playlist matching given name for given project.
    """
    project = normalize_model_parameter(project)
    params = {"project_id": project["id"], "name": name}
    return raw.fetch_first("playlists", params=params, client=client)


def new_playlist(
    project,
    name,
    episode=None,
    for_entity="shot",
    for_client=False,
    client=default,
):
    """
    Create a new playlist in the database for given project.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): Playlist name.

    Returns:
        dict: Created playlist.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "project_id": project["id"],
        "for_entity": for_entity,
        "for_client": for_client,
    }
    if episode is not None:
        episode = normalize_model_parameter(episode)
        data["episode_id"] = episode["id"]
    playlist = get_playlist_by_name(project, name, client=client)
    if playlist is None:
        playlist = raw.post("data/playlists/", data, client=client)
    return playlist


def update_playlist(playlist, client=default):
    """
    Save given playlist data into the API. Metadata are fully replaced by
    the ones set on given playlist.

    Args:
        playlist (dict): The playlist dict to update.

    Returns:
        dict: Updated playlist.
    """
    return raw.put(
        "data/playlists/%s" % playlist["id"], playlist, client=client
    )


def get_entity_preview_files(entity, client=default):
    """
    Get all preview files grouped by task type for a given entity.

    Args:
        entity (str / dict): The entity to retrieve files from or its ID.

    Returns:
        dict: A dict where keys are task type IDs and value array of revisions.
    """
    entity = normalize_model_parameter(entity)
    return raw.get(
        "data/playlists/entities/%s/preview-files" % entity["id"],
        client=client,
    )


def add_entity_to_playlist(
    playlist, entity, preview_file=None, persist=True, client=default
):
    """
    Add an entity to the playlist, use the last uploaded preview as revision
    to review.

    Args:
        playlist (dict): Playlist object to modify.
        entity (str / dict): The entity to add or its ID.
        preview_file (str / dict): Set it to force a give revision to review.
        persist (bool): Set it to True to save the result to the API.

    Returns:
        dict: Updated playlist.
    """
    entity = normalize_model_parameter(entity)

    if preview_file is None:
        preview_files = get_entity_preview_files(entity)
        for task_type_id in preview_files.keys():
            task_type_files = preview_files[task_type_id]
            first_file = task_type_files[0]
            if (
                preview_file is None
                or preview_file["created_at"] < first_file["created_at"]
            ):
                preview_file = first_file

    preview_file = normalize_model_parameter(preview_file)
    playlist["shots"].append(
        {"entity_id": entity["id"], "preview_file_id": preview_file["id"]}
    )
    if persist:
        update_playlist(playlist, client=client)
    return playlist


def remove_entity_from_playlist(
    playlist, entity, persist=True, client=default
):
    """
    Remove all occurences of a given entity from a playlist.

    Args:
        playlist (dict): Playlist object to modify
        entity (str / dict): the entity to remove or its ID

    Returns:
        dict: Updated playlist.
    """
    entity = normalize_model_parameter(entity)
    playlist["shots"] = [
        entry
        for entry in playlist["shots"]
        if entry["entity_id"] != entity["id"]
    ]
    if persist:
        update_playlist(playlist, client=client)
    return playlist


def update_entity_preview(
    playlist, entity, preview_file, persist=True, client=default
):
    """
    Remove all occurences of a given entity from a playlist.

    Args:
        playlist (dict): Playlist object to modify
        entity (str / dict): the entity to add or its ID

    Returns:
        dict: Updated playlist.
    """
    entity = normalize_model_parameter(entity)
    preview_file = normalize_model_parameter(preview_file)
    for entry in playlist["shots"]:
        if entry["entity_id"] == entity["id"]:
            entry["preview_file_id"] = preview_file["id"]
    if persist:
        update_playlist(playlist, client=client)
    return playlist
