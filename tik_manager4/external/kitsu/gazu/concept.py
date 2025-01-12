from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)

default = raw.default_client


@cache
def all_concepts(client=default):
    """
    Returns:
        list: All concepts from database.
    """
    concepts = raw.fetch_all("concepts", client=client)
    return sort_by_name(concepts)


@cache
def all_concepts_for_project(project, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.

    Returns:
        list: Concepts from database or for given project.
    """
    project = normalize_model_parameter(project)
    concepts = raw.fetch_all(
        "projects/%s/concepts" % project["id"], client=client
    )
    return sort_by_name(concepts)


@cache
def all_previews_for_concept(concept, client=default):
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.

    Returns:
        list: Previews from database for given concept.
    """
    concept = normalize_model_parameter(concept)
    return raw.fetch_all(
        "concepts/%s/preview-files" % concept["id"], client=client
    )


def remove_concept(concept, force=False, client=default):
    """
    Remove given concept from database.

    Args:
        concept (dict / str): Concept to remove.
    """
    concept = normalize_model_parameter(concept)
    path = "data/concepts/%s" % concept["id"]
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(path, params, client=client)


@cache
def get_concept(concept_id, client=default):
    """
    Args:
        concept_id (str): ID of claimed concept.

    Returns:
        dict: Concept corresponding to given concept ID.
    """
    return raw.fetch_one("concepts", concept_id, client=client)


@cache
def get_concept_by_name(project, concept_name, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        concept_name (str): Name of claimed concept.

    Returns:
        dict: Concept corresponding to given name and project.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "concepts",
        {"project_id": project["id"], "name": concept_name},
        client=client,
    )


def new_concept(
    project,
    name,
    description=None,
    data={},
    entity_concept_links=[],
    client=default,
):
    """
    Create a concept for given project. Allow to set metadata too.

    Args:
        project (str / dict): The project dict or the project ID.
        name (str): The name of the concept to create.
        data (dict): Free field to set metadata of any kind.
        entity_concept_links (list): List of entities to tag.
    Returns:
        Created concept.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "data": data,
        "entity_concept_links": normalize_list_of_models_for_links(
            entity_concept_links
        ),
    }

    if description is not None:
        data["description"] = description

    concept = get_concept_by_name(project, name, client=client)
    if concept is None:
        path = "data/projects/%s/concepts" % project["id"]
        return raw.post(path, data, client=client)
    else:
        return concept


def update_concept(concept, client=default):
    """
    Save given concept data into the API. Metadata are fully replaced by the ones
    set on given concept.

    Args:
        concept (dict): The concept dict to update.

    Returns:
        dict: Updated concept.
    """
    return raw.put("data/entities/%s" % concept["id"], concept, client=client)
