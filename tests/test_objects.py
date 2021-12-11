# import pytest
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

def test_subproject():
    test_sub_project_name = "sample_sub_project"
    pr.add_sub_project(test_sub_project_name)
    assert len(pr.sub_projects) == 1
    assert str(pr.sub_projects[0]) == test_sub_project_name

def test_second_level_sub_project():
    second_level_sub_project_name = "second_level_test"
    pr.sub_projects[0].add_sub_project(second_level_sub_project_name)
    assert len(pr.sub_projects[0].sub_projects) == 1
    assert str(pr.sub_projects[0].sub_projects[0]) == second_level_sub_project_name
    print(pr.sub_projects[0].sub_projects[0]._relative_path)
