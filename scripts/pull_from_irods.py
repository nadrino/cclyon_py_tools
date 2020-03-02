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
        print(toolbox.alert + "Directory \""+pull_folder+"\" has not been found.")
        continue

    printout = subprocess.run(['ils'], stdout=subprocess.PIPE)
    print(printout.stdout.decode('utf-8').split('\n'))



print(toolbox.red_color +
      "************** " + this_script_file_name + " ended **************" +
      toolbox.reset_color)
