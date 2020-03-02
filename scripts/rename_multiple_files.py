#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cclyon_toolbox_lib as toolbox_lib
import sys
import os

parameters = dict()

if len(sys.argv) < 3:
    print(toolbox_lib.info + " *** Usage : *** ")
    print(toolbox_lib.info + "rename_multiple_files <substring_to_search> <replacing_string>")
    exit(0)

for arg_id in range(len(sys.argv)):

    if arg_id == 1:
        parameters["substring_to_search"] = sys.argv[arg_id]

    if arg_id == 2:
        parameters["replacing_string"] = sys.argv[arg_id]


files_list = toolbox_lib.get_list_of_files_in_folder("./")

for file_name in files_list:

    command_line = "mv "
    new_file_name = file_name.replace(parameters["substring_to_search"], parameters["replacing_string"])
    command_line += file_name + " " + new_file_name
    os.system(command_line)
