from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .helpers import (
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)

default = raw.default_client


@cache
def all_project_status(client=default):
    """
    Returns:
        list: Project status listed in database.
    """
    return sort_by_name(raw.fetch_all("project-status", client=client))


@cache
def get_project_status_by_name(project_status_name, client=default):
    """
    Args:
        project_status_name (str): Name of claimed project status.

    Returns:
        dict: Project status corresponding to given name.
    """
    return raw.fetch_first(
        "project-status", {"name": project_status_name}, client=client
    )


@cache
def all_projects(client=default):
    """
    Returns:
        list: Projects stored in the database.
    """
    return sort_by_name(raw.fetch_all("projects", client=client))


@cache
def all_open_projects(client=default):
    """
    Returns:
        Open projects stored in the database.
    """
    return sort_by_name(raw.fetch_all("projects/open", client=client))


@cache
def get_project(project_id, client=default):
    """
    Args:
        project_id (str): ID of claimed project.

    Returns:
        dict: Project corresponding to given id.
    """
    return raw.fetch_one("projects", project_id, client=client)


@cache
def get_project_url(project, section="assets", client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        section (str): The section we want to open in the browser.

    Returns:
        url (str): Web url associated to the given project
    """
    project = normalize_model_parameter(project)
    path = "{host}/productions/{project_id}/{section}/"
    return path.format(
        host=raw.get_api_url_from_host(),
        project_id=project["id"],
        section=section,
    )


@cache
def get_project_by_name(project_name, client=default):
    """
    Args:
        project_name (str): Name of claimed project.

    Returns:
        dict: Project corresponding to given name.
    """
    return raw.fetch_first("projects", {"name": project_name}, client=client)


def new_project(
    name,
    production_type="short",
    team=[],
    asset_types=[],
    task_statuses=[],
    task_types=[],
    production_style="2d3d",
    client=default,
):
    """
    Creates a new project.

    Args:
        name (str): Name of the project to create.
        production_type (str): short, featurefilm, tvshow.
        team (list): Team of the project.
        asset_types (list): Asset types of the project.
        task_statuses (list): Task statuses of the project.
        task_types (list): Task types of the project.
        production_style (str): 2d, 3d, 2d3d, ar, vfx, stop-motion, motion-design,
            archviz, commercial, catalog, immersive, nft, video-game, vr.
    Returns:
        dict: Created project.
    """
    project = get_project_by_name(name, client=client)
    if project is None:
        project = raw.create(
            "projects",
            {
                "name": name,
                "production_type": production_type,
                "team": normalize_list_of_models_for_links(team),
                "asset_types": normalize_list_of_models_for_links(asset_types),
                "task_statuses": normalize_list_of_models_for_links(
                    task_statuses
                ),
                "task_types": normalize_list_of_models_for_links(task_types),
                "production_style": production_style,
            },
            client=client,
        )
    return project


def remove_project(project, force=False, client=default):
    """
    Remove given project from database. (Prior to do that, make sure, there
    is no asset or shot left).

    Args:
        project (dict / str): Project to remove.
    """
    project = normalize_model_parameter(project)
    path = "data/projects/%s" % project["id"]
    if force:
        path += "?force=true"
    return raw.delete(path, client=client)


def update_project(project, client=default):
    """
    Save given project data into the API. Metadata are fully replaced by the
    ones set on given project.

    Args:
        project (dict): The project to update.

    Returns:
        dict: Updated project.
    """
    if "team" in project:
        project["team"] = normalize_list_of_models_for_links(project["team"])
    if "asset_types" in project:
        project["asset_types"] = normalize_list_of_models_for_links(
            project["asset_types"]
        )
    if "task_statuses" in project:
        project["task_statuses"] = normalize_list_of_models_for_links(
            project["task_statuses"]
        )
    if "task_types" in project:
        project["task_types"] = normalize_list_of_models_for_links(
            project["task_types"]
        )
    return raw.put("data/projects/%s" % project["id"], project, client=client)


def update_project_data(project, data={}, client=default):
    """
    Update the metadata for the provided project. Keys that are not provided
    are not changed.

    Args:
        project (dict / ID): The project dict or id to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated project.
    """
    project = normalize_model_parameter(project)
    project = get_project(project["id"], client=client)
    if "data" not in project or project["data"] is None:
        project["data"] = {}
    project["data"].update(data)
    return update_project(project, client=client)


def close_project(project, client=default):
    """
    Closes the provided project.

    Args:
        project (dict / ID): The project dict or id to save in database.

    Returns:
        dict: Updated project.
    """
    project = normalize_model_parameter(project)
    closed_status_id = None
    for status in all_project_status(client=client):
        if status["name"].lower() == "closed":
            closed_status_id = status["id"]

    project["project_status_id"] = closed_status_id
    update_project(project, client=client)
    return project


def add_asset_type(project, asset_type, client=default):
    project = normalize_model_parameter(project)
    asset_type = normalize_model_parameter(asset_type)
    data = {"asset_type_id": asset_type["id"]}
    return raw.post(
        "data/projects/%s/settings/asset-types" % project["id"],
        data,
        client=client,
    )


def add_task_type(project, task_type, priority, client=default):
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    data = {"task_type_id": task_type["id"], "priority": priority}
    return raw.post(
        "data/projects/%s/settings/task-types" % project["id"],
        data,
        client=client,
    )


def add_task_status(project, task_status, client=default):
    project = normalize_model_parameter(project)
    task_status = normalize_model_parameter(task_status)
    data = {"task_status_id": task_status["id"]}
    return raw.post(
        "data/projects/%s/settings/task-status" % project["id"],
        data,
        client=client,
    )


def add_metadata_descriptor(
    project,
    name,
    entity_type,
    data_type="string",
    choices=[],
    for_client=False,
    departments=[],
    client=default,
):
    """
    Create a new metadata descriptor for a project.

    Args:
        project (dict / ID): The project dict or id.
        name (str): The name of the metadata descriptor
        entity_type (str): asset, shot or scene.
        choices (list): A list of possible values, empty list for free values.
        for_client (bool) : Wheter it should be displayed in Kitsu or not.
        departments (list): A list of departments dict or id.

    Returns:
        dict: Created metadata descriptor.
    """
    project = normalize_model_parameter(project)
    data = {
        "name": name,
        "data_type": data_type,
        "choices": choices,
        "for_client": for_client,
        "entity_type": entity_type,
        "departments": normalize_list_of_models_for_links(departments),
    }
    return raw.post(
        "data/projects/%s/metadata-descriptors" % project["id"],
        data,
        client=client,
    )


def get_metadata_descriptor(project, metadata_descriptor_id, client=default):
    """
    Retrieve a the metadata descriptor matching given ID.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or id.

    Returns:
        dict: The metadata descriptor matching the ID.
    """
    project = normalize_model_parameter(project)
    metadata_descriptor = normalize_model_parameter(metadata_descriptor_id)
    return raw.fetch_one(
        "projects/%s/metadata-descriptors" % project["id"],
        metadata_descriptor["id"],
        client=client,
    )


def get_metadata_descriptor_by_field_name(project, field_name, client=default):
    """
    Get a metadata descriptor matchind given project and name.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or id.

    Returns:
        dict: The metadata descriptor matchind the ID.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_first(
        "metadata-descriptors",
        params={
            "project_id": project["id"],
            "field_name": field_name,
        },
        client=client,
    )


def all_metadata_descriptors(project, client=default):
    """
    Get all the metadata descriptors.

    Args:
        project (dict / ID): The project dict or id.

    Returns:
        list: The metadata descriptors.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all(
        "projects/%s/metadata-descriptors" % project["id"],
        client=client,
    )


def update_metadata_descriptor(project, metadata_descriptor, client=default):
    """
    Update a metadata descriptor.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor (dict): The metadata descriptor that needs to be updated.

    Returns:
        dict: The updated metadata descriptor.
    """
    if "departments" in metadata_descriptor:
        metadata_descriptor["departments"] = (
            normalize_list_of_models_for_links(
                metadata_descriptor["departments"]
            )
        )

    project = normalize_model_parameter(project)
    return raw.put(
        "data/projects/%s/metadata-descriptors/%s"
        % (project["id"], metadata_descriptor["id"]),
        metadata_descriptor,
        client=client,
    )


def remove_metadata_descriptor(
    project, metadata_descriptor_id, force=False, client=default
):
    """
    Remove a metadata descriptor.

    Args:
        project (dict / ID): The project dict or id.
        metadata_descriptor_id (dict / ID): The metadata descriptor dict or id.
    """
    project = normalize_model_parameter(project)
    metadata_descriptor = normalize_model_parameter(metadata_descriptor_id)
    params = {}
    if force:
        params = {"force": True}
    return raw.delete(
        "data/projects/%s/metadata-descriptors/%s"
        % (project["id"], metadata_descriptor["id"]),
        params,
        client=client,
    )


def get_team(project, client=default):
    """
    Get team for project.

    Args:
        project (dict / ID): The project dict or id.
    """
    project = normalize_model_parameter(project)
    return raw.fetch_all("projects/%s/team" % project["id"], client=client)


def add_person_to_team(project, person, client=default):
    """
    Add a person to the team project.

    Args:
        project (dict / ID): The project dict or id.
        person (dict / ID): The person dict or id.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    data = {"person_id": person["id"]}
    return raw.post(
        "data/projects/%s/team" % project["id"], data, client=client
    )


def remove_person_from_team(project, person, client=default):
    """
    Remove a person from the team project.

    Args:
        project (dict / ID): The project dict or id.
        person (dict / ID): The person dict or id.
    """
    project = normalize_model_parameter(project)
    person = normalize_model_parameter(person)
    return raw.delete(
        "data/projects/%s/team/%s" % (project["id"], person["id"]),
        client=client,
    )
