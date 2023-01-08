import os
import tik_manager4

test_project_path = os.path.join(os.path.expanduser("~"), "t4_test_manual_DO_NOT_USE")
tik = tik_manager4.initialize("Standalone")
tik.user._set("Admin", "1234")
tik.project._set(test_project_path)

# tik.project.delete_sub_project(uid=1226621109)


tik.project.create_sub_project("testSub", parent_path="")

tik.project.delete_sub_project(path="testSub")