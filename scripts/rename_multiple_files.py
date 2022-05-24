#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GenericToolbox.Colors as tColors
import GenericToolbox.IO as tIO

import sys
import os

parameters = dict()

if len(sys.argv) < 3:
    print(tColors.info + " *** Usage : *** ")
    print(tColors.info + "rename_multiple_files <substring_to_search> <replacing_string>")
    exit(0)

for arg_id in range(len(sys.argv)):

    if arg_id == 1:
        parameters["substring_to_search"] = sys.argv[arg_id]

    if arg_id == 2:
        parameters["replacing_string"] = sys.argv[arg_id]


files_list = tIO.get_list_of_files_in_folder("./")

for file_name in files_list:

    command_line = "mv "
    new_file_name = file_name.replace(parameters["substring_to_search"], parameters["replacing_string"])
    command_line += file_name + " " + new_file_name
    os.system(command_line)
