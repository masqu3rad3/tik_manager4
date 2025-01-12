from . import user as gazu_user
from . import project as gazu_project
from . import asset as gazu_asset
from . import task as gazu_task
from . import shot as gazu_shot
from . import scene as gazu_scene


def all_open_projects(user_context=False):
    """
    Return the list of projects for which the user has a task.
    """
    if user_context:
        return gazu_user.all_open_projects()
    else:
        return gazu_project.all_open_projects()


def all_assets_for_project(project, user_context=False):
    """
    Return the list of assets for which the user has a task.
    """
    if user_context:
        return gazu_user.all_assets_for_project(project)
    else:
        return gazu_asset.all_assets_for_project(project)


def all_asset_types_for_project(project, user_context=False):
    """
    Return the list of asset types for which the user has a task.
    """
    if user_context:
        return gazu_user.all_asset_types_for_project(project)
    else:
        return gazu_asset.all_asset_types_for_project(project)


def all_assets_for_asset_type_and_project(
    project, asset_type, user_context=False
):
    """
    Return the list of assets for given project and asset_type and for which
    the user has a task.
    """
    if user_context:
        return gazu_user.all_assets_for_asset_type_and_project(
            project, asset_type
        )
    else:
        return gazu_asset.all_assets_for_project_and_type(project, asset_type)


def all_task_types_for_asset(asset, user_context=False):
    """
    Return the list of tasks for given asset and current user.
    """
    if user_context:
        return gazu_user.all_task_types_for_asset(asset)
    else:
        return gazu_task.all_task_types_for_asset(asset)


def all_task_types_for_shot(shot, user_context=False):
    """
    Return the list of tasks for given shot and current user.
    """
    if user_context:
        return gazu_user.all_task_types_for_shot(shot)
    else:
        return gazu_task.all_task_types_for_shot(shot)


def all_task_types_for_scene(scene, user_context=False):
    """
    Return the list of tasks for given scene and current user.
    """
    if user_context:
        return gazu_user.all_task_types_for_scene(scene)
    else:
        return gazu_task.all_task_types_for_scene(scene)


def all_task_types_for_sequence(sequence, user_context=False):
    """
    Return the list of tasks for given sequence and current user.
    """
    if user_context:
        return gazu_user.all_task_types_for_sequence(sequence)
    else:
        return gazu_task.all_task_types_for_sequence(sequence)


def all_sequences_for_project(project, user_context=False):
    """
    Return the list of sequences for given project and current user.
    """
    if user_context:
        return gazu_user.all_sequences_for_project(project)
    else:
        return gazu_shot.all_sequences_for_project(project)


def all_scenes_for_project(project, user_context=False):
    """
    Return the list of scenes for given project and current user.
    """
    if user_context:
        return gazu_user.all_scenes_for_project(project)
    else:
        return gazu_scene.all_scenes(project)


def all_shots_for_sequence(sequence, user_context=False):
    """
    Return the list of shots for given sequence and current user.
    """
    if user_context:
        return gazu_user.all_shots_for_sequence(sequence)
    else:
        return gazu_shot.all_shots_for_sequence(sequence)


def all_scenes_for_sequence(sequence, user_context=False):
    """
    Return the list of scenes for given sequence and current user.
    """
    if user_context:
        return gazu_user.all_scenes_for_sequence(sequence)
    else:
        return gazu_scene.all_scenes_for_sequence(sequence)


def all_sequences_for_episode(episode, user_context=False):
    """
    Return the list of shots for given sequence and current user.
    """
    if user_context:
        return gazu_user.all_sequences_for_episode(episode)
    else:
        return gazu_shot.all_sequences_for_episode(episode)


def all_episodes_for_project(project, user_context=False):
    """
    Return the list of shots for given sequence and current user.
    """
    if user_context:
        return gazu_user.all_episodes_for_project(project)
    else:
        return gazu_shot.all_episodes_for_project(project)
