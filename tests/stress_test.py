"""Stress tests for Tik Manager 4"""

import os
import shutil
import requests
import random
from pprint import pprint
import pytest
# import uuid
from .mockup import Mockup, clean_user
from tik_manager4.objects import user
from tik_manager4.core import filelog, utils

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

response = requests.get(word_site)
WORDS = response.content.splitlines()

class TestStress:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    mock = Mockup()
    mock.prepare()
    user.User(common_directory=mock.common)  # this is for not popping up the "missing common folder" message
    import tik_manager4 # importing main checks the common folder definition, thats why its here
    tik = tik_manager4.initialize("Standalone")
    def test_create_a_big_project(self, clean_user):
        test_stress_project_path = os.path.join(utils.get_home_dir(), "t4_stress_test_DO_NOT_USE")
        if os.path.exists(test_stress_project_path):
            shutil.rmtree(test_stress_project_path)

        self.tik.user.set("Admin", "1234")

        # create project with lots of assets, shots, tasks, works, publishes and metadata
        self.tik.create_project(test_stress_project_path,
                                structure_template="asset_sequence",
                                resolution=[3840, 2160],
                                fps=24,
                                colorspace="linear",
                                pixel_aspect_ratio=1.0,
                                pre_roll=30,
                                post_roll=2,
                                sub_steps=1
                                )


        # ASSETS
        iteration = 10
        parent_paths = ["Assets/Characters", "Assets/Props", "Assets/Environment", "Assets/Vehicles"]
        for sub_asset in parent_paths:
            random_int_list = [random.randint(0, 9999) for x in range(iteration)]
            for x in random_int_list:
                word = WORDS[x].decode("utf-8")
                sub = self.tik.project.create_sub_project(word, parent_path=sub_asset)
                # create 5 task for each sub
                if sub == -1:
                    continue
                for x in range(1, 6):
                    task = self.tik.project.create_task("{0}_Task_{1}".format(word, x), categories=["Model", "Rig", "LookDev"], parent_path=sub.path)
                    # for each category, create 10 works
                    for _, category in task.categories.items():
                        for y in range(1, 6):
                            work = category.create_work("{0}_{1}_Work_{2}".format(task.name, category.name, y))
                            # for each work, create 10 publishes


        # SEQUENCES AND SHOTS
        for x in range (1, 5):
            seq = self.tik.project.create_sub_project("Sequence_{}".format(x), parent_path="Sequences")
            for y in range (1, iteration):
                shot = self.tik.project.create_sub_project("Shot_{}".format(y), parent_path=seq.path)



        # # create 100 Character, 100 Props, 100 Environment and 100 Vehicle sub-projects
        # random_int_list_a = [random.randint(0, 9999) for x in range(100)]
        # random_int_list_b = [random.randint(0, 9999) for x in range(100)]
        # random_int_list_c = [random.randint(0, 9999) for x in range(100)]
        # random_int_list_d = [random.randint(0, 9999) for x in range(100)]
        # for x in random_int_list_a:
        #     word = WORDS[x].decode("utf-8") # convert bytes to string
        #     self.tik.project.create_sub_project(word, parent_path="Assets/Characters")
        # for x in random_int_list_b:
        #     word = WORDS[x].decode("utf-8")
        #     self.tik.project.create_sub_project(word, parent_path="Assets/Props")
        # for x in random_int_list_c:
        #     word = WORDS[x].decode("utf-8")
        #     self.tik.project.create_sub_project(word, parent_path="Assets/Environment")
        # for x in random_int_list_d:
        #     word = WORDS[x].decode("utf-8")
        #     self.tik.project.create_sub_project(word, parent_path="Assets/Vehicles")

        # set the project
        self.tik.set_project(test_stress_project_path)
