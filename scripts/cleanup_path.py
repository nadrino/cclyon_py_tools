#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

env_list = list()
env_list.append("PATH")
env_list.append("LD_LIBRARY_PATH")

for env in env_list:

    path = os.getenv(env)
    path_folders = path.split(":")

    cleaned_up_path_folders = list()
    for folder in path_folders:
        if folder[0] != '/':
            continue
        sub_folder_list = folder.split("/")
        cleaned_up_folder_list = list()
        for sub_folder in sub_folder_list:
            if sub_folder != "":
                cleaned_up_folder_list.append(sub_folder)
        new_path_element = "/" + "/".join(cleaned_up_folder_list)
        if new_path_element not in cleaned_up_path_folders:
            cleaned_up_path_folders.append(new_path_element)

    new_path = ":".join(cleaned_up_path_folders)
    # print("export " + env + "=\"" + new_path + "\"")
    # os.system("export " + env + "=\"" + new_path + "\"")
    # subprocess.run(["export", env + "=\"" + new_path + "\""])
    os.environ[env] = new_path


