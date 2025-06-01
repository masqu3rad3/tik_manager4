"""Stress tests for Tik Manager 4"""

from pathlib import Path
import shutil
import requests
import random
from tik_manager4.core import filelog, utils
import pytest

log = filelog.Filelog(logname=__name__, filename="tik_manager4")

word_site = "https://www.mit.edu/~ecprice/wordlist.10000"

response = requests.get(word_site)
WORDS = response.content.splitlines()

# @pytest.mark.usefixtures("clean_user")
# @pytest.mark.usefixtures("prepare")
class TestStress:
    """Uses a fresh mockup_common folder and test_project under user directory for all tests"""
    def test_create_a_big_project(self, tik, files):
        test_stress_project_path = Path(utils.get_home_dir(), "t4_stress_test_DO_NOT_USE")
        # test_stress_project_path = os.path.join(utils.get_home_dir(), "t4_stress_test_DO_NOT_USE")
        if test_stress_project_path.exists():
            files.force_remove_directory(test_stress_project_path)

        tik.user.set("Admin", "1234")

        # create project with lots of assets, shots, tasks, works, publishes and metadata
        tik.create_project(str(test_stress_project_path),
                                structure_template="asset_sequence",
                                resolution=[3840, 2160],
                                fps=24,
                                colorspace="linear",
                                pixel_aspect_ratio=1.0,
                                pre_roll=30,
                                post_roll=2,
                                sub_steps=1,
                                locked_commons = False
                                )


        # ASSETS
        total_publishes = 0
        subproject_iteration = 3
        task_iteration = 2
        work_iteration = 2
        publish_iteration = 4
        parent_paths = ["Assets/Characters", "Assets/Props", "Assets/Environment", "Assets/Vehicles"]
        for sub_asset in parent_paths:
            random_int_list = [random.randint(0, 9999) for x in range(subproject_iteration)]
            for x in random_int_list:
                word = WORDS[x].decode("utf-8")
                sub = tik.project.create_sub_project(word, parent_path=sub_asset)
                # create 5 task for each sub
                if sub == -1:
                    continue
                for x in range(1, task_iteration+1):
                    task = tik.project.create_task("{0}_Task_{1}".format(word, x), categories=["Model", "Rig", "LookDev"], parent_path=sub.path)
                    # for each category, create 10 works
                    for _, category in task.categories.items():
                        for y in range(1, work_iteration+1):
                        # y = 1
                            work = category.create_work("{0}_{1}_Work_{2}".format(task.name, category.name, y))
                            # for each work, create 6 publishes
                            for z in range(1, publish_iteration+1):
                                tik.project.snapshot_publisher.work_object = work
                                tik.project.snapshot_publisher.work_version = 1
                                tik.project.snapshot_publisher.resolve()
                                tik.project.snapshot_publisher.reserve()
                                tik.project.snapshot_publisher.extract()
                                tik.project.snapshot_publisher.publish(
                                    notes="Stress Test Publish {0}".format(z),
                                )
                                total_publishes += 1
                            # get all publishes for the work
                            published_versions = work.publish.get_versions() # this one both scans and returns the versions
                            # promote a random version
                            if published_versions:
                                random_version = random.choice(published_versions)
                                random_version.promote()
                            else:
                                log.warning("No published versions found for work: {}".format(work.name))



        # SEQUENCES AND SHOTS
        for x in range (1, 5):
            seq = tik.project.create_sub_project("Sequence_{}".format(x), parent_path="Sequences")
            for y in range (1, subproject_iteration):
                shot = tik.project.create_sub_project("Shot_{}".format(y), parent_path=seq.path)



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
        tik.set_project(str(test_stress_project_path))

        print("\n\nTotal Publishes Created: {}".format(total_publishes))
