# import pytest
from pprint import pprint

import os
from tik_manager4.objects import project

# class PropertyTest(object):
pr = project.Project()

def test_initialize():
    assert pr

def test_project_path():
    test_project = os.path.join(os.path.expanduser("~"), "test_project")
    pr.path = test_project
    assert pr.path == test_project

def test_project_name():
    pr.name = "test_project"
    assert pr.name == "test_project"

def test_create_a_shot_asset_project_structure():
    asset_categories = ["Model", "LookDev", "Rig"]
    shot_categories = ["Layout", "Animation", "Lighting", "Render"]

    assets = pr.add_sub_project("Assets")
    chars = assets.add_sub_project("Characters")
    props = assets.add_sub_project("Props")
    env = assets.add_sub_project("Environment")

    leaf_assets = []
    leaf_assets.append(chars.add_sub_project("Soldier"))
    leaf_assets.append(props.add_sub_project("Rifle"))
    leaf_assets.append(props.add_sub_project("Knife"))
    leaf_assets.append(env.add_sub_project("Tree"))
    leaf_assets.append(env.add_sub_project("Ground"))

    # for leaf in leaf_assets:
    #     for category in asset_categories:
    #         leaf.add_category(category)

    shots = pr.add_sub_project("Shots")
    sequence_a = shots.add_sub_project("SequenceA")
    leaf_shots = []
    leaf_shots.append(sequence_a.add_sub_project("SHOT_010"))
    leaf_shots.append(sequence_a.add_sub_project("SHOT_020"))
    leaf_shots.append(sequence_a.add_sub_project("SHOT_030"))
    leaf_shots.append(sequence_a.add_sub_project("SHOT_040"))

    sequence_b = shots.add_sub_project("SequenceB")
    leaf_shots.append(sequence_b.add_sub_project("SHOT_010"))
    leaf_shots.append(sequence_b.add_sub_project("SHOT_070"))
    leaf_shots.append(sequence_b.add_sub_project("SHOT_120"))

    for leaf in leaf_shots:
        for category in shot_categories:
            leaf.add_category(category)

    # print("\n")
    # print("Project:", pr.name)
    # print("Assets:")
    # pprint(pr.subs)
    print("\n")
    # assert pr.subs["Assets"].subs["Characters"].subs["Soldier"].name == "Soldier"
    # pprint(list(pr.get_sub_project_names(recursive=True)))
    pprint(pr.get_sub_tree())

def test_existing_sub_project():
    pr.add_sub_project("duplicate_test")
    assert pr.add_sub_project("duplicate_test") == 0


#
# def test_subproject():
#     test_sub_project_name = "sample_sub_project"
#     pr.add_sub_project(test_sub_project_name)
#     assert len(pr.sub_projects) == 1
#     assert str(pr.sub_projects[0]) == test_sub_project_name

# def test_second_level_sub_project():
#     second_level_sub_project_name = "second_level_test"
#     pr.sub_projects[0].add_sub_project(second_level_sub_project_name)
#     assert len(pr.sub_projects[0].sub_projects) == 1
#     assert str(pr.sub_projects[0].sub_projects[0]) == second_level_sub_project_name
#     print(pr.sub_projects[0].sub_projects[0]._relative_path)
