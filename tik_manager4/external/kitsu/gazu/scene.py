from . import client as raw

from .sorting import sort_by_name
from .cache import cache
from .helpers import normalize_model_parameter
from .shot import get_sequence

default = raw.default_client


def new_scene(project, sequence, name, client=default):
    """
    Create a scene for given sequence.
    """
    project = normalize_model_parameter(project)
    sequence = normalize_model_parameter(sequence)
    scene = {"name": name, "sequence_id": sequence["id"]}
    return raw.post(
        "data/projects/%s/scenes" % project["id"], scene, client=client
    )


@cache
def all_scenes(project=None, client=default):
    """
    Retrieve all scenes.
    """
    project = normalize_model_parameter(project)
    if project is not None:
        scenes = raw.fetch_all(
            "projects/%s/scenes" % project["id"], client=client
        )
    else:
        scenes = raw.fetch_all("scenes", client=client)
    return sort_by_name(scenes)


@cache
def all_scenes_for_project(project, client=default):
    """
    Retrieve all scenes for given project.
    """
    project = normalize_model_parameter(project)
    scenes = raw.fetch_all("projects/%s/scenes" % project["id"], client=client)
    return sort_by_name(scenes)


@cache
def all_scenes_for_sequence(sequence, client=default):
    """
    Retrieve all scenes which are children from given sequence.
    """
    sequence = normalize_model_parameter(sequence)
    return sort_by_name(
        raw.fetch_all("sequences/%s/scenes" % sequence["id"], client=client),
    )


@cache
def get_scene(scene_id, client=default):
    """
    Return scene corresponding to given scene ID.
    """
    return raw.fetch_one("scenes", scene_id, client=client)


@cache
def get_scene_by_name(sequence, scene_name, client=default):
    """
    Returns scene corresponding to given sequence and name.
    """
    sequence = normalize_model_parameter(sequence)
    result = raw.fetch_all(
        "scenes/all",
        {"parent_id": sequence["id"], "name": scene_name},
        client=client,
    )
    return next(iter(result or []), None)


def update_scene(scene, client=default):
    """
    Save given scene data into the API.
    """
    return raw.put("data/entities/%s" % scene["id"], scene, client=client)


def new_scene_asset_instance(scene, asset, description=None, client=default):
    """
    Creates a new asset instance on given scene. The instance number is
    automatically generated (increment highest number).
    """
    scene = normalize_model_parameter(scene)
    asset = normalize_model_parameter(asset)
    data = {"asset_id": asset["id"]}

    if description is not None:
        data["description"] = description

    return raw.post(
        "data/scenes/%s/asset-instances" % scene["id"], data, client=client
    )


@cache
def all_asset_instances_for_scene(scene, client=default):
    """
    Return the list of asset instances listed in a scene.
    """
    scene = normalize_model_parameter(scene)
    return raw.get(
        "data/scenes/%s/asset-instances" % scene["id"], client=client
    )


@cache
def get_asset_instance_by_name(scene, name, client=default):
    """
    Returns the asset instance of the scene that has the given name.
    """
    return raw.fetch_first(
        "asset-instances",
        {"name": name, "scene_id": scene["id"]},
        client=client,
    )


@cache
def all_camera_instances_for_scene(scene, client=default):
    """
    Return the list of camera instances listed in a scene.
    """
    scene = normalize_model_parameter(scene)
    return raw.get(
        "data/scenes/%s/camera-instances" % scene["id"], client=client
    )


@cache
def all_shots_for_scene(scene, client=default):
    """
    Return the list of shots issued from given scene.
    """
    scene = normalize_model_parameter(scene)
    return raw.get("data/scenes/%s/shots" % scene["id"], client=client)


def add_shot_to_scene(scene, shot, client=default):
    """
    Link a shot to a scene to mark the fact it was generated out from that
    scene.
    """
    scene = normalize_model_parameter(scene)
    shot = normalize_model_parameter(shot)
    data = {"shot_id": shot["id"]}
    return raw.post("data/scenes/%s/shots" % scene["id"], data, client=client)


def remove_shot_from_scene(scene, shot, client=default):
    """
    Remove link between a shot and a scene.
    """
    scene = normalize_model_parameter(scene)
    shot = normalize_model_parameter(shot)
    return raw.delete(
        "data/scenes/%s/shots/%s" % (scene["id"], shot["id"]), client=client
    )


def update_asset_instance_name(asset_instance, name, client=default):
    """
    Update the name of given asset instance.
    """
    path = "/data/asset-instances/%s" % asset_instance["id"]
    return raw.put(path, {"name": name}, client=client)


def update_asset_instance_data(asset_instance, data, client=default):
    """
    Update the extra data of given asset instance.
    """
    asset_instance = normalize_model_parameter(asset_instance)
    path = "/data/asset-instances/%s" % asset_instance["id"]
    return raw.put(path, {"data": data}, client=client)


@cache
def get_sequence_from_scene(scene, client=default):
    """
    Return sequence which is parent of given shot.
    """
    scene = normalize_model_parameter(scene)
    return get_sequence(scene["parent_id"], client=client)
