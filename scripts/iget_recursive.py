#!/usr/bin/env python
# -*- coding: utf-8 -*-

import GenericToolbox.Colors as tColors
import GenericToolbox.IO as tIO

import sys
import os
import subprocess

# Recursion tools
import inspect
# sys.setrecursionlimit(1500)

parameters_dict = dict()

is_dry_run = False
this_script_file_name = os.path.basename(__file__)
original_working_directory = os.getcwd()
now_time_string = tIO.getNowTimeString()

do_overwrite = False
is_verbose_mode = False
parameters_dict["pull_folders"] = list()


if len(sys.argv) == 1:
    print(tColors.warning + "--dry-run : Make all the process but don't start the run.")
    print(tColors.warning + "-f : Enables overwriting.")
    print(tColors.warning + "-v : Verbose mode.")
    print(tColors.warning + "Example of usage : iget_recursive.py /QMULZone1/home/asg/asg2019oa/xseccovs")
    sys.exit(0)

print(tColors.redColor +
      "************** " + this_script_file_name + " starts **************" +
      tColors.resetColor)

for arg_id in range(len(sys.argv)):

    if sys.argv[arg_id] == "--dry-run":
        is_dry_run = True
        print(tColors.warning + "Dry run enabled.")
    elif sys.argv[arg_id] == "-f":
        do_overwrite = True
        print(tColors.warning + "Overwrite mode enabled.")
    elif sys.argv[arg_id] == "-v":
        is_verbose_mode = True
        print(tColors.warning + "Verbose mode enabled.")
    else:
        if arg_id >= 1:
            parameters_dict["pull_folders"].append(sys.argv[arg_id])


for pull_folder in parameters_dict["pull_folders"]:

    printout = subprocess.run(['icd', pull_folder], stdout=subprocess.PIPE)
    if "No such directory" in printout.stdout.decode('utf-8'):
        print( tColors.alert + "Directory \""+pull_folder+"\" has not been found." )
        continue

    if pull_folder[-1] == '/':
        pull_folder = pull_folder[:-1]
    head_folder = pull_folder.split('/')[-1]
    tIO.mkdir(head_folder)
    os.chdir(original_working_directory + "/" + head_folder)

    def recursive_download(download_folder_):

        # print(tColors.alert + "Recursion depth : " + str(len(inspect.stack())))
        recursive_spaces = " "*(2*(len(inspect.stack())-1))

        printout = subprocess.run(['icd', download_folder_], stdout=subprocess.PIPE)
        if "No such directory" in printout.stdout.decode('utf-8'):
            return

        print(tColors.warning + "./" + os.getcwd()[len(original_working_directory)+1:] + "/")

        printout = subprocess.run(['ils'], stdout=subprocess.PIPE)
        ls_list = printout.stdout.decode('utf-8').split('\n')[1:]
        element_list = list()
        for element in ls_list:
            element = element[2:]
            if element == "":
                continue
            element_list.append(element)
            print(tColors.warning + recursive_spaces + "├─ " + element)

        for element in element_list:

            if "C-" in element:
                current_dir = os.getcwd()
                recurse_head_folder = element.split('/')[-1]

                # Preparing new folder
                tIO.mkdir(recurse_head_folder)
                os.chdir(current_dir + "/" + recurse_head_folder)
                recursive_download(download_folder_ + "/" + recurse_head_folder)

                # Back to the original folder
                os.chdir(current_dir)
                subprocess.run(['icd', download_folder_], stdout=subprocess.PIPE)
            else:
                print(tColors.info + "Downloading " + element)
                if os.path.exists(element):
                    if not do_overwrite:
                        if is_verbose_mode:
                            print(tColors.warning + element + " already exists (it may have already been downloaded).")
                            print(tColors.warning + "Add '-f' option to allow overwrite.")
                        continue
                    else:
                        if is_verbose_mode:
                            print("rm " + element)
                        os.system("rm " + element)
                command_line = ['iget', element, "./"]
                if is_verbose_mode:
                    command_line.append("-vP")
                    print(" ".join(['iget', element, "./"]))
                subprocess.run(command_line)


    recursive_download(pull_folder)


print(tColors.redColor +
      "************** " + this_script_file_name + " ended **************" +
      tColors.resetColor)
