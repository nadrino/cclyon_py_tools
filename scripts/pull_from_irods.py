#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cclyon_toolbox_lib as toolbox
import sys
import os
import subprocess

parameters_dict = dict()

is_dry_run = False
this_script_file_name = os.path.basename(__file__)
current_working_directory = os.getcwd()
now_time_string = toolbox.get_now_time_string()

parameters_dict["pull_folders"] = list()


if os.getenv("JOBS_DIR") is None:
    print(toolbox.error + "$JOBS_DIR is not set.")
    sys.exit(1)

if len(sys.argv) == 1:
    print(toolbox.warning + "--dry-run : Make all the process but don't start the run.")
    print(toolbox.warning + "Example of usage : pull_from_irods.py /QMULZone1/home/asg/asg2019oa/xseccovs")
    sys.exit(0)

print(toolbox.red_color +
      "************** " + this_script_file_name + " starts **************" +
      toolbox.reset_color)

for arg_id in range(len(sys.argv)):

    if sys.argv[arg_id] == "--dry-run":
        is_dry_run = True
        print(toolbox.warning + "Dry run enabled.")
    else:
        if arg_id >= 1:
            parameters_dict["pull_folders"].append(sys.argv[arg_id])


for pull_folder in parameters_dict["pull_folders"]:

    printout = subprocess.run(['icd', pull_folder], stdout=subprocess.PIPE)
    if "No such directory" in printout.stdout.decode('utf-8'):
        print( toolbox.alert + "Directory \""+pull_folder+"\" has not been found." )
        continue

    if pull_folder[-1] == '/':
        pull_folder = pull_folder[:-1]
    head_folder = pull_folder.split('/')[-1]
    toolbox.mkdir(head_folder)
    os.chdir(current_working_directory + "/" + head_folder)

    def recursive_download(download_path_):

        printout = subprocess.run(['icd', pull_folder], stdout=subprocess.PIPE)
        if "No such directory" in printout.stdout.decode('utf-8'):
            return

        toolbox.mkdir("")

        printout = subprocess.run(['ils'], stdout=subprocess.PIPE)
        ls_list = printout.stdout.decode('utf-8').split('\n')[1:]

        for element in ls_list:
            if "C-" in element:
                current_dir = os.getcwd()
                recurse_head_folder = pull_folder.split('/')[-1]
                print(toolbox.info + "Entering " + download_path_)
                toolbox.mkdir(recurse_head_folder)
                os.chdir(current_working_directory + "/" + recurse_head_folder)
                recursive_download(element)
                os.chdir(current_dir)
            else:
                print(toolbox.info + "Downloading " + download_path_)
                subprocess.run(['iget', download_path_, "./"], stdout=subprocess.PIPE)

        return

    recursive_download(head_folder)


print(toolbox.red_color +
      "************** " + this_script_file_name + " ended **************" +
      toolbox.reset_color)
