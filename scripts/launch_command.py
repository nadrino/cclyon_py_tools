#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

import cclyon_toolbox_lib as toolbox_lib

# Checking required env variables
toolbox_lib.get_env_variable("WORK_FOLDER")
toolbox_lib.get_env_variable("RESULTS_FOLDER")

parmeters_dict = dict()

parmeters_dict["command"] = ""
parmeters_dict["multithread-support"] = False
parmeters_dict["cpu_time"] = "47:59:59"
debug = False
mode = "job"
command_arg_list = list()


print(toolbox_lib.red_color + "************** Launch command starts **************" + toolbox_lib.reset_color)

for arg_id in range(len(sys.argv)):

    if sys.argv[arg_id] == "-debug":
        debug = True
    elif sys.argv[arg_id] == "-interactive":
        mode = "interactive"
    else:
        if arg_id >= 1: # Skipping "launch_command.py"
            command_arg_list.append(sys.argv[arg_id])
            if sys.argv[arg_id] == "--multithread-support":
                parmeters_dict["multithread-support"] = True



if len(sys.argv) == 1:
    print(toolbox_lib.warning + "-interactive : Launch script in prompt")
    print(toolbox_lib.warning + "-debug : verbose-only mode")
    print(toolbox_lib.warning + "Example of usage : launch_command.py Erec_Tuning -it 13 -z-sampling-mode 5-Positions -MC-SVN r1777")
    sys.exit()


#> Parsing parameters
script_subfolder = "LaunchCommand"
script_names = command_arg_list[0]
parmeters_dict["command"] = " ".join(command_arg_list)
print(toolbox_lib.green_color + "Launching Command : " + toolbox_lib.reset_color + parmeters_dict["command"])

out_filename_item_list = list()
for argument in command_arg_list:
    argument_str = str(argument) # Copy string object
    argument_str = argument_str.replace("@", "X") # Replacing special characters
    if argument_str[0] != '-' or (argument_str[0:2] == "--"):
        if "/" in argument_str:
            argument_str = argument_str.split("/")[-1]
        if "." in argument_str:
            argument_str = argument_str.split(".")[0]
        if len(argument_str) > 20:
            argument_str = ".." + argument_str[-20:-1]
        out_filename_item_list.append(argument_str)

outfiles_base_name = toolbox_lib.get_now_time_string() + "_" + "_".join(out_filename_item_list)
if len(outfiles_base_name) > 200: outfiles_base_name = outfiles_base_name[0:200]
print(toolbox_lib.gold_color + "Outfiles base name : " + toolbox_lib.reset_color + outfiles_base_name)

this_python_script_path = os.path.dirname(os.path.realpath(__file__))
WORK_FOLDER = os.environ.get("WORK_FOLDER")
RESULTS_FOLDER = os.environ.get("WORK_FOLDER")
launch_script_reservoir_path = this_python_script_path + "/LaunchCommand"
execution_folder = RESULTS_FOLDER + "/" + script_names
log_folder = WORK_FOLDER + "/Logs/" + command_arg_list[0] + "/"

toolbox_lib.mkdir(launch_script_reservoir_path)
toolbox_lib.mkdir(execution_folder)
toolbox_lib.mkdir(log_folder)


#> Preparing launch script
lauch_script_string =  "#!/bin/bash\n"
lauch_script_string += "\n"
lauch_script_string += "echo source " + STEREO_OUTPUT + "/Setup/scripts/stereo_setup.sh\n"
lauch_script_string += "source " + STEREO_OUTPUT + "/Setup/scripts/stereo_setup.sh\n"
lauch_script_string += "echo setup_root\n"
lauch_script_string += "setup_root\n"
lauch_script_string += "echo setup_geant\n"
lauch_script_string += "setup_geant\n"
lauch_script_string += "echo setup_stereo\n"
lauch_script_string += "setup_stereo\n"
lauch_script_string += "echo cd " + execution_folder + "\n"
lauch_script_string += "cd " + execution_folder + "\n"
lauch_script_string += "\n"
lauch_script_string += "echo '*******************************************************************'\n"
lauch_script_string += "echo COMPUTATION BEGINS\n"
lauch_script_string += "echo '*******************************************************************'\n"
lauch_script_string += "echo " + parmeters_dict["command"] +"\n"
lauch_script_string += parmeters_dict["command"] +" &> " + log_folder + "/log_" + outfiles_base_name + ".log \n"
lauch_script_string += "echo '*******************************************************************'\n"
lauch_script_string += "echo COMPUTATION FINISHED\n"
lauch_script_string += "echo '*******************************************************************'\n"

launch_file = open(launch_script_reservoir_path + "/Script_" + outfiles_base_name + ".sh", 'w')
launch_file.write(lauch_script_string)  # python will convert \n to os.linesep
launch_file.close()  # you can omit in most cases as the destructor will call it
print(toolbox_lib.green_color + "Launch script writen as : " + toolbox_lib.reset_color + launch_script_reservoir_path + "/Script_" + outfiles_base_name + ".sh")

#> Preparing job script
job_command_arg_list = list()
job_command_arg_list.append("qsub")
job_command_arg_list.append("-l os=" + toolbox_lib.get_current_os())
job_command_arg_list.append("-o " + log_folder + "/log_full_" + outfiles_base_name + ".log")
job_command_arg_list.append("-e " + log_folder + "/log_full_" + outfiles_base_name + ".err")
job_command_arg_list.append("-P P_stereo")
if parmeters_dict["multithread-support"]:
    job_command_arg_list.append("-pe multicores 8 -q mc_long")
job_command_arg_list.append("-l xrootd=1,mysql=1,sps=1,hpss=1,ct=" + parmeters_dict["cpu_time"] + ",vmem=4G,fsize=20G")
job_command_arg_list.append("-j y")
job_command_arg_list.append(launch_script_reservoir_path + "/Script_" + outfiles_base_name + ".sh")



# job_launch_command = "qsub -l os=" + toolbox_lib.get_current_os() + " "
# job_launch_command += "-o " + log_folder + "/log_full_" + outfiles_base_name + ".log "
# job_launch_command += "-e " + log_folder + "/log_full_" + outfiles_base_name + ".err "
# job_launch_command += "-P P_stereo "
# if parmeters_dict["multithread-support"]:
#     job_launch_command += "-pe multicores 8 -q mc_long "
# job_launch_command += "-l xrootd=1,sps=1,hpss=1,ct=" + parmeters_dict["cpu_time"] + ",vmem=4G,fsize=20G -j y "
# job_launch_command += launch_script_reservoir_path + "/Script_" + outfiles_base_name + ".sh"


job_launch_command = " ".join(job_command_arg_list)

print(toolbox_lib.green_color + "Job command : " + toolbox_lib.reset_color + job_launch_command)

#> Launching Job
if not debug:
    if mode == "job":
        print(toolbox_lib.blue_color)
        os.system(job_launch_command)
        print(toolbox_lib.reset_color)
    elif mode == "interactive":
        os.system(parmeters_dict["command"])

# time.sleep(1)
print(toolbox_lib.red_color + "************** Launch command ended. **************" + toolbox_lib.reset_color)