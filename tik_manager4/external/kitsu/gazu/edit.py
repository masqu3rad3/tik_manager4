from . import client as raw

from .cache import cache
from .helpers import normalize_model_parameter
from gazu.sorting import sort_by_name

default = raw.default_client


@cache
def get_edit(edit_id, client=default):
    """
    Args:
        edit_id (str): ID of claimed edit.

    Returns:
        dict: Edit corresponding to given edit ID.
    """
    return raw.fetch_one("edits", edit_id, client=client)


@cache
def get_edit_by_name(project, edit_name, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        edit_name (str): Name of claimed edit.

    Returns:
        dict: Edit corresponding to given name and sequence.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "edits/all",
        {"project_id": project["id"], "name": edit_name},
        client=client,
    )


@cache
def get_edit_url(edit, client=default):
    """
    Args:
        edit (str / dict): The edit dict or the edit ID.

    Returns:
        url (str): Web url associated to the given edit
    """
    edit = normalize_model_parameter(edit)
    edit = get_edit(edit["id"])
    path = "{host}/productions/{project_id}/"
    if edit["episode_id"] is None:
        path += "edits/{edit_id}/"
    else:
        path += "episodes/{episode_id}/edits/{edit_id}/"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        project_id=edit["project_id"],
        edit_id=edit["id"],
        episode_id=edit["episode_id"],
    )


@cache
def all_edits_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Edits from database or for given project.
    """
    project = normalize_model_parameter(project)
    edits = raw.fetch_all("projects/%s/edits" % project["id"], client=client)
    return sort_by_name(edits)


@cache
def all_previews_for_edit(edit, client=default):
    """
    Args:
        edit (str / dict): The edit dict or the edit ID.

    Returns:
        list: Previews from database for given edit.
    """
    edit = normalize_model_parameter(edit)
    return raw.fetch_all("edits/%s/preview-files" % edit["id"], client=client)


def new_edit(
    project,
    name,
    description=None,
    data={},
    episode=None,
    client=default,
):
    """
    Create an edit for given project (and episode if given).
    Allow to set metadata too.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the edit to create.
        description (str): The description of the edit to create.
        data (dict): Free field to set metadata of any kind.
        episode (str / dict): The episode dict or the episode ID.

    Returns:
        Created edit.
    """
    project = normalize_model_parameter(project)
    if episode is not None:
        episode = normalize_model_parameter(episode)

    data = {"name": name, "data": data, "parent_id": episode["id"]}

    if description is not None:
        data["description"] = description

    edit = get_edit_by_name(project, name, client=client)
    if edit is None:
        path = "data/projects/%s/edits" % project["id"]
        return raw.post(path, data, client=client)
    else:
        return edit


def remove_edit(edit, force=False, client=default):
    """
    Remove given edit from database.

    Args:
        edit (dict / str): Edit to remove.
    """
    edit = normalize_model_parameter(edit)
    path = "data/edits/%s" % edit["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def update_edit(edit, client=default):
    """
    Save given edit data into the API. Metadata are fully replaced by the ones
    set on given edit.

    Args:
        edit (dict): The edit dict to update.

    Returns:
        dict: Updated edit.
    """
    return raw.put("data/entities/%s" % edit["id"], edit, client=client)


def update_edit_data(edit, data={}, client=default):
    """
    Update the metadata for the provided edit. Keys that are not provided are
    not changed.

    Args:
        edit (dict / ID): The edit dict or ID to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated edit.
    """
    edit = normalize_model_parameter(edit)
    current_edit = get_edit(edit["id"], client=client)
    updated_edit = {"id": current_edit["id"], "data": current_edit["data"]}
    updated_edit["data"].update(data)
    return update_edit(updated_edit, client=client)
