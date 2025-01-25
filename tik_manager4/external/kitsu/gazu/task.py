import string

import json

# from deprecated import deprecated

from gazu.exception import (
    TaskStatusNotFoundException,
    TaskMustBeADictException,
)

from . import client as raw
from .sorting import sort_by_name
from .helpers import (
    download_file,
    normalize_model_parameter,
    normalize_list_of_models_for_links,
)

from .cache import cache

default = raw.default_client


@cache
def all_task_statuses(client=default):
    """
    Returns:
        list: Task statuses stored in database.
    """
    task_statuses = raw.fetch_all("task-status", client=client)
    return sort_by_name(task_statuses)


@cache
def all_task_types(client=default):
    """
    Returns:
        list: Task types stored in database.
    """
    task_types = raw.fetch_all("task-types", client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_project(project, client=default):
    """
    Returns:
        list: Task types stored in database.
    """
    project = normalize_model_parameter(project)
    task_types = raw.fetch_all(
        "projects/%s/task-types" % project["id"], client=client
    )
    return sort_by_name(task_types)


@cache
def all_task_statuses_for_project(project, client=default):
    """
    Returns:
        list: Task status stored in database.
    """
    project = normalize_model_parameter(project)
    task_statuses = raw.fetch_all(
        "projects/%s/settings/task-status" % project["id"], client=client
    )
    return sort_by_name(task_statuses)


@cache
def all_tasks_for_shot(shot, relations=False, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns:
        list: Tasks linked to given shot.
    """
    shot = normalize_model_parameter(shot)
    params = {}
    if relations:
        params = {"relations": True}
    tasks = raw.fetch_all("shots/%s/tasks" % shot["id"], params, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_concept(concept, relations=False, client=default):
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.

    Returns:
        list: Tasks linked to given concept.
    """
    concept = normalize_model_parameter(concept)
    params = {}
    if relations:
        params = {"relations": True}
    tasks = raw.fetch_all(
        "concepts/%s/tasks" % concept["id"], params, client=client
    )
    return sort_by_name(tasks)


@cache
def all_tasks_for_edit(edit, relations=False, client=default):
    """
    Args:
        edit (str / dict): The edit dict or the edit ID.

    Returns:
        list: Tasks linked to given edit.
    """
    edit = normalize_model_parameter(edit)
    params = {}
    if relations:
        params = {"relations": True}
    tasks = raw.fetch_all("edits/%s/tasks" % edit["id"], params, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_sequence(sequence, relations=False, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns
        list: Tasks linked to given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    params = {}
    if relations:
        params = {"relations": True}
    path = "sequences/%s/tasks" % sequence["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_scene(scene, relations=False, client=default):
    """
    Args:
        sequence (str / dict): The scene dict or the scene ID.

    Returns:
        list: Tasks linked to given scene.
    """
    scene = normalize_model_parameter(scene)
    params = {}
    if relations:
        params = {"relations": True}
    path = "scenes/%s/tasks" % scene["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_asset(asset, relations=False, client=default):
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Tasks directly linked to given asset.
    """
    asset = normalize_model_parameter(asset)
    params = {}
    if relations:
        params = {"relations": True}
    path = "assets/%s/tasks" % asset["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_episode(episode, relations=False, client=default):
    """
    Retrieve all tasks directly linked to given episode.
    """
    episode = normalize_model_parameter(episode)
    params = {}
    if relations:
        params = {"relations": True}
    path = "episodes/%s/tasks" % episode["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_shot_tasks_for_sequence(sequence, relations=False, client=default):
    """
    Retrieve all tasks directly linked to all shots of given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    params = {}
    if relations:
        params = {"relations": True}
    path = "sequences/%s/shot-tasks" % sequence["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_shot_tasks_for_episode(episode, relations=False, client=default):
    """
    Retrieve all tasks directly linked to all shots of given episode.
    """
    episode = normalize_model_parameter(episode)
    params = {}
    if relations:
        params = {"relations": True}
    path = "episodes/%s/shot-tasks" % episode["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_assets_tasks_for_episode(episode, relations=False, client=default):
    """
    Retrieve all tasks directly linked to all assets of given episode.
    """
    episode = normalize_model_parameter(episode)
    params = {}
    if relations:
        params = {"relations": True}
    path = "episodes/%s/asset-tasks" % episode["id"]
    tasks = raw.fetch_all(path, params, client=client)
    return sort_by_name(tasks)


@cache
def all_tasks_for_task_status(project, task_type, task_status, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        task_type (str / dict): The task type dict or ID.
        task_status (str / dict): The task status dict or ID.

    Returns:
        list: Tasks set at given status for given project and task type.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    task_status = normalize_model_parameter(task_status)
    return raw.fetch_all(
        "tasks",
        {
            "project_id": project["id"],
            "task_type_id": task_type["id"],
            "task_status_id": task_status["id"],
        },
        client=client,
    )


@cache
def all_tasks_for_task_type(project, task_type, episode=None, client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        task_type (str / dict): The task type dict or ID.
        episode_id (str / dict): The episode dict or ID.

    Returns:
        list: Tasks for given project and task type.
    """
    project = normalize_model_parameter(project)
    task_type = normalize_model_parameter(task_type)
    params = {
        "project_id": project["id"],
        "task_type_id": task_type["id"],
    }
    if episode is not None:
        episode = normalize_model_parameter(episode)
        params["episode_id"] = episode["id"]
    return raw.fetch_all("tasks", params, client=client)


@cache
def all_task_types_for_shot(shot, client=default):
    """
    Args:
        shot (str / dict): The shot dict or the shot ID.

    Returns
        list: Task types of task linked to given shot.
    """
    shot = normalize_model_parameter(shot)
    path = "shots/%s/task-types" % shot["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_concept(concept, client=default):
    """
    Args:
        concept (str / dict): The concept dict or the concept ID.

    Returns
        list: Task types of task linked to given concept.
    """
    concept = normalize_model_parameter(concept)
    path = "concepts/%s/task-types" % concept["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_asset(asset, client=default):
    """
    Args:
        asset (str / dict): The asset dict or the asset ID.

    Returns:
        list: Task types of tasks related to given asset.
    """
    asset = normalize_model_parameter(asset)
    task_types = raw.fetch_all(
        "assets/%s/task-types" % asset["id"], client=client
    )
    return sort_by_name(task_types)


@cache
def all_task_types_for_scene(scene, client=default):
    """
    Args:
        scene (str / dict): The scene dict or the scene ID.

    Returns:
        list: Task types of tasks linked to given scene.
    """
    scene = normalize_model_parameter(scene)
    path = "scenes/%s/task-types" % scene["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_sequence(sequence, client=default):
    """
    Args:
        sequence (str / dict): The sequence dict or the sequence ID.

    Returns:
        list: Task types of tasks linked directly to given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    path = "sequences/%s/task-types" % sequence["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_task_types_for_episode(episode, client=default):
    """
    Returns:
        list: Task types of tasks linked directly to given episode.
    """
    episode = normalize_model_parameter(episode)
    path = "episodes/%s/task-types" % episode["id"]
    task_types = raw.fetch_all(path, client=client)
    return sort_by_name(task_types)


@cache
def all_tasks_for_entity_and_task_type(entity, task_type, client=default):
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.
        task_type (str / dict): The task type dict or ID.

    Returns:
        list: Tasks for given entity or task type.
    """
    entity = normalize_model_parameter(entity)
    task_type = normalize_model_parameter(task_type)
    task_type_id = task_type["id"]
    entity_id = entity["id"]
    path = "entities/%s/task-types/%s/tasks" % (entity_id, task_type_id)
    return raw.fetch_all(path, client=client)


@cache
def all_tasks_for_person(person, client=default):
    """
    Returns:
        list: Tasks that are not done for given person (only for open projects).
    """
    person = normalize_model_parameter(person)
    return raw.fetch_all("persons/%s/tasks" % person["id"], client=client)


@cache
def all_done_tasks_for_person(person, client=default):
    """
    Returns:
        list: Tasks that are done for given person (only for open projects).
    """
    person = normalize_model_parameter(person)
    return raw.fetch_all("persons/%s/done-tasks" % person["id"], client=client)


@cache
def get_task_by_entity(entity, task_type, name="main", client=default):
    """
    Args:
        entity (str / dict): The entity dict or the entity ID.
        task_type (str / dict): The task type dict or ID.
        name (str): Name of the task to look for.

    Returns:
        Task matching given entity, task type and name.
    """
    entity = normalize_model_parameter(entity)
    task_type = normalize_model_parameter(task_type)
    return raw.fetch_first(
        "tasks",
        {
            "name": name,
            "task_type_id": task_type["id"],
            "entity_id": entity["id"],
        },
        client=client,
    )


# @deprecated(
#     version="0.9.17",
#     reason="You should use another function: gazu.task.get_task_by_entity, it will be removed in a future version of Gazu (0.10.0).",
# )
@cache
def get_task_by_name(entity, task_type, name="main", client=default):
    return get_task_by_entity(entity, task_type, name=name, client=client)


@cache
def get_task_type(task_type_id, client=default):
    """
    Args:
        task_type_id (str): ID of claimed task type.

    Returns:
        dict: Task type matching given ID.
    """
    return raw.fetch_one("task-types", task_type_id, client=client)


@cache
def get_task_type_by_name(
    task_type_name, for_entity=None, department=None, client=default
):
    """
    Args:
        task_type_name (str): Name of claimed task type.
        for_entity (str): The entity type for which the task type is created.
        department (str): The department for which the task type is created.

    Returns:
        dict: Task type object for given name.
    """
    params = {"name": task_type_name}
    if for_entity is not None:
        params["for_entity"] = for_entity
    if department is not None:
        params["department_id"] = normalize_model_parameter(department)["id"]
    return raw.fetch_first("task-types", params, client=client)


@cache
def get_task_by_path(project, file_path, entity_type="shot", client=default):
    """
    Args:
        project (str / dict): The project dict or the project ID.
        file_path (str): The file path to find a related task.
        entity_type (str): asset, shot or scene.

    Returns:
        dict: A task from given file path. This function requires context:
        the project related to the given path and the related entity type.
    """
    project = normalize_model_parameter(project)
    data = {
        "file_path": file_path,
        "project_id": project["id"],
        "type": entity_type,
    }
    return raw.post("data/tasks/from-path/", data, client=client)


@cache
def get_default_task_status(client=default):
    """
    Returns:
        dict: The unique task status flagged with `is_default`.
    """
    return raw.fetch_first(
        "task-status", params={"is_default": True}, client=client
    )


@cache
def get_task_status(task_status_id, client=default):
    """
    Args:
        task_status_id (str): ID of claimed task status.

    Returns:
        dict: Task status matching given ID.
    """
    return raw.fetch_one("task-status", task_status_id, client=client)


@cache
def get_task_status_by_name(name, client=default):
    """
    Args:
        name (str / dict): The name of claimed task status.

    Returns:
        dict: Task status matching given name.
    """
    return raw.fetch_first("task-status", {"name": name}, client=client)


@cache
def get_task_status_by_short_name(task_status_short_name, client=default):
    """
    Args:
        short_name (str / dict): The short name of claimed task status.

    Returns:
        dict: Task status matching given short name.
    """
    return raw.fetch_first(
        "task-status", {"short_name": task_status_short_name}, client=client
    )


def remove_task_type(task_type, client=default):
    """
    Remove given task type from database.

    Args:
        task_type (str / dict): The task type dict or ID.
    """
    task_type = normalize_model_parameter(task_type)
    return raw.delete(
        "data/task-types/%s" % task_type["id"],
        {"force": True},
        client=client,
    )


def remove_task_status(task_status, client=default):
    """
    Remove given task status from database.

    Args:
        task_status (str / dict): The task status dict or ID.
    """
    task_status = normalize_model_parameter(task_status)
    return raw.delete(
        "data/task-status/%s" % task_status["id"],
        {"force": True},
        client=client,
    )


def update_task_type(task_type, client=default):
    """
    Update given task type into the API.

    Args:
        task_type (dict): The task type dict to update.

    Returns:
        dict: Updated task type.
    """
    return raw.put(
        "data/task-types/%s" % task_type["id"],
        task_type,
        client=client,
    )


def update_task_status(task_status, client=default):
    """
    Update given task status into the API.

    Args:
        task_status (dict): The task status dict to update.

    Returns:
        dict: Updated task status.
    """
    return raw.put(
        "data/task-status/%s" % task_status["id"],
        task_status,
        client=client,
    )


@cache
def get_task(task_id, client=default):
    """
    Args:
        task_id (str): ID of claimed task.

    Returns:
        dict: Task matching given ID.
    """
    task_id = normalize_model_parameter(task_id)
    return raw.get("data/tasks/%s/full" % task_id["id"], client=client)


def new_task(
    entity,
    task_type,
    name="main",
    task_status=None,
    assigner=None,
    assignees=[],
    client=default,
):
    """
    Create a new task for given entity and task type.

    Args:
        entity (dict): Entity for which task is created.
        task_type (dict): Task type of created task.
        name (str): Name of the task (default is "main").
        task_status (dict): The task status to set (default status is Todo).
        assigner (dict): Person who assigns the task.
        assignees (list): List of people assigned to the task.

    Returns:
        Created task.
    """
    entity = normalize_model_parameter(entity)
    task_type = normalize_model_parameter(task_type)
    if task_status is None:
        task_status = get_default_task_status(client=client)

    data = {
        "project_id": entity["project_id"],
        "entity_id": entity["id"],
        "task_type_id": task_type["id"],
        "task_status_id": task_status["id"],
        "assignees": normalize_list_of_models_for_links(assignees),
        "name": name,
    }

    if assigner is not None:
        data["assigner_id"] = normalize_model_parameter(assigner)["id"]

    task = get_task_by_name(entity, task_type, name, client=client)
    if task is None:
        task = raw.post("data/tasks", data, client=client)
    return task


def remove_task(task, client=default):
    """
    Remove given task from database.

    Args:
        task (str / dict): The task dict or the task ID.
    """
    task = normalize_model_parameter(task)
    raw.delete("data/tasks/%s" % task["id"], {"force": True}, client=client)


def start_task(task, started_task_status=None, client=default):
    """
    Create a comment to change task status to started_task_status
    (by default WIP) and set its real start date to now.

    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        dict: Created comment.
    """
    if started_task_status is None:
        started_task_status = get_task_status_by_short_name(
            "wip", client=client
        )
        if started_task_status is None:
            raise TaskStatusNotFoundException(
                (
                    "started_task_status is None : 'wip' task status is "
                    "non-existent. You have to create it or to set an other "
                    "task status for started_task_status in the parameters "
                    "of the function."
                )
            )

    return add_comment(task, started_task_status, client=client)


def task_to_review(
    task, person, comment, revision=1, change_status=True, client=default
):
    """
    Deprecated.
    Mark given task as pending, waiting for approval. Author is given through
    the person argument.

    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person dict or the person ID.
        comment (str): Comment text
        revision (int): Force revision of related preview file
        change_status (bool): If set to false, the task status is not changed.

    Returns:
        dict: Modified task
    """
    task = normalize_model_parameter(task)
    person = normalize_model_parameter(person)
    path = "actions/tasks/%s/to-review" % task["id"]
    data = {
        "person_id": person["id"],
        "comment": comment,
        "revision": revision,
        "change_status": change_status,
    }

    return raw.put(path, data, client=client)


@cache
def get_time_spent(task, date=None, client=default):
    """
    Get the time spent by CG artists on a task at a given date if given. A field contains
    the total time spent.  Durations are given in seconds. Date format is
    YYYY-MM-DD.

    Args:
        task (str / dict): The task dict or the task ID.
        date (str): The date for which time spent is required.

    Returns:
        dict: A dict with person ID as key and time spent object as value.
    """
    task = normalize_model_parameter(task)
    path = "actions/tasks/%s/time-spents" % (task["id"])
    if date is not None:
        path += "/%s" % (date)
    return raw.get(path, client=client)


def set_time_spent(task, person, date, duration, client=default):
    """
    Set the time spent by a CG artist on a given task at a given date. Durations
    must be set in seconds. Date format is YYYY-MM-DD.

    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person who spent the time on given task.
        date (str): The date for which time spent must be set.
        duration (int): The duration of the time spent on given task.

    Returns:
        dict: Created time spent entry.
    """
    task = normalize_model_parameter(task)
    person = normalize_model_parameter(person)
    path = "actions/tasks/%s/time-spents/%s/persons/%s" % (
        task["id"],
        date,
        person["id"],
    )
    return raw.post(path, {"duration": duration}, client=client)


def add_time_spent(task, person, date, duration, client=default):
    """
    Add given duration to the already logged duration for given task and person
    at a given date. Durations must be set in seconds. Date format is
    YYYY-MM-DD.

    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person who spent the time on given task.
        date (str): The date for which time spent must be added.
        duration (int): The duration to add on the time spent on given task.

    Returns:
        dict: Updated time spent entry.
    """
    task = normalize_model_parameter(task)
    person = normalize_model_parameter(person)
    path = "actions/tasks/%s/time-spents/%s/persons/%s/add" % (
        task["id"],
        date,
        person["id"],
    )
    return raw.post(path, {"duration": duration}, client=client)


def add_comment(
    task,
    task_status,
    comment="",
    person=None,
    checklist=[],
    attachments=[],
    created_at=None,
    links=[],
    client=default,
):
    """
    Add comment to given task. Each comment requires a task_status. Since the
    addition of comment triggers a task status change. Comment text can be
    empty.

    Args:
        task (str / dict): The task dict or the task ID.
        task_status (str / dict): The task status dict or ID.
        comment (str): Comment text
        person (str / dict): Comment author
        checklist (list): Comment checklist
        attachments (list[file_path]): Attachments file paths
        created_at (str): Comment date
        links (list): List of links to add to the comment

    Returns:
        dict: Created comment.
    """
    task = normalize_model_parameter(task)
    task_status = normalize_model_parameter(task_status)
    data = {
        "task_status_id": task_status["id"],
        "comment": comment,
        "checklist": checklist,
        "links": links,
    }

    if person is not None:
        person = normalize_model_parameter(person)
        data["person_id"] = person["id"]

    if created_at is not None:
        data["created_at"] = created_at

    if len(attachments) == 0:
        return raw.post(
            "actions/tasks/%s/comment" % task["id"], data, client=client
        )
    else:
        attachment = attachments.pop()
        data["checklist"] = json.dumps(checklist)
        return raw.upload(
            "actions/tasks/%s/comment" % task["id"],
            attachment,
            data=data,
            extra_files=attachments,
            client=client,
        )


def add_attachment_files_to_comment(
    task, comment, attachments=[], client=default
):
    """
    Add attachments files to a given comment.

    Args:
        task (dict / ID): The task dict or the task ID.
        comment (dict / ID): The comment dict or the comment ID.
        attachments (list / str) : A list of path for attachments or directly the path.

    Returns:
        dict: Added attachment files.
    """
    if isinstance(attachments, str):
        attachments = [attachments]
    if len(attachments) == 0:
        raise ValueError("The attachments list is empty")
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    attachment = attachments.pop()
    return raw.upload(
        "actions/tasks/%s/comments/%s/add-attachment"
        % (task["id"], comment["id"]),
        attachment,
        extra_files=attachments,
        client=client,
    )


def get_comment(comment_id, client=default):
    """
    Get comment instance

    Args:
        comment_id (ID): The comment ID.

    Returns:
        dict: Given comment instance.
    """
    return raw.fetch_one("comments", comment_id, client=client)


def remove_comment(comment, client=default):
    """
    Remove given comment and related (previews, news, notifications) from
    database.

    Args:
        comment (str / dict): The comment dict or the comment ID.
    """
    comment = normalize_model_parameter(comment)
    return raw.delete("data/comments/%s" % (comment["id"]), client=client)


def create_preview(task, comment, revision=None, client=default):
    """
    Create a preview into given comment.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment or the comment ID.
        revision (int): Revision number.

    Returns:
        dict: Created preview file model.
    """
    task = normalize_model_parameter(task)
    comment = normalize_model_parameter(comment)
    path = "actions/tasks/%s/comments/%s/add-preview" % (
        task["id"],
        comment["id"],
    )
    data = {}
    if revision is not None:
        data["revision"] = revision
    return raw.post(path, data, client=client)


def upload_preview_file(
    preview_file, file_path, normalize_movie=True, client=default
):
    """
    Create a preview into given comment.

    Args:
        preview_file (str / dict): The preview_file dict or the preview_file ID.
        file_path (str): Path of the file to upload as preview.
    """
    path = (
        "pictures/preview-files/%s"
        % normalize_model_parameter(preview_file)["id"]
    )
    if not normalize_movie:
        path += "?normalize=false"
    return raw.upload(path, file_path, client=client)


def add_preview(
    task,
    comment,
    preview_file_path=None,
    preview_file_url=None,
    normalize_movie=True,
    revision=None,
    client=default,
):
    """
    Add a preview to given comment.

    Args:
        task (str / dict): The task dict or the task ID.
        comment (str / dict): The comment or the comment ID.
        preview_file_path (str): Path of the file to upload as preview.
        preview_file_url (str): Url to download the preview file if no path is
        given.
        normalize_movie (bool): Normalize the movie or not.
        revision (int): Revision number.
    Returns:
        dict: Created preview file model.
    """
    if preview_file_url is not None:
        preview_file_path = download_file(
            preview_file_url,
        )

    preview_file = create_preview(
        task, comment, revision=revision, client=client
    )
    return upload_preview_file(
        preview_file,
        preview_file_path,
        normalize_movie=normalize_movie,
        client=client,
    )


def publish_preview(
    task,
    task_status,
    comment="",
    person=None,
    checklist=[],
    attachments=[],
    created_at=None,
    preview_file_path=None,
    preview_file_url=None,
    normalize_movie=True,
    revision=None,
    set_thumbnail=False,
    links=[],
    client=default,
):
    """
    Publish a comment and include given preview for given task and set given
    task status.

    Args:
        task (str / dict): The task dict or the task ID.
        task_status (str / dict): The task status dict or ID.
        comment (str): Comment text
        person (str / dict): Comment author
        checklist (list): Comment checklist
        attachments (list[file_path]): Attachments file paths
        created_at (str): Comment date
        preview_file_path (str): Path of the file to upload as preview.
        preview_file_url (str): Url to download the preview file if no path is
        given.
        normalize_movie (bool): Set to false to not do operations on it on the
        server side.
        revision (int): Revision number.
        set_thumbnail (bool): Set the preview as thumbnail of the entity.
        links (list): List of links to add to the comment
    Returns:
        tuple(dict, dict): Created comment model and created preview file
        model.
    """
    new_comment = add_comment(
        task,
        task_status,
        comment=comment,
        person=person,
        checklist=checklist,
        attachments=attachments,
        created_at=created_at,
        links=links,
        client=client,
    )
    preview_file = add_preview(
        task,
        new_comment,
        preview_file_path=preview_file_path,
        preview_file_url=preview_file_url,
        normalize_movie=normalize_movie,
        revision=revision,
        client=client,
    )
    if set_thumbnail:
        set_main_preview(preview_file, client=client)
    return new_comment, preview_file


def publish_comments_previews(task, comments=[], client=default):
    """
    Publish a list of comments (with attachments and previews) for given task.
    Each dict comments may contain a list of attachment files path and preview
    files path in the keys "attachment_files" and "preview_files".

    Args:
        task (str / dict): The task dict or the task ID.
        comments (list): List of comments to publish.

    Returns:
        list: List of created comments.
    """
    task = normalize_model_parameter(task)

    files = {}
    for x, comment in enumerate(comments):
        if comment.get("attachment_files"):
            for y, file_path in enumerate(comment["attachment_files"]):
                files["attachment_file-%i-%i" % (x, y)] = open(file_path, "rb")
        if comment.get("preview_files"):
            for y, file_path in enumerate(comment["preview_files"]):
                files["preview_file-%i-%i" % (x, y)] = open(file_path, "rb")

    files["comments"] = (None, json.dumps(comments), "application/json")
    return raw.upload(
        "actions/tasks/%s/add-comments-previews" % task["id"],
        file_path=None,
        files=files,
        client=client,
    )


def set_main_preview(preview_file, frame_number=None, client=default):
    """
    Set given preview as thumbnail of given entity.

    Args:
        preview_file (str / dict): The preview file dict or ID.
        frame_number (int): Frame of preview video to set as main preview

    Returns:
        dict: Created preview file model.
    """
    data = {}
    if frame_number is not None:
        data["frame_number"] = frame_number
    preview_file = normalize_model_parameter(preview_file)
    path = "actions/preview-files/%s/set-main-preview" % preview_file["id"]
    return raw.put(path, data, client=client)


@cache
def all_comments_for_task(task, client=default):
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        Comments linked to the given task.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_all("tasks/%s/comments" % task["id"], client=client)


@cache
def get_last_comment_for_task(task, client=default):
    """
    Args:
        task (str / dict): The task dict or the task ID.

    Returns:
        Last comment posted for given task.
    """
    task = normalize_model_parameter(task)
    return raw.fetch_first("tasks/%s/comments" % task["id"], client=client)


@cache
def assign_task(task, person, client=default):
    """
    Assign one Person to a Task.
    Args:
        task (str / dict): The task dict or the task ID.
        person (str / dict): The person dict or the person ID.

    Returns:
        (dict) the affected Task
    """
    person = normalize_model_parameter(person)
    task = normalize_model_parameter(task)
    path = "/actions/persons/%s/assign" % person["id"]
    return raw.put(path, {"task_ids": task["id"]}, client=client)


def clear_assignations(tasks, person=None, client=default):
    """
    Clear assignations for a single or multiple tasks.
    If no person is given, all assignations are cleared.
    Args:
        tasks (list / str / dict): Task dict or the task ID, single or list.
        person (str / dict): The person dict or the person ID.

    Returns:
        (dict) List of affected Task IDs
    """
    if not isinstance(tasks, list):
        tasks = [tasks]
    data = {}
    for task in tasks:
        task = normalize_model_parameter(task)
        data.setdefault("task_ids", []).append(task["id"])
    if person is not None:
        person = normalize_model_parameter(person)
        data["person_id"] = person["id"]
    return raw.put(
        "/actions/tasks/clear-assignation", data=data, client=client
    )


def new_task_type(name, color="#000000", for_entity="Asset", client=default):
    """
    Create a new task type with the given name.

    Args:
        name (str): The name of the task type
        color (str): The color of the task type as an hexadecimal string
        with # as first character. ex : #00FF00
        for_entity (str): The entity type for which the task type is created.

    Returns:
        dict: The created task type
    """
    task_type = get_task_type_by_name(name, for_entity)
    if task_type is None:
        data = {"name": name, "color": color, "for_entity": for_entity}
        task_type = raw.post("data/task-types", data, client=client)
    return task_type


def new_task_status(name, short_name, color, client=default):
    """
    Create a new task status with the given name, short name and color.

    Args:
        name (str): The name of the task status
        short_name (str): The short name of the task status
        color (str): The color of the task status as an hexadecimal string
        with # as first character. ex : #00FF00

    Returns:
        dict: The created task status
    """
    assert color[0] == "#"
    assert all(c in string.hexdigits for c in color[1:])

    data = {"name": name, "short_name": short_name, "color": color}
    return raw.post("data/task-status", data, client=client)


def update_task(task, client=default):
    """
    Update given task into the API. Metadata are fully replaced by the ones
    set on given task.

    Args:
        task (dict): The task dict to update.

    Returns:
        dict: Updated task.
    """
    if "assignees" in task:
        task["assignees"] = normalize_list_of_models_for_links(
            task["assignees"]
        )
    return raw.put("data/tasks/%s" % task["id"], task, client=client)


def update_task_data(task, data={}, client=default):
    """
    Update the metadata for the provided task. Keys that are not provided are
    not changed.

    Args:
        task (dict / ID): The task dict or ID to save in database.
        data (dict): Free field to set metadata of any kind.

    Returns:
        dict: Updated task.
    """
    task = normalize_model_parameter(task)
    current_task = get_task(task["id"], client=client)

    updated_task = {"id": current_task["id"], "data": current_task["data"]}
    if updated_task["data"] is None:
        updated_task["data"] = {}
    updated_task["data"].update(data)
    return update_task(updated_task, client=client)


@cache
def get_task_url(task, client=default):
    """
    Args:
        task (dict): The task dict.

    Returns:
        url (str): Web url associated to the given task
    """
    if not isinstance(task, dict):
        raise TaskMustBeADictException
    path = "{host}/productions/{project_id}/shots/tasks/{task_id}/"
    return path.format(
        host=raw.get_api_url_from_host(client=client),
        project_id=task["project_id"],
        task_id=task["id"],
    )


def all_tasks_for_project(
    project, task_type=None, episode=None, client=default
):
    """
    Args:
        project (str / dict): The project (or its ID) to get tasks from.
        task_type (str / dict): The task type (or its ID) to filter tasks.
        episode (str / dict): The episode (or its ID) to filter tasks.

    Returns:
        dict: Tasks related to given project.
    """
    project = normalize_model_parameter(project)
    path = "/data/projects/%s/tasks" % project["id"]
    params = {}
    if task_type is not None:
        task_type = normalize_model_parameter(task_type)
        params["task_type_id"] = task_type["id"]
    if episode is not None:
        episode = normalize_model_parameter(episode)
        params["episode_id"] = episode["id"]
    return raw.get(path, params=params, client=client)


def update_comment(comment, client=default):
    """
    Save given comment data into the API. Metadata are fully replaced by the ones
    set on given comment.

    Args:
        comment (dict): The comment dict to update.

    Returns:
        dict: Updated comment.
    """
    return raw.put("data/comments/%s" % comment["id"], comment, client=client)
