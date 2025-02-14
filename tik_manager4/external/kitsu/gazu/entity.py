from . import client as raw

from .cache import cache
from .sorting import sort_by_name
from .helpers import normalize_model_parameter

default = raw.default_client


@cache
def all_entities(client=default):
    """
    Returns:
        list: Retrieve all entities
    """
    return raw.fetch_all("entities", client=client)


@cache
def all_entity_types(client=default):
    """
    Returns:
        list: Entity types listed in database.
    """
    return sort_by_name(raw.fetch_all("entity-types", client=client))


@cache
def get_entity(entity_id, client=default):
    """
    Args:
        entity_id (str): ID of claimed entity.

    Returns:
        dict: Retrieve entity matching given ID (it can be an entity of any
        kind: asset, shot, sequence, episode, etc).
    """
    return raw.fetch_one("entities", entity_id, client=client)


@cache
def get_entity_by_name(entity_name, project=None, client=default):
    """
    Args:
        name (str): The name of the claimed entity.
        project (str, dict): Project ID or dict.

    Returns:
        Retrieve entity matching given name (and project if given).
    """
    params = {"name": entity_name}
    if project is not None:
        project = normalize_model_parameter(project)
        params["project_id"] = project["id"]
    return raw.fetch_first("entities", params, client=client)


@cache
def get_entity_type(entity_type_id, client=default):
    """
    Args:
        entity_type_id (str): ID of claimed entity type.
    Returns:
        Retrieve entity type matching given ID (It can be an entity type of any
        kind).
    """
    return raw.fetch_one("entity-types", entity_type_id, client=client)


@cache
def get_entity_type_by_name(entity_type_name, client=default):
    """
    Args:
        entity_type_name (str): The name of the claimed entity type

    Returns:
        Retrieve entity type matching given name.
    """
    return raw.fetch_first(
        "entity-types", {"name": entity_type_name}, client=client
    )


@cache
def guess_from_path(project_id, path, sep="/"):
    """
    Get list of possible project file tree templates matching a file path
    and data ids corresponding to template tokens.

    Args:
        project_id (str): Project id of given file
        file_path (str): Path to a file
        sep (str): File path separator, defaults to "/"
    Returns:
        list: dictionnaries with the corresponding entities and template name.
    """
    return raw.post(
        "/data/entities/guess_from_path",
        {"project_id": project_id, "file_path": path, "sep": sep},
    )


def new_entity_type(name, client=default):
    """
    Creates an entity type with the given name.

    Args:
        name (str, client=default): The name of the entity type

    Returns:
        dict: The created entity type
    """
    data = {"name": name}
    return raw.create("entity-types", data, client=client)


def remove_entity(entity, force=False, client=default):
    """
    Remove given entity from database.

    Args:
        entity (dict): Entity to remove.
    """
    entity = normalize_model_parameter(entity)
    path = "data/entities/%s" % entity["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


def all_entities_with_tasks_linked_to_entity(entity, client=default):
    """
    Args:
        entity (dict): Entity to get linked entities.
    Returns:
        list: Retrieve all entities linked to given entity.
    """
    entity = normalize_model_parameter(entity)
    return raw.fetch_all(
        "entities/%s/entities-linked/with-tasks" % entity["id"], client=client
    )
