import os

from .helpers import normalize_model_parameter

from . import client as raw
from . import asset as asset_module
from . import casting as casting_module
from . import person as person_module
from . import project as project_module
from . import files as files_module
from . import shot as shot_module
from . import task as task_module

from .helpers import normalize_model_parameter, validate_date_format

default = raw.default_client


def get_last_events(
    limit=20000,
    project=None,
    after=None,
    before=None,
    only_files=False,
    name=None,
    client=default,
):
    """
    Get last events that occured on the machine.

    Args:
        limit (int): Number of events to retrieve.
        project (dict/id): Get only events related to this project.
        after (dict/id): Get only events occuring after given date.
        before (dict/id): Get only events occuring before given date.
        only_files (bool): Get only events related to files.

    Returns:
        dict: Last events matching criterions.
    """
    path = "/data/events/last"
    params = {"limit": limit, "only_files": only_files}
    if project is not None:
        project = normalize_model_parameter(project)
        params["project_id"] = project["id"]
    if after is not None:
        params["after"] = validate_date_format(after)
    if before is not None:
        params["before"] = validate_date_format(before)
    if name is not None:
        params["name"] = name
    return raw.get(path, params=params, client=client)


def import_entities(entities, client=default):
    """
    Import entities from another instance to target instance (keep id and audit
    dates).

    Args:
        entities (list): Entities to import.

    Returns:
        dict: Entities created.
    """
    return raw.post("import/kitsu/entities", entities, client=client)


def import_tasks(tasks, client=default):
    """
    Import tasks from another instance to target instance (keep id and audit
    dates).

    Args:
        tasks (list): Tasks to import.

    Returns:
        dict: Tasks created.
    """
    return raw.post("import/kitsu/tasks", tasks, client=client)


def import_entity_links(links, client=default):
    """
    Import enitity links from another instance to target instance (keep id and
    audit dates).

    Args:
        links (list): Entity links to import.

    Returns:
        dict: Entity links created.
    """
    return raw.post("import/kitsu/entity-links", links, client=client)


def get_model_list_diff(source_list, target_list, id_field="id"):
    """
    Args:
        source_list (list): List of models to compare.
        target_list (list): List of models for which we want a diff.

    Returns:
        tuple: Two lists, one containing the missing models in the target list
        and one containing the models that should not be in the target list.
    """
    missing = []
    source_ids = {m[id_field]: True for m in source_list}
    target_ids = {m[id_field]: True for m in target_list}
    missing = [
        model
        for model in source_list
        if not target_ids.get(model[id_field], False)
    ]
    unexpected = [
        model
        for model in target_list
        if not source_ids.get(model[id_field], False)
    ]
    return (missing, unexpected)


def get_link_list_diff(source_list, target_list):
    """
    Args:
        source_list (list): List of links to compare.
        target_list (list): List of links for which we want a diff.

    Returns:
        tuple: Two lists, one containing the missing links in the target list
        and one containing the links that should not be in the target list.
        Links are identified by their in ID and their out ID.
    """

    def get_link_key(l):
        return l["entity_in_id"] + "-" + l["entity_out_id"]

    missing = []
    unexpected = []
    source_ids = {get_link_key(m): True for m in source_list}
    target_ids = {get_link_key(m): True for m in target_list}
    for link in source_list:
        if get_link_key(link) not in target_ids:
            missing.append(link)
    for link in target_list:
        if get_link_key(link) not in source_ids:
            unexpected.append(link)
    return (missing, unexpected)


def get_id_map_by_name(source_list, target_list):
    """
    Args:
        source_list (list): List of links to compare.
        target_list (list): List of links for which we want a diff.

    Returns:
        dict: A dict where keys are the source model names and the values are
        the IDs of the target models with same name.
        It's useful to match a model from the source list to its relative in
        the target list based on its name.
    """
    link_map = {}
    name_map = {}
    for model in target_list:
        name_map[model["name"].lower()] = model["id"]
    for model in source_list:
        if model["name"].lower() in name_map:
            link_map[model["name"]] = name_map[model["name"].lower()]
    return link_map


def get_id_map_by_id(source_list, target_list, field="name"):
    """
    Args:
        source_list (list): List of links to compare.
        target_list (list): List of links for which we want a diff.

    Returns:
        dict: A dict where keys are the source model names and the values are
        the IDs of the target models with same name.
        It's useful to match a model from the source list to its relative in
        the target list based on its name.
    """
    link_map = {}
    name_map = {}
    for model in target_list:
        name_map[model[field].lower()] = model["id"]
    for model in source_list:
        if model[field].lower() in name_map:
            link_map[model["id"]] = name_map[model[field].lower()]
    return link_map


def is_changed(source_model, target_model):
    """
    Args:
        source_model (dict): Model from the source API.
        target_model (dict): Matching model from the target API.

    Returns:
        bool: True if the source model is older than the target model (based on
        `updated_at` field)
    """
    source_date = source_model["updated_at"]
    target_date = target_model["updated_at"]
    return source_date > target_date


def get_sync_department_id_map(source_client, target_client):
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source departments ids with target department ids
    """
    departments_source = person_module.all_departments(client=source_client)
    departments_target = person_module.all_departments(client=target_client)
    return get_id_map_by_id(departments_source, departments_target)


def get_sync_asset_type_id_map(source_client, target_client):
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source asset type ids with target asset type ids
    """
    asset_types_source = asset_module.all_asset_types(client=source_client)
    asset_types_target = asset_module.all_asset_types(client=target_client)
    return get_id_map_by_id(asset_types_source, asset_types_target)


def get_sync_project_id_map(source_client, target_client):
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source project ids with target project ids
    """
    projects_source = project_module.all_projects(client=source_client)
    projects_target = project_module.all_projects(client=target_client)
    return get_id_map_by_id(projects_source, projects_target)


def get_sync_task_type_id_map(source_client, target_client):
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source task type ids with target task type ids
    """
    task_types_source = task_module.all_task_types(client=source_client)
    task_types_target = task_module.all_task_types(client=target_client)
    return get_id_map_by_id(task_types_source, task_types_target)


def get_sync_task_status_id_map(source_client, target_client):
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source task status ids with target task status
              ids
    """
    task_statuses_source = task_module.all_task_statuses(client=source_client)
    task_statuses_target = task_module.all_task_statuses(client=target_client)
    return get_id_map_by_id(task_statuses_source, task_statuses_target)


def get_sync_person_id_map(source_client, target_client):
    """
    Args:
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: A dict matching source person ids with target person ids
    """
    persons_source = person_module.all_persons(client=source_client)
    persons_target = person_module.all_persons(client=target_client)
    return get_id_map_by_id(persons_source, persons_target, field="email")


def push_assets(project_source, project_target, client_source, client_target):
    """
    Copy assets from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Pushed assets
    """
    asset_types_map = get_sync_asset_type_id_map(client_source, client_target)
    task_types_map = get_sync_task_type_id_map(client_source, client_target)
    assets = asset_module.all_assets_for_project(
        project_source, client=client_source
    )
    for asset in assets:
        asset["entity_type_id"] = asset_types_map[asset["entity_type_id"]]
        if asset["ready_for"] is not None:
            asset["ready_for"] = task_types_map[asset["ready_for"]]
        asset["project_id"] = project_target["id"]
    return import_entities(assets, client=client_target)


def push_episodes(
    project_source, project_target, client_source, client_target
):
    """
    Copy episodes from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`)

    Args:
        project_source (dict): The project to get episodes from
        project_target (dict): The project to push episodes to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Pushed episodes
    """
    episodes = shot_module.all_episodes_for_project(
        project_source, client=client_source
    )
    for episode in episodes:
        episode["project_id"] = project_target["id"]
    return import_entities(episodes, client=client_target)


def push_sequences(
    project_source, project_target, client_source, client_target
):
    """
    Copy sequences from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`)

    Args:
        project_source (dict): The project to get sequences from
        project_target (dict): The project to push sequences to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Pushed sequences
    """
    sequences = shot_module.all_sequences_for_project(
        project_source, client=client_source
    )
    for sequence in sequences:
        sequence["project_id"] = project_target["id"]
    return import_entities(sequences, client=client_target)


def push_shots(project_source, project_target, client_source, client_target):
    """
    Copy shots from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get shots from
        project_target (dict): The project to push shots to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Pushed shots
    """
    shots = shot_module.all_shots_for_project(
        project_source, client=client_source
    )
    for shot in shots:
        shot["project_id"] = project_target["id"]
    return import_entities(shots, client=client_target)


def push_entity_links(
    project_source, project_target, client_source, client_target
):
    """
    Copy entity links (breakdown, concepts) from source to target and preserve
    audit fields (`id`, `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Pushed entity links
    """
    links = casting_module.all_entity_links_for_project(
        project_source, client=client_source
    )
    return import_entity_links(links, client=client_target)


def push_project_entities(
    project_source, project_target, client_source, client_target
):
    """
    Copy assets, episodes, sequences, shots and entity links from source to
    target and preserve audit fields (`id`, `created_at`, and `updated_at`).

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        dict: Pushed data
    """
    assets = push_assets(project_source, project_target)
    episodes = []
    if project_source["production_type"] == "tvshow":
        episodes = push_episodes(project_source, project_target)
    sequences = push_sequences(project_source, project_target)
    shots = push_shots(project_source, project_target)
    entity_links = push_entity_links(project_source, project_target)
    return {
        "assets": assets,
        "episodes": episodes,
        "sequences": sequences,
        "shots": shots,
        "entity_links": entity_links,
    }


def push_tasks(
    project_source,
    project_target,
    default_status,
    client_source,
    client_target,
):
    """
    Copy tasks from source to target and preserve audit fields (`id`,
    `created_at`, and `updated_at`)
    Attachments and previews are created too.

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Pushed entity links
    """

    default_status_id = normalize_model_parameter(default_status)["id"]
    task_type_map = get_sync_task_type_id_map(client_source, client_target)
    person_map = get_sync_person_id_map(client_source, client_target)

    tasks = task_module.all_tasks_for_project(
        project_source, client=client_source
    )
    for task in tasks:
        task["task_type_id"] = task_type_map[task["task_type_id"]]
        task["task_status_id"] = default_status_id
        task["assigner_id"] = person_map[task["assigner_id"]]
        task["project_id"] = project_target["id"]

        task["assignees"] = [
            person_map[person_id] for person_id in task["assignees"]
        ]
    return import_tasks(tasks, client=client_target)


def push_tasks_comments(project_source, client_source, client_target):
    """
    Create a new comment into target api for each comment in source project
    but preserve only `created_at` field.
    Attachments and previews are created too.

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Created comments
    """

    task_status_map = get_sync_task_status_id_map(client_source, client_target)
    person_map = get_sync_person_id_map(client_source, client_target)
    tasks = task_module.all_tasks_for_project(
        project_source, client=client_source
    )
    for task in tasks:
        push_task_comments(
            task_status_map, person_map, task, client_source, client_target
        )
    return tasks


def push_task_comments(
    task_status_map, person_map, task, client_source, client_target
):
    """
    Create a new comment into target api for each comment in source task
    but preserve only `created_at` field.
    Attachments and previews are created too.

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Created comments
    """
    comments = task_module.all_comments_for_task(task, client=client_source)
    comments.reverse()
    comments_target = []
    for comment in comments:
        comment_target = push_task_comment(
            task_status_map,
            person_map,
            task,
            comment,
            client_source,
            client_target,
        )
        comments_target.append(comment_target)
    return comments_target


def push_task_comment(
    task_status_map,
    person_map,
    task,
    comment,
    client_source,
    client_target,
    author_id=None,
    tmp_path="/tmp/zou/sync/",
):
    """
    Create a new comment into target api for each comment in source task
    but preserve only `created_at` field.
    Attachments and previews are created too.

    Args:
        project_source (dict): The project to get assets from
        project_target (dict): The project to push assets to
        source_client (KitsuClient): client to get data from source API
        target_client (KitsuClient): client to push data to target API

    Returns:
        list: Created comments
    """
    attachments = []
    for attachment_id in comment["attachment_files"]:
        if type(attachment_id) == dict:
            attachment_id = attachment_id["id"]
        attachment_file = files_module.get_attachment_file(
            attachment_id, client=client_source
        )
        file_path = os.path.join(tmp_path, attachment_file["name"])
        files_module.download_attachment_file(
            attachment_file, file_path, client=client_source
        )
        attachments.append(file_path)

    previews = []
    for preview_file in comment["previews"]:
        if type(preview_file) is str:
            preview_file_id = preview_file
        else:
            preview_file_id = preview_file["id"]
        preview_file = files_module.get_preview_file(
            preview_file_id, client=client_source
        )
        if (
            preview_file["original_name"] is not None
            and preview_file["extension"] is not None
        ):
            file_path = os.path.join(
                tmp_path,
                preview_file["original_name"]
                + "."
                + preview_file["extension"],
            )
            files_module.download_preview_file(
                preview_file, file_path, client=client_source
            )
            previews.append(
                {
                    "file_path": file_path,
                    "annotations": preview_file["annotations"],
                }
            )

    task_status = {"id": task_status_map[comment["task_status_id"]]}
    if author_id is not None:
        author_id = author_id
    else:
        author_id = person_map[comment["person_id"]]
    person = {"id": author_id}

    comment_target = task_module.add_comment(
        task,
        task_status,
        attachments=attachments,
        comment=comment["text"],
        created_at=comment["created_at"],
        person=person,
        checklist=comment["checklist"] or [],
        client=client_target,
    )

    for preview in previews:
        new_preview_file = task_module.add_preview(
            task, comment_target, preview["file_path"], client=client_target
        )
        files_module.update_preview(
            new_preview_file,
            {"annotations": preview["annotations"]},
            client=client_target,
        )
        try:
            os.remove(preview["file_path"])
        except OSError:
            pass

    for attachment_path in attachments:
        try:
            os.remove(attachment_path)
        except OSError:
            pass

    return comment


def convert_id_list(ids, model_map):
    """
    Args:
        ids (list): Ids to convert.
        model_map (dict): Map matching ids to another value.c

    Returns:
        list: Ids converted through given model map.
    """
    return [model_map[id] for id in ids]
